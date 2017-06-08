from __future__ import absolute_import, unicode_literals
from django.db import models

from .compat import GistIndex
from .fields import LTree, LTreeField


class MPathNode(models.Model):
    ltree = LTreeField(null=False, unique=True)
    label = models.CharField(null=False, blank=False, max_length=255)

    # Duplicating the whole path is annoying, but we need this field so that the
    # database can ensure consistency when we create a node.
    # Otherwise, we could create 'a.b' without first creating 'a'.
    _parent = models.ForeignKey('self', null=True, to_field='ltree', db_index=False)

    class Meta:
        abstract = True
        indexes = [
            GistIndex(fields=['ltree']),
            GistIndex(fields=['_parent']),
        ]

    def _set_ltree(self):
        if self._parent_id:
            ltree = '%s.%s' % (self._parent_id, self.label)
        else:
            ltree = self.label
        self.ltree = LTree(ltree)

    @property
    def parent(self):
        mgr = self.__class__._default_manager
        parent_ltree = self.ltree._parent
        if parent_ltree:
            return mgr.get(ltree=parent_ltree)
        else:
            return None

    @parent.setter
    def parent(self, parent):
        """
        Sets the ltree for this node so that it is a child of the given parent node.
        """
        self._parent = parent
        self._set_ltree()

    def save(self, **kwargs):
        # If no label, let the db throw an error. Otherwise, ensure path is consistent with
        # parent and label.
        if not self.label:
            raise ValueError("%s objects must have a label. Got: label=%r" % (self.__class__.__name__, self.label))

        self._set_ltree()

        return super(MPathNode, self).save(**kwargs)

    def get_children(self):
        """
        Returns a queryset of children for this node, using the default manager.
        """
        mgr = self.__class__._default_manager
        return mgr.filter(ltree__lquery=self.ltree.children_lquery())

    def get_descendants(self, include_self=True):
        """
        Returns a queryset of descendants for this node, using the default manager.

        If include_self=True is given, the queryset will include this node.
        """
        mgr = self.__class__._default_manager
        qs = mgr.filter(ltree__descendant_or_equal=self.ltree)

        if not include_self:
            qs = qs.exclude(ltree=self.ltree)
        return qs

    def get_ancestors(self, include_self=True):
        """
        Returns a queryset of ancestors for this node, using the default manager.

        If include_self=True is given, the queryset will include this node.
        """
        mgr = self.__class__._default_manager
        qs = mgr.filter(ltree__ancestor_or_equal=self.ltree)

        if not include_self:
            qs = qs.exclude(ltree=self.ltree)
        return qs
