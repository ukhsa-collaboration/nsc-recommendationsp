from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords


class Contact(TimeStampedModel):

    name = models.CharField(verbose_name=_("name"), max_length=256)
    email = models.EmailField(verbose_name=_("email"))
    phone = models.CharField(verbose_name=_("phone number"), max_length=50, blank=True)
    organisation = models.ForeignKey(
        "organisation.Organisation",
        on_delete=models.CASCADE,
        verbose_name=_("organisation"),
        related_name="contacts",
    )

    history = HistoricalRecords()

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
