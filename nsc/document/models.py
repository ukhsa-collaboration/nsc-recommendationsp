import os

from django.core.validators import FileExtensionValidator
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from simple_history.models import HistoricalRecords

from nsc.utils.datetime import get_today


class DocumentQuerySet(models.QuerySet):
    def for_policy(self, policy):
        return self.filter(documentpolicy__policy_id=policy.pk)

    def for_review(self, review):
        return self.filter(review_id=review.pk)

    def cover_sheets(self):
        return self.filter(document_type=Document.TYPE.cover_sheet)

    def evidence_reviews(self):
        return self.filter(document_type=Document.TYPE.evidence_review)

    def evidence_maps(self):
        return self.filter(document_type=Document.TYPE.evidence_map)

    def systematic_reviews(self):
        return self.filter(document_type=Document.TYPE.systematic)

    def cost_effective_models(self):
        return self.filter(document_type=Document.TYPE.cost)

    def external_reviews(self):
        return self.filter(document_type=Document.TYPE.external_review)

    def submission_forms(self):
        return self.filter(document_type=Document.TYPE.submission_form)

    def others(self):
        return self.filter(document_type=Document.TYPE.other)

    def archive(self):
        return self.filter(document_type=Document.TYPE.archive)


def document_path(instance, filename=None):
    from nsc.review.models import Review

    if isinstance(instance, Document):
        review = instance.review
    elif isinstance(instance, Review):
        review = instance
    else:
        raise ValueError("Instance must be either a Review or Document")

    year = get_today().year
    path = os.path.join(str(year))
    if review and review.review_start:
        year = review.review_start.year
        path = os.path.join(str(year), review.slug)

    if filename:
        return os.path.join(path, filename)
    else:
        return path


class DocumentPolicy(TimeStampedModel):
    SOURCE = Choices(
        ("review", _("Review")),
        ("archive", _("Archive")),
    )

    document = models.ForeignKey("Document", on_delete=models.CASCADE)
    policy = models.ForeignKey("policy.Policy", on_delete=models.CASCADE)
    source = models.CharField(max_length=7, choices=SOURCE, default=SOURCE.review)


class Document(TimeStampedModel):

    TYPE = Choices(
        ("cover_sheet", _("Coversheet")),
        ("submission_form", _("Submission form")),
        ("evidence_review", _("Evidence review")),
        ("evidence_map", _("Evidence map")),
        ("cost", _("Cost-effective model")),
        ("systematic", _("Systematic review")),
        ("external_review", _("External review")),
        ("archive", _("Archive")),
        ("other", _("Other")),
    )

    name = models.CharField(verbose_name=_("name"), max_length=256)
    document_type = models.CharField(
        verbose_name=_("type of document"), choices=TYPE, max_length=256
    )
    upload = models.FileField(
        verbose_name=_("upload"),
        upload_to=document_path,
        max_length=256,
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "odt"])],
    )
    review = models.ForeignKey(
        "review.Review",
        on_delete=models.SET_NULL,
        verbose_name=_("review"),
        related_name="documents",
        null=True,
    )

    policies = models.ManyToManyField(
        "policy.Policy",
        through="DocumentPolicy",
        related_name="policy_documents",
        null=True,
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
        if self.upload.name:
            self.upload.storage.delete(self.upload.name)


@receiver(models.signals.post_delete, sender=Document)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    instance.delete_file()
