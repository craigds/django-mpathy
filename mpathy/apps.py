from django.apps import AppConfig
from django.db.models.signals import post_migrate, pre_migrate


class MpathyConfig(AppConfig):
    name = 'mpathy'

    def ready(self):
        from .operations import inject_pre_migration_operations, inject_post_migration_operations

        pre_migrate.connect(inject_pre_migration_operations, sender=self)
        post_migrate.connect(inject_post_migration_operations, sender=self)
