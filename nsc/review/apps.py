from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from nsc.signals import clear_cache


class ReviewConfig(AppConfig):
    name = "nsc.review"

    def ready(self):
        from nsc.review.models import Review, ReviewRecommendation

        receiver(post_save, sender=Review)(clear_cache)
        receiver(post_delete, sender=Review)(clear_cache)
        receiver(post_save, sender=ReviewRecommendation)(clear_cache)
        receiver(post_delete, sender=ReviewRecommendation)(clear_cache)
