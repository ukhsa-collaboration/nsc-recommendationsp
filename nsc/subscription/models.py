from django.db import models

from django_extensions.db.models import TimeStampedModel

from ..policy.models import Policy


class Subscription(TimeStampedModel):
    email = models.EmailField(unique=True)
    policies = models.ManyToManyField(Policy, related_name="subscriptions")

    def __str__(self):
        return self.email


class StakeholderSubscription(TimeStampedModel):
    title = models.CharField(max_length=10)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    organisation = models.CharField(max_length=256)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
