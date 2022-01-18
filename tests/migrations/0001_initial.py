# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from django.db import migrations, models
import django.contrib.postgres.indexes
import django.db.models.deletion

import mpathy.fields


def forwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = []
    initial = True

    operations = [
        migrations.CreateModel(
            name="MyTree",
            fields=[
                ("ltree", mpathy.fields.LTreeField(unique=True)),
                ("label", models.CharField(max_length=255)),
                (
                    "parent",
                    models.ForeignKey(
                        db_index=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tests.MyTree",
                        to_field="ltree",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddIndex(
            model_name="mytree",
            index=django.contrib.postgres.indexes.GistIndex(
                fields=["ltree"], name="tests_mytre_ltree_600965_gist"
            ),
        ),
        migrations.AddIndex(
            model_name="mytree",
            index=django.contrib.postgres.indexes.GistIndex(
                fields=["parent"], name="tests_mytre_parent_05b59f_gist"
            ),
        ),
    ]
