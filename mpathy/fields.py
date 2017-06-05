from __future__ import absolute_import, unicode_literals
from django.db import models

from six import text_type


class LTree(text_type):
    def labels(self):
        return self.split('.')

    def children_lquery(self):
        """
        Returns an lquery which finds nodes which are children of the current node.
        """
        return '%s.*{1}' % self

    def parent_lquery(self):
        """
        Returns an lquery to find the parent of the current node.
        """
        return '.'.join(self.labels()[:-1])


class LTreeField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 256
        super(LTreeField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(LTreeField, self).deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def db_type(self, connection):
        return 'ltree'

    def to_python(self, value):
        return LTree(value)


class LQuery(models.Lookup):
    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s ~ %s' % (lhs, rhs), params


LTreeField.register_lookup(LQuery)


class DescendantOrEqual(models.Lookup):
    lookup_name = 'descendant_or_equal'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s <@ %s' % (lhs, rhs), params


class AncestorOrEqual(models.Lookup):
    lookup_name = 'ancestor_or_equal'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s @> %s' % (lhs, rhs), params
