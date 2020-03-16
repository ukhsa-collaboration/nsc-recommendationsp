from django.core.files.storage import default_storage
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from simple_history.models import HistoricalRecords

from nsc.document.models import Document
from nsc.utils.datetime import get_date_display, get_today
from nsc.utils.markdown import convert


class ReviewQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Review.STATUS.published).order_by("-review_start")

    def draft(self):
        return self.filter(status=Review.STATUS.draft).order_by("-review_start")

    def in_consultation(self):
        today = get_today()
        return self.filter(
            consultation_start__lte=today, consultation_end__gte=today
        ).order_by("-review_start")

    def not_in_consultation(self):
        """
        Get the policies which are currently not open for public comments - either
        because they are not in review or in review but not in that particular phase.
        """
        today = get_today()
        return self.filter(
            models.Q(consultation_start__gt=today)
            | models.Q(consultation_end__lt=today)
            | models.Q(consultation_start__isnull=True)
        ).order_by("-review_start")


class Review(TimeStampedModel):

    STATUS = Choices(("draft", _("Draft")), ("published", _("Published")))

    TYPE = Choices(
        ("evidence", _("Evidence review")),
        ("map", _("Evidence map")),
        ("cost", _("Cost-effective model")),
        ("systematic", _("Systematic review")),
    )

    name = models.CharField(verbose_name=_("name"), max_length=256)
    slug = models.SlugField(verbose_name=_("slug"), max_length=256, unique=True)
    status = models.CharField(
        verbose_name=_("status"), choices=STATUS, max_length=50, default=STATUS.draft
    )
    review_type = models.CharField(
        verbose_name=_("type of review"), choices=TYPE, max_length=50
    )

    review_start = models.DateField(
        verbose_name=_("review start date"), null=True, blank=True
    )
    review_end = models.DateField(
        verbose_name=_("review end date"), null=True, blank=True
    )
    consultation_start = models.DateField(
        verbose_name=_("consultation start date"), null=True, blank=True
    )
    consultation_end = models.DateField(
        verbose_name=_("consultation end date"), null=True, blank=True
    )
    nsc_meeting_date = models.DateField(
        verbose_name=_("NSC meeting date"), null=True, blank=True
    )

    recommendation = models.NullBooleanField(verbose_name=_("recommendation"))

    summary = models.TextField(verbose_name=_("summary"))
    summary_html = models.TextField(verbose_name=_("HTML summary"))

    history = HistoricalRecords()
    objects = ReviewQuerySet.as_manager()

    class Meta:
        ordering = ("name", "pk")
        verbose_name_plural = _("reviews")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("review:detail", kwargs={"slug": self.slug})

    def get_external_review(self):
        return Document.objects.for_review(self).external_reviews().first()

    def get_submission_form(self):
        return Document.objects.for_review(self).submission_forms().first()

    def get_cover_sheet(self):
        return Document.objects.for_review(self).cover_sheets().first()

    def get_evidence_review(self):
        return Document.objects.for_review(self).evidence_reviews().first()

    def clean(self):
        if not self.slug:
            self.slug = slugify(self.name)

        self.summary_html = convert(self.summary)

    def policies_display(self):
        return mark_safe("<br/>".join([policy.name for policy in self.policies.all()]))

    def consultation_start_display(self):
        return get_date_display(self.consultation_start)

    def consultation_end_display(self):
        return get_date_display(self.consultation_end)

    def discussion_date_display(self):
        return get_date_display(self.discussion_date)

    def has_notified_communications_department(self):
        # ToDo implement
        return False

    def has_notified_stakeholders_notified(self):
        # ToDo implement
        return False

    def has_consultation_dates_set(self):
        return self.consultation_start is not None and self.consultation_end is not None

    def has_nsc_meeting_date_set(self):
        return self.nsc_meeting_date is not None

    def has_external_review(self):
        return Document.objects.for_review(self).external_reviews().exists()

    def has_cover_sheet(self):
        return Document.objects.for_review(self).cover_sheets().exists()

    def has_evidence_review(self):
        return Document.objects.for_review(self).evidence_reviews().exists()

    def has_summary(self):
        return self.summary and len(self.summary) > 0

    def has_recommendation(self):
        return self.recommendation is not None

    def stakeholders(self):
        result = set()
        for policy in self.policies.all():
            result.update(policy.organisations.all())
        return sorted(result, key=lambda obj: obj.name)


@receiver(models.signals.post_delete, sender=Review)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    from nsc.document.models import review_document_path

    folder = review_document_path(instance)
    default_storage.delete(folder)
