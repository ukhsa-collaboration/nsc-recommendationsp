from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from nsc.signals import clear_cache


class StakeholderConfig(AppConfig):
    name = "nsc.stakeholder"

    def ready(self):
        from nsc.stakeholder.models import Stakeholder

        receiver(post_save, sender=Stakeholder)(clear_cache)
        receiver(post_delete, sender=Stakeholder)(clear_cache)
