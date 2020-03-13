from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from simple_history.models import HistoricalRecords

from nsc.utils.datetime import get_today


class DocumentQuerySet(models.QuerySet):
    def for_review(self, review):
        return self.filter(review_id=review.pk)

    def coversheets(self):
        return self.filter(document_type=Document.TYPE.coversheet)

    def evidence_reviews(self):
        return self.filter(document_type=Document.TYPE.evidence_review)

    def submission_forms(self):
        return self.filter(document_type=Document.TYPE.submission_form)

    def recommendations(self):
        return self.filter(document_type=Document.TYPE.recommendation)


def review_document_path(instance, filename):
    review = instance.review
    year = review.review_start.year if review.review_start else get_today().year
    return "{0}/{1}/{2}".format(year, review.slug, filename)


class Document(TimeStampedModel):

    TYPE = Choices(
        ("coversheet", _("Coversheet")),
        ("submission_form", _("Submission form")),
        ("evidence_review", _("Evidence Review")),
        ("recommendation", _("Review recommendation")),
    )

    name = models.CharField(verbose_name=_("name"), max_length=256)
    document_type = models.CharField(
        verbose_name=_("type of document"), choices=TYPE, max_length=256
    )
    upload = models.FileField(verbose_name=_("upload"), upload_to=review_document_path)
    is_public = models.BooleanField(verbose_name=_("is public"))
    review = models.ForeignKey(
        "review.Review",
        on_delete=models.CASCADE,
        verbose_name=_("review"),
        related_name="documents",
    )

    history = HistoricalRecords()
    objects = DocumentQuerySet.as_manager()

    class Meta:
        ordering = ("name", "pk")
        verbose_name_plural = _("documents")

    def __str__(self):
        return self.name

    def get_download_url(self):
        return reverse("document:download", kwargs={"pk": self.pk})

    def exists(self):
        return Document.objects.filter(pk=self.pk).exists() if self.pk else False

    def file_exists(self):
        return self.upload.storage.exists(self.upload.name)

    def delete_file(self):
        self.upload.storage.delete(self.upload.name)


@receiver(models.signals.post_delete, sender=Document)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    instance.delete_file()
