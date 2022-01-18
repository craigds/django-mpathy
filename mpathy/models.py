from django.contrib.postgres.indexes import GistIndex
from django.db import models
from django.db.models.expressions import CombinedExpression, RawSQL

from .fields import LTree, LTreeField, Subpath


class BadMove(ValueError):
    pass


class MPathQuerySet(models.QuerySet):
    def get_cached_trees(self):
        """
        Evaluates this queryset and returns a list of top-level nodes.
        """
        nodes_by_path = {}
        min_level = None
        for node in self:
            node._cached_children = []
            nodes_by_path[node.ltree] = node
            level = node.ltree.level()
            if min_level is None or min_level > level:
                min_level = level

        top_level_nodes = []
        for node in self:
            parent_path = node.ltree.parent()
            if parent_path in nodes_by_path:
                nodes_by_path[parent_path]._cached_children.append(node)
            elif node.ltree.level() == min_level:
                top_level_nodes.append(node)

        return top_level_nodes


class MPathManager(models.Manager.from_queryset(MPathQuerySet)):
    def move_subtree(self, node, new_parent):
        """
        Moves a node and all its descendants under the given new parent.
        If the parent is None, the node will become a root node.

        If the `node` is equal to the new parent, or is an ancestor of it,
        raises BadMove.

        If node's parent is already new_parent, returns immediately.

        NOTE:
        This updates all the nodes in the database, and the current node instance.
        It cannot update any other node instances that are in memory, so if you have some
        whose ltree paths are affected by this function you may need to refresh them
        from the database.
        """
        if node.is_ancestor_of(new_parent, include_self=True):
            raise BadMove(
                "%r can't be made a child of %r"
                % (node.ltree, new_parent.ltree if new_parent else None)
            )

        # Check if there's actually anything to do, return if not
        if node.parent_id is None:
            if new_parent is None:
                return
        elif new_parent is not None and node.ltree.parent() == new_parent.ltree:
            return

        old_parent_ltree = node.ltree.parent()
        old_parent_level = old_parent_ltree.level() if old_parent_ltree else -1

        # An expression which refers to the part of a given node's path which is
        # not in the current node's old parent path.
        # i.e. when node is 'a.b.c', the old parent will be 'a.b',
        # so for a descendant called 'a.b.c.d.e' we want to find 'c.d.e'.
        ltree_tail_expr = Subpath(models.F("ltree"), old_parent_level + 1)

        # Update the ltree on all descendant nodes to match new_parent
        qs = self.filter(ltree__descendant_or_equal=node.ltree)
        if new_parent is None:
            new_ltree_expr = ltree_tail_expr
        else:
            # TODO: how to do this without raw sql? django needs a cast expression
            # here otherwise the concat() fails because the ltree is interpreted
            # as text. Additionally, there's no available concatenation operator for ltrees
            # exposable in django.
            new_ltree_expr = CombinedExpression(
                lhs=RawSQL("%s::ltree", [new_parent.ltree]),
                connector="||",
                rhs=ltree_tail_expr,
            )
        qs.update(
            ltree=new_ltree_expr,
            # Update parent at the same time as ltree, otherwise the check constraint fails
            parent=models.Case(
                models.When(
                    pk=node.pk,
                    then=models.Value(new_parent.ltree if new_parent else None),
                ),
                default=Subpath(new_ltree_expr, 0, -1),
                output_field=node.__class__._meta.get_field("parent"),
            ),
        )

        # Update node in memory
        node.parent = new_parent
        node._set_ltree()
        node.save(update_fields=["parent"])


class MPathNode(models.Model):
    ltree = LTreeField(null=False, unique=True)
    label = models.CharField(null=False, blank=False, max_length=255)

    # Duplicating the whole path is annoying, but we need this field so that the
    # database can ensure consistency when we create a node.
    # Otherwise, we could create 'a.b' without first creating 'a'.
    parent = models.ForeignKey(
        "self",
        related_name="children",
        null=True,
        to_field="ltree",
        db_index=False,
        on_delete=models.CASCADE,
    )

    objects = MPathManager()

    class Meta:
        abstract = True
        indexes = [
            GistIndex(fields=["ltree"]),
            GistIndex(fields=["parent"]),
        ]

    def _set_ltree(self):
        if self.parent_id:
            ltree = "%s.%s" % (self.parent_id, self.label)
        else:
            ltree = self.label
        self.ltree = LTree(ltree)

    def save(self, **kwargs):
        # If no label, let the db throw an error. Otherwise, ensure path is consistent with
        # parent and label.
        if not self.label:
            raise ValueError(
                "%s objects must have a label. Got: label=%r"
                % (self.__class__.__name__, self.label)
            )

        # If this is a new node or parent has changed, re-calculate ltree.
        # NOTE: This only works for leaf nodes, so shouldnt be relied on.
        # It's here as a convenience so you can create nodes with a pre-set parent.
        # For *changing* parent of an existing node, use MPathManager.move_subtree()
        self._set_ltree()

        return super(MPathNode, self).save(**kwargs)

    def is_ancestor_of(self, other, include_self=False):
        if other is None:
            return False
        return self.ltree.is_ancestor_of(other.ltree, include_self=include_self)

    def is_descendant_of(self, other, include_self=False):
        if other is None:
            return True
        return self.ltree.is_descendant_of(other.ltree, include_self=include_self)

    def get_siblings(self, include_self=False):
        """
        Returns a queryset of this node's siblings, using the default manager.

        If include_self=True is given, the queryset will include this node.
        """
        mgr = self.__class__._default_manager
        qs = mgr.filter(parent__ltree=self.parent_id)

        if not include_self:
            qs = qs.exclude(ltree=self.ltree)
        return qs

    def get_children(self):
        """
        Returns a queryset of children for this node, using the default manager.
        """
        try:
            # Shortcut the database if this node has been fetched using
            # qs.get_cached_trees()
            return self._cached_children
        except AttributeError:
            mgr = self.__class__._default_manager
            return mgr.filter(ltree__lquery=self.ltree.children_lquery())

    def get_descendants(self, include_self=False):
        """
        Returns a queryset of descendants for this node, using the default manager.

        If include_self=True is given, the queryset will include this node.
        """
        mgr = self.__class__._default_manager
        qs = mgr.filter(ltree__descendant_or_equal=self.ltree)

        if not include_self:
            qs = qs.exclude(ltree=self.ltree)
        return qs

    def get_ancestors(self, include_self=False):
        """
        Returns a queryset of ancestors for this node, using the default manager.

        If include_self=True is given, the queryset will include this node.
        """
        mgr = self.__class__._default_manager
        qs = mgr.filter(ltree__ancestor_or_equal=self.ltree)

        if not include_self:
            qs = qs.exclude(ltree=self.ltree)
        return qs
