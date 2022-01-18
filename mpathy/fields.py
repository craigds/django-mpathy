from django.db import models


class Subpath(models.Func):
    function = "subpath"


class LTree(str):
    def labels(self):
        return self.split(".")

    def level(self):
        """
        Returns the level of this node.
        Root nodes are level 0.
        """
        return self.count(".")

    def is_root(self):
        return self.level() == 0

    def is_ancestor_of(self, other, include_self=False):
        if include_self and self == other:
            return True
        if other.level() <= self.level():
            return False
        return other.labels()[: self.level() + 1] == self.labels()

    def is_descendant_of(self, other, include_self=False):
        return other.is_ancestor_of(self, include_self=include_self)

    def parent(self):
        if self.level():
            return LTree(self.rsplit(".", 1)[0])
        return None

    def children_lquery(self):
        """
        Returns an lquery which finds nodes which are children of the current node.
        """
        return "%s.*{1}" % self

    def parent_lquery(self):
        """
        Returns an lquery to find the parent of the current node.
        """
        return ".".join(self.labels()[:-1])


class LTreeField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 256
        super(LTreeField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(LTreeField, self).deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def db_type(self, connection):
        return "ltree"

    def to_python(self, value):
        return LTree(value)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return LTree(value)


class Level(models.Transform):
    lookup_name = "level"
    function = "nlevel"

    @property
    def output_field(self):
        return models.IntegerField()


class LQuery(models.Lookup):
    lookup_name = "lquery"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "%s ~ %s" % (lhs, rhs), params


class DescendantOrEqual(models.Lookup):
    lookup_name = "descendant_or_equal"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "%s <@ %s" % (lhs, rhs), params


class AncestorOrEqual(models.Lookup):
    lookup_name = "ancestor_or_equal"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "%s @> %s" % (lhs, rhs), params


LTreeField.register_lookup(Level)
LTreeField.register_lookup(LQuery)
LTreeField.register_lookup(DescendantOrEqual)
LTreeField.register_lookup(AncestorOrEqual)
