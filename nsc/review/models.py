from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.files.storage import default_storage
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from simple_history.models import HistoricalRecords

from nsc.contact.models import Contact
from nsc.document.models import Document
from nsc.notify.models import Email
from nsc.stakeholder.models import Stakeholder
from nsc.utils.datetime import get_date_display, get_today
from nsc.utils.markdown import convert


class ReviewQuerySet(models.QuerySet):
    def dates_confirmed(self):
        return self.filter(dates_confirmed=True)

    def consultation_open(self):
        return self.dates_confirmed().filter(consultation_start__lte=get_today())

    def published(self):
        return self.filter(review_end__lte=get_today()).order_by("-review_start")

    def in_progress(self):
        today = get_today()
        return self.filter(
            models.Q(review_start__lte=today)
            & (models.Q(review_end__isnull=True) | models.Q(review_end__gte=today))
        )

    def open_for_comments(self):
        today = get_today()
        return self.filter(consultation_start__lte=today, consultation_end__gte=today)

    def closed_for_comments(self):
        today = get_today()
        return self.filter(
            ~(
                models.Q(consultation_start__lte=today)
                & models.Q(consultation_end__gte=today)
            )
        )


class Review(TimeStampedModel):

    STATUS = Choices(
        ("development", _("In review")),
        ("pre_consultation", _("Pre-consultation")),
        ("in_consultation", _("In consultation")),
        ("post_consultation", _("Post-consultation")),
        ("completed", _("Completed")),
    )

    TYPE = Choices(
        ("evidence", _("Evidence review")),
        ("map", _("Evidence map")),
        ("cost", _("Cost-effective model")),
        ("systematic", _("Systematic review")),
        ("other", _("Other")),
    )

    name = models.CharField(verbose_name=_("name"), max_length=256)
    slug = models.SlugField(verbose_name=_("slug"), max_length=256, unique=True)

    review_type = ArrayField(
        models.CharField(max_length=10, choices=TYPE), verbose_name=_("type of review"),
    )

    dates_confirmed = models.BooleanField(default=False)
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

    background = models.TextField(verbose_name=_("history"))
    background_html = models.TextField(verbose_name=_("HTML history"))

    stakeholders = models.ManyToManyField(Stakeholder, related_name="reviews")
    stakeholders_confirmed = models.BooleanField(default=False)

    open_consultation_notifications = models.ManyToManyField(
        Email, related_name="reviews"
    )

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
        return Document.objects.for_review(self).external_reviews()

    def get_submission_form(self):
        return Document.objects.for_review(self).submission_forms().first()

    @cached_property
    def submission_form(self):
        return self.get_submission_form()

    def get_cover_sheet(self):
        return Document.objects.for_review(self).cover_sheets().first()

    @cached_property
    def cover_sheet(self):
        return self.get_cover_sheet()

    def get_evidence_review(self):
        return Document.objects.for_review(self).evidence_reviews().first()

    @cached_property
    def evidence_review(self):
        return self.get_evidence_review()

    def get_cost_effective_model(self):
        return Document.objects.for_review(self).cost_effective_models().first()

    @cached_property
    def cost_effective_model(self):
        return self.get_cost_effective_model()

    def get_evidence_map(self):
        return Document.objects.for_review(self).evidence_maps().first()

    @cached_property
    def evidence_map(self):
        return self.get_evidence_map()

    def get_systematic_review(self):
        return Document.objects.for_review(self).systematic_reviews().first()

    @cached_property
    def systematic_review(self):
        return self.get_systematic_review()

    def get_other_review_documents(self):
        return Document.objects.for_review(self).others()

    @cached_property
    def other_review_documents(self):
        return self.get_other_review_documents()

    def policies_display(self):
        return mark_safe("<br/>".join([policy.name for policy in self.policies.all()]))

    def consultation_start_display(self):
        return get_date_display(self.consultation_start)

    def consultation_end_display(self):
        return get_date_display(self.consultation_end)

    def nsc_meeting_date_display(self):
        return get_date_display(self.nsc_meeting_date)

    def manager_display(self):
        # Todo return the name of the person who is managing the review
        return ""

    def has_notified_stakeholders(self):
        return self.stakeholders_confirmed

    def has_consultation_dates_set(self):
        return (
            self.dates_confirmed
            and self.consultation_start is not None
            and self.consultation_end is not None
        )

    def has_nsc_meeting_date_set(self):
        return self.dates_confirmed and self.nsc_meeting_date is not None

    def has_external_review(self):
        return Document.objects.for_review(self).external_reviews().exists()

    def has_supporting_documents(self):
        required_document_types = {
            Document.TYPE.cover_sheet,
            *map(
                lambda item: item[1],
                filter(
                    lambda item: item[0] in self.review_type,
                    [
                        (self.TYPE.evidence, Document.TYPE.evidence_review),
                        (self.TYPE.map, Document.TYPE.evidence_map),
                        (self.TYPE.cost, Document.TYPE.cost),
                        (self.TYPE.systematic, Document.TYPE.systematic),
                    ],
                ),
            ),
        }

        return (
            set(self.documents.values_list("document_type", flat=True))
            & required_document_types
        ) == required_document_types

    def has_submission_form(self):
        return Document.objects.for_review(self).submission_forms().exists()

    def has_summary(self):
        all_summary_drafts = list(self.summary_drafts.all())
        return len(all_summary_drafts) and all(d.updated for d in all_summary_drafts)

    def has_history(self):
        return self.background and len(self.background) > 0

    def has_recommendation(self):
        return self.recommendation is not None

    def status(self):
        today = get_today()
        if self.dates_confirmed and self.review_end and self.review_end <= today:
            return self.STATUS.completed
        elif (
            self.dates_confirmed
            and self.consultation_end
            and self.consultation_end < today
        ):
            return self.STATUS.post_consultation
        elif (
            self.dates_confirmed
            and self.consultation_start
            and self.consultation_start <= today
        ):
            return self.STATUS.in_consultation
        elif self.has_external_review():
            return self.STATUS.pre_consultation
        else:
            return self.STATUS.development

    def status_display(self):
        return self.STATUS[self.status()]

    @property
    def policy_stakeholders(self):
        return (
            Stakeholder.objects.filter(policies__reviews__pk=self.pk)
            .distinct()
            .order_by("name")
        )

    def save(self, **kwargs):
        if not self.pk and not self.review_start:
            self.review_start = get_today()

        if not self.slug:
            self.slug = slugify(self.name)

        self.summary_html = convert(self.summary)
        self.background_html = convert(self.background)

        return super(Review, self).save(**kwargs)

    def send_open_consultation_notifications(self):
        email_context = {"review": self.name}

        # find each stakeholder without a notification object and create one
        existing_notification_emails = self.open_consultation_notifications.values_list(
            "address", flat=True
        )
        self.open_consultation_notifications.add(
            *Email.objects.bulk_create(
                Email(
                    address=contact.email,
                    template_id=settings.NOTIFY_TEMPLATE_CONSULTATION_OPEN,
                    context=email_context,
                )
                for contact in Contact.objects.with_email()
                .filter(stakeholder__in=self.stakeholders.all())
                .exclude(email__in=existing_notification_emails)
            )
        )

        if settings.PHE_COMMUNICATIONS_EMAIL not in existing_notification_emails:
            self.open_consultation_notifications.add(
                Email.objects.create(
                    address=settings.PHE_COMMUNICATIONS_EMAIL,
                    template_id=settings.NOTIFY_TEMPLATE_CONSULTATION_OPEN,
                    context=email_context,
                )
            )


class SummaryDraft(TimeStampedModel):
    text = models.TextField()
    policy = models.ForeignKey(
        "policy.Policy", on_delete=models.CASCADE, related_name="summary_drafts"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="summary_drafts"
    )
    updated = models.BooleanField(default=False)

    def __str__(self):
        return f"Plain English Summary for {self.policy} (review {self.review})."


@receiver(models.signals.post_delete, sender=Review)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    from nsc.document.models import document_path

    folder = document_path(instance)
    default_storage.delete(folder)
