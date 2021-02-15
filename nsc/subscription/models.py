from django.db import models

from django_extensions.db.models import TimeStampedModel

from ..policy.models import Policy


class Subscription(TimeStampedModel):
    email = models.EmailField(unique=True)
    policies = models.ManyToManyField(Policy, related_name="subscriptions")

    def __str__(self):
        return self.email
