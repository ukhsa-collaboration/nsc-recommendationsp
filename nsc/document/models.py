import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from simple_history.models import HistoricalRecords


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
    if review:
        return "{0}/{1}/{2}".format(review.review_start.year, review.slug, filename)
    else:
        today = datetime.date.today()
        return "uploads/{0}/{1}/{2}".format(today.year, today.month, filename)


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
    upload = models.FileField(
        verbose_name=_("document"),
        upload_to=review_document_path,
        null=True,
        blank=True,
    )
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
