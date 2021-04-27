from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from nsc.signals import clear_cache


class PolicyConfig(AppConfig):
    name = "nsc.policy"

    def ready(self):
        from nsc.policy.models import Policy

        receiver(post_save, sender=Policy)(clear_cache)
        receiver(post_delete, sender=Policy)(clear_cache)
