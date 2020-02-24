from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from simple_history.models import HistoricalRecords


class DocumentQuerySet(models.QuerySet):
    def for_review(self, review_id):
        return self.filter(review_id=review_id)

    def policy(self, review_id):
        return self.for_review(review_id).filter(document_type=Document.TYPES.policy)

    def review(self, review_id):
        return self.for_review(review_id).filter(document_type=Document.TYPES.review)

    def recommendation(self, review_id):
        return self.for_review(review_id).filter(
            document_type=Document.TYPES.recommendation
        )


class Document(TimeStampedModel):

    TYPES = Choices(
        ("policy", _("Policy")),
        ("review", _("Review")),
        ("recommendation", _("Recommendation")),
    )

    name = models.CharField(verbose_name=_("name"), max_length=256)
    document_type = models.CharField(
        verbose_name=_("type of document"), choices=TYPES, max_length=256
    )
    document = models.FileField(verbose_name=_("document"), null=True, blank=True)
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
