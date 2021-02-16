from django.contrib.admin import ModelAdmin, register

from .models import Subscription


@register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = (
        "email",
        "created",
        "modified",
    )
