from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from dateutil import relativedelta
from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from simple_history.models import HistoricalRecords

from nsc.document.models import Document
from nsc.organisation.models import Organisation
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

    recommendation = models.BooleanField(
        verbose_name=_("recommendation"), default=False
    )

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

    def get_evidence_review_document(self):
        return Document.objects.for_review(self).evidence_reviews().first()

    def get_submission_form(self):
        return Document.objects.for_review(self).submission_forms().first()

    def get_coversheet_document(self):
        return Document.objects.for_review(self).coversheets().first()

    def get_recommendation_document(self):
        return Document.objects.for_review(self).recommendations().first()

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

    def stakeholders(self):
        # ToDo this is just a way of generating data. It is nowhere close to
        # being correct.
        if self.policies:
            return self.policies.first().organisations.all()
        else:
            return Organisation.objects.none()

    def open(self, commit=True):
        if self.status == self.STATUS.published:
            raise ValidationError(_("You cannot open a review that has been published"))

        self.status = self.STATUS.draft
        self.review_start = get_today()
        if commit:
            self.clean()
            self.save()

    def close(self, commit=True):
        self.status = self.STATUS.published
        self.review_end = get_today()
        if commit:
            self.clean()
            self.save()

    def open_consultation(self, start=None, end=None, commit=True):
        if self.status != self.STATUS.draft:
            raise ValidationError(
                _("You can only open a draft review for public consultation")
            )

        self.consultation_start = start if start else get_today()
        self.consultation_end = (
            end if end else self.consultation_start + relativedelta(months=+3)
        )
        if commit:
            self.clean()
            self.save()

    def close_consultation(self, commit=True):
        self.consultation_end = get_today()
        if commit:
            self.clean()
            self.save()
