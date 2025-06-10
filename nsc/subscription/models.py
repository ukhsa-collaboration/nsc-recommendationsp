from django.db import models
from django.urls import reverse

from django_extensions.db.models import TimeStampedModel

from ..policy.models import Policy
from .signer import get_object_signature


class SubscriptionQuerySet(models.QuerySet):
    def with_email(self):
        return self.exclude(email="")


class Subscription(TimeStampedModel):
    email = models.EmailField(unique=True)
    policies = models.ManyToManyField(Policy, related_name="subscriptions")

    objects = SubscriptionQuerySet.as_manager()

    def __str__(self):
        return self.email

    @property
    def management_url(self):
        return reverse(
            "subscription:public-manage",
            kwargs={"pk": self.pk, "token": get_object_signature(self)},
        )


class StakeholderSubscription(TimeStampedModel):
    title = models.CharField(max_length=10)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    organisation = models.CharField(max_length=256)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
