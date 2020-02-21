from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords


class OrganisationQuerySet(QuerySet):
    def public(self, policy=None):
        qs = self.filter(is_public=True)
        if policy:
            qs = qs.filter(policies=policy)
        return qs


class Organisation(TimeStampedModel):

    name = models.CharField(verbose_name=_("name"), max_length=256)
    url = models.URLField(verbose_name=_("url"), max_length=256, blank=True)
    is_public = models.BooleanField(verbose_name=_("is_public"), default=False)

    policies = models.ManyToManyField(
        "policy.Policy", verbose_name=_("policies"), related_name="organisations"
    )

    history = HistoricalRecords()
    objects = OrganisationQuerySet().as_manager()

    class Meta:
        ordering = ("name", "pk")
        verbose_name_plural = _("organisations")

    def __str__(self):
        return self.name

    def get_detail_url(self):
        return reverse("organisation:detail", kwargs={"pk": self.pk})

    def get_edit_url(self):
        return reverse("organisation:add", kwargs={"pk": self.pk})

    def is_public_display(self):
        return _("Yes") if self.is_public else _("No")

    def contacts_display(self):
        return mark_safe(
            "<br>/".join([contact.name for contact in self.contacts.all()])
        )

    def policies_display(self):
        return mark_safe("<br/>".join([policy.name for policy in self.policies.all()]))
