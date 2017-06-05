from django.db.models import Index

#
# Extracted from https://github.com/django/django/pull/8303
#

try:
    from django.contrib.postgres.indexes import GistIndex
except ImportError:
    class GistIndex(Index):
        suffix = 'gist'
        # Allow an index name longer than 30 characters since the suffix is 4
        # characters (usual limit is 3). Since this index can only be used on
        # PostgreSQL, the 30 character limit for cross-database compatibility isn't
        # applicable.
        max_name_length = 31

        def create_sql(self, model, schema_editor):
            return super(GistIndex, self).create_sql(model, schema_editor, using=' USING gist')
