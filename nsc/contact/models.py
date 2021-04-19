from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords


class ContactQuerySet(models.QuerySet):
    def with_email(self):
        return self.exclude(email="")


class Contact(TimeStampedModel):

    name = models.CharField(
        verbose_name=_("Name of contact (optional)"), max_length=256, blank=True,
    )
    role = models.CharField(
        verbose_name=_("Contact's role (optional)"),
        max_length=50,
        blank=True,
        default="",
    )
    email = models.EmailField(verbose_name=_("Contact's email (optional)"), blank=True,)
    phone = models.CharField(
        verbose_name=_("Contact's mobile phone number (optional)"),
        max_length=50,
        blank=True,
    )
    stakeholder = models.ForeignKey(
        "stakeholder.Stakeholder",
        on_delete=models.CASCADE,
        verbose_name=_("stakeholder"),
        related_name="contacts",
    )

    history = HistoricalRecords()

    objects = ContactQuerySet.as_manager()

    class Meta:
        ordering = ("name", "pk")
        verbose_name_plural = _("contacts")

    def __str__(self):
        return self.name

    def get_detail_url(self):
        return reverse("contact:detail", kwargs={"pk": self.pk})

    def get_edit_url(self):
        return reverse("contact:edit", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("contact:delete", kwargs={"pk": self.pk})
