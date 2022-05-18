from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from nsc.utils.forms import ChoiceArrayField


class StakeholderQuerySet(QuerySet):
    def public(self, policy=None):
        qs = self.filter(is_public=True)
        if policy:
            qs = qs.filter(policies=policy)
        return qs


class Stakeholder(TimeStampedModel):
    TYPE_PROFESSIONAL = "PROFESSIONAL"
    TYPE_ACADEMIC = "ACADEMIC"
    TYPE_PATIENT_GROUP = "PATIENT_GROUP"
    TYPE_INDIVIDUAL = "INDIVIDUAL"
    TYPE_COMMERCIAL = "COMMERCIAL"
    TYPE_OTHER = "OTHER"
    TYPE_CHOICES = (
        (TYPE_PROFESSIONAL, _("Royal College or other professional organisation")),
        (TYPE_ACADEMIC, _("Academic/research organisation")),
        (TYPE_PATIENT_GROUP, _("Patient group/voluntary sector")),
        (TYPE_INDIVIDUAL, _("Individual")),
        (TYPE_COMMERCIAL, _("Commercial organisation")),
        (TYPE_OTHER, _("Other")),
    )

    COUNTRY_ENGLAND = "ENGLAND"
    COUNTRY_NORTHERN_IRELAND = "NORTHERN_IRELAND"
    COUNTRY_SCOTLAND = "SCOTLAND"
    COUNTRY_WALES = "WALES"
    COUNTRY_UK = "UK"
    COUNTRY_INTERNATIONAL = "INTERNATIONAL"
    COUNTRY_CHOICES = (
        (COUNTRY_ENGLAND, _("England")),
        (COUNTRY_NORTHERN_IRELAND, _("Northern Ireland")),
        (COUNTRY_SCOTLAND, _("Scotland")),
        (COUNTRY_WALES, _("Wales")),
        (COUNTRY_UK, _("UK")),
        (COUNTRY_INTERNATIONAL, _("International")),
    )
    CHOICE_DB_VALUES = [db_value for db_value, verbose in COUNTRY_CHOICES]

    name = models.CharField(
        verbose_name=_("stakeholder name"),
        max_length=256,
    )
    type = models.CharField(
        verbose_name=_("stakeholder type"),
        max_length=13,
        choices=TYPE_CHOICES,
    )
    countries = ChoiceArrayField(
        models.CharField(
            choices=COUNTRY_CHOICES, max_length=max(len(c) for c in CHOICE_DB_VALUES)
        ),
        null=True,
    )
    url = models.URLField(verbose_name=_("url"), max_length=256, blank=True)
    twitter = models.URLField(
        verbose_name=_("twitter"),
        max_length=256,
        blank=True,
    )
    is_public = models.BooleanField(
        verbose_name=_("Should this organisation be published on the condition pages"),
        default=False,
    )

    policies = models.ManyToManyField(
        "policy.Policy", verbose_name=_("policies"), related_name="stakeholders"
    )

    comments = models.TextField(
        verbose_name=_("Additional comments (for internal use only)"),
        blank=True,
        default="",
    )

    history = HistoricalRecords()
    objects = StakeholderQuerySet().as_manager()

    class Meta:
        ordering = ("name", "pk")
        verbose_name_plural = _("stakeholders")

    def __str__(self):
        return self.name

    def get_detail_url(self):
        return reverse("stakeholder:detail", kwargs={"pk": self.pk})

    def get_edit_url(self):
        return reverse("stakeholder:edit", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("stakeholder:delete", kwargs={"pk": self.pk})

    def is_public_display(self):
        return _("Yes") if self.is_public else _("No")

    def contacts_display(self):
        return mark_safe(
            "<br>/".join([contact.name for contact in self.contacts.all()])
        )

    def contacts_emails(self):
        return [contact.email for contact in self.contacts.all() if contact.email]

    def policies_display(self):
        return mark_safe("<br/>".join([policy.name for policy in self.policies.all()]))

    def get_countries_display(self):
        choices = dict(self.COUNTRY_CHOICES)
        if self.countries:
            countries = [str(choices[c]) for c in self.countries]
            return ", ".join(countries)
        return ""
