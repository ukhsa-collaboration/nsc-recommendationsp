from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from nsc.signals import clear_cache


class DocumentConfig(AppConfig):
    name = "nsc.document"

    def ready(self):
        from nsc.document.models import Document

        receiver(post_save, sender=Document)(clear_cache)
        receiver(post_delete, sender=Document)(clear_cache)
