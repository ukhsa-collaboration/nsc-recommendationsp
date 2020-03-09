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
        return self.filter(phase=Review.PHASE.consultation).order_by("-review_start")


class Review(TimeStampedModel):

    STATUS = Choices(("draft", _("Draft")), ("published", _("Published")))

    PHASE = Choices(
        ("pre_consultation", _("Pre-consultation")),
        ("consultation", _("Consultation")),
        ("post_consultation", _("Post consultation")),
        ("completed", _("Completed")),
    )

    TYPE = Choices(("rapid", _("Rapid review")), ("other", _("Other")))

    name = models.CharField(verbose_name=_("name"), max_length=256)
    slug = models.SlugField(verbose_name=_("slug"), max_length=256, unique=True)
    status = models.CharField(
        verbose_name=_("status"), choices=STATUS, max_length=50, default=STATUS.draft
    )
    phase = models.CharField(
        verbose_name=_("review phase"),
        choices=PHASE,
        max_length=50,
        default=PHASE.pre_consultation,
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
    discussion_date = models.DateField(
        verbose_name=_("discussion date"), null=True, blank=True
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
        if self.status == self.STATUS.published:
            if self.phase != self.PHASE.completed:
                raise ValidationError(_("A published review cannot be reopened"))

        if not self.slug:
            self.slug = slugify(self.name)

        self.summary_html = convert(self.summary)

    def policies_display(self):
        return mark_safe("<br/>".join([policy.name for policy in self.policies.all()]))

    def consultation_start_display(self):
        return get_date_display(self.consultation_start)

    def consultation_end_display(self):
        return get_date_display(self.consultation_end)

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
        self.phase = self.PHASE.pre_consultation
        self.review_start = get_today()
        if commit:
            self.clean()
            self.save()

    def close(self, commit=True):
        self.status = self.STATUS.published
        self.phase = self.PHASE.completed
        self.review_end = get_today()
        if commit:
            self.clean()
            self.save()

    def open_consultation(self, start=None, end=None, commit=True):
        if self.status != self.STATUS.draft:
            raise ValidationError(
                _("You can only open a draft review for public consultation")
            )

        self.phase = self.PHASE.consultation
        self.consultation_start = start if start else get_today()
        self.consultation_end = (
            end if end else self.consultation_start + relativedelta(months=+3)
        )
        if commit:
            self.clean()
            self.save()

    def close_consultation(self, commit=True):
        self.phase = self.PHASE.post_consultation
        self.consultation_end = get_today()
        if commit:
            self.clean()
            self.save()
