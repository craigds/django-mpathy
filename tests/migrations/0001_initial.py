# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from django.db import migrations, models
import django.db.models.deletion

from mpathy.operations import LTreeExtension
import mpathy.compat
import mpathy.fields


def forwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = []
    initial = True

    operations = [
        LTreeExtension(),

        migrations.CreateModel(
            name='MyTree',
            fields=[
                ('ltree', mpathy.fields.LTreeField(unique=True)),
                ('label', models.CharField(max_length=255)),
                ('_parent', models.ForeignKey(db_index=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='tests.MyTree', to_field='ltree')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='mytree',
            index=mpathy.compat.GistIndex(fields=['ltree'], name='tests_mytre_ltree_600965_gist'),
        ),
        migrations.AddIndex(
            model_name='mytree',
            index=mpathy.compat.GistIndex(fields=['_parent'], name='tests_mytre__parent_05b59f_gist'),
        ),

        migrations.RunSQL(
            # Check that the ltree is always consistent with being a child of _parent
            '''
            ALTER TABLE tests_mytree ADD CONSTRAINT check_ltree CHECK (
                ltree ~ (_parent_id::text || '.*{1}')::lquery
                OR (_parent_id IS NULL AND ltree ~ '*{1}'::lquery)
            )
            ''',
            reverse_sql='''
            ALTER TABLE tests_mytree DROP CONSTRAINT check_ltree
            ''',

        )
    ]
