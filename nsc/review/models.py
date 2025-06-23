import logging
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.files.storage import default_storage
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from simple_history.models import HistoricalRecords

from nsc.contact.models import Contact
from nsc.document.models import Document
from nsc.notify.models import Email
from nsc.stakeholder.models import Stakeholder
from nsc.utils.datetime import get_date_display, get_today
from nsc.utils.markdown import convert


logger = logging.getLogger(__name__)


class ReviewQuerySet(models.QuerySet):
    def dates_confirmed(self):
        return self.filter(dates_confirmed=True)

    def exclude_legacy(self):
        return self.filter(is_legacy=False)

    def consultation_open(self):
        return self.dates_confirmed().filter(consultation_start__lte=get_today())

    def published(self):
        return self.filter(published=True).order_by("-review_start")

    def in_progress(self):
        return self.exclude(published=True)

    def open_for_comments(self):
        today = get_today()
        return self.in_progress().filter(
            consultation_start__lte=today, consultation_end__gte=today
        )

    def closed_for_comments(self):
        today = get_today()
        return self.filter(
            ~(
                models.Q(consultation_start__lte=today)
                & models.Q(consultation_end__gte=today)
            )
        ).exclude(published=True)


class Review(TimeStampedModel):

    STATUS = Choices(
        ("development", _("In review")),
        ("in_consultation", _("In Open consultation")),
        ("post_consultation", _("Post-consultation")),
        ("completed", _("Review Complete")),
    )

    TYPE = Choices(
        ("evidence", _("Evidence review")),
        ("map", _("Evidence map")),
        ("cost", _("Cost-effective model")),
        ("systematic", _("Systematic review")),
        ("other", _("Other")),
    )

    name = models.CharField(verbose_name=_("name"), max_length=100)
    slug = models.SlugField(verbose_name=_("slug"), max_length=100, unique=True)

    is_legacy = models.BooleanField(default=False)

    review_type = ArrayField(
        models.CharField(max_length=10, choices=TYPE),
        verbose_name=_("type of review"),
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

    summary = models.TextField(verbose_name=_("summary"), blank=True)
    summary_html = models.TextField(verbose_name=_("HTML summary"), blank=True)

    background = models.TextField(verbose_name=_("history"), blank=True)
    background_html = models.TextField(verbose_name=_("HTML history"), blank=True)

    stakeholders = models.ManyToManyField(Stakeholder, related_name="reviews")
    stakeholders_confirmed = models.BooleanField(default=False)

    open_consultation_notifications = models.ManyToManyField(
        Email, related_name="open_consultation_reviews", blank=True
    )

    decision_published_notifications = models.ManyToManyField(
        Email, related_name="publish_notification_reviews", blank=True
    )

    published = models.BooleanField(null=True, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
    )

    history = HistoricalRecords()
    objects = ReviewQuerySet.as_manager()

    class Meta:
        permissions = [
            ("evidence_review_manager", "Evidence Review Manager"),
        ]
        ordering = ("name", "pk")
        verbose_name_plural = _("reviews")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("review:detail", kwargs={"slug": self.slug})

    def get_review_type_display(self):
        return ", ".join(
            str(self.TYPE[getattr(self.TYPE, rt)]) for rt in self.review_type
        )

    def get_external_reviews(self):
        return Document.objects.for_review(self).external_reviews()

    @cached_property
    def external_review(self):
        return self.get_external_reviews().first()

    def get_submission_forms(self):
        return Document.objects.for_review(self).submission_forms()

    @cached_property
    def submission_form(self):
        return self.get_submission_forms().first()

    def get_cover_sheets(self):
        return Document.objects.for_review(self).cover_sheets()

    @cached_property
    def cover_sheet(self):
        return self.get_cover_sheets().first()

    def get_evidence_reviews(self):
        return Document.objects.for_review(self).evidence_reviews()

    @cached_property
    def evidence_review(self):
        return self.get_evidence_reviews().first()

    def get_cost_effective_models(self):
        return Document.objects.for_review(self).cost_effective_models()

    @cached_property
    def cost_effective_model(self):
        return self.get_cost_effective_models().first()

    def get_evidence_maps(self):
        return Document.objects.for_review(self).evidence_maps()

    @cached_property
    def evidence_map(self):
        return self.get_evidence_maps().first()

    def get_systematic_reviews(self):
        return Document.objects.for_review(self).systematic_reviews()

    @cached_property
    def systematic_review(self):
        return self.get_systematic_reviews().first()

    @cached_property
    def get_all_type_documents(self):
        return [
            *self.get_evidence_reviews(),
            *self.get_cost_effective_models(),
            *self.get_evidence_maps(),
            *self.get_systematic_reviews(),
            *self.get_other_review_documents(),
        ]

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
        return self.nsc_meeting_date.strftime("%B %Y")

    def summary_review_date_display(self):
        display_date = self.nsc_meeting_date or self.review_end

        if display_date:
            return display_date.strftime("%B %Y")
        else:
            return None

    def manager_display(self):
        return self.user.get_full_name() or self.user.username

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
        return self.published

    @cached_property
    def recommendation(self):
        review_recommendation = self.review_recommendations.first()
        if review_recommendation:
            return review_recommendation.recommendation
        return False

    def status(self):
        today = get_today()
        if self.has_supporting_documents() and self.has_summary():
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
        else:
            return self.STATUS.development

    def status_display(self):
        return self.STATUS[self.status()]

    def preparing(self):
        return self.status() == self.STATUS.development

    def in_consultation(self):
        return self.status() == self.STATUS.in_consultation

    def post_consultation(self):
        return self.status() == self.STATUS.post_consultation

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

    def get_email_context(self, **extra):

        formatted_start_date = (
            self.consultation_start.strftime("%d %B %Y")
            if self.consultation_start
            else ""
        )
        formatted_end_date = (
            self.consultation_end.strftime("%d %B %Y") if self.consultation_end else ""
        )
        return {
            "review": self.name,
            "policy list": "\n".join(
                f"* [{p.name}]({urljoin(settings.EMAIL_ROOT_DOMAIN, p.get_public_url())})"
                for p in self.policies.all()
            ),
            "review manager full name": self.user.get_full_name(),
            "consultation url": urljoin(
                settings.EMAIL_ROOT_DOMAIN, self.get_absolute_url()
            ),
            "consultation start date": formatted_start_date,
            "consultation end date": formatted_end_date,
            **extra,
        }

    def send_notifications(
        self, relation, stakeholder_template, comms_template, extra_context=None
    ):
        email_context = self.get_email_context(**(extra_context or {}))

        # Check if template is configured
        if not stakeholder_template:
            logger.error(
                "MISSING TEMPLATE: NOTIFY_TEMPLATE_DECISION_PUBLISHED is not set!"
            )
            return

        # find each stakeholder without a notification object and create one
        existing_notification_emails = relation.values_list("address", flat=True)
        contacts_to_email = (
            Contact.objects.with_email()
            .filter(stakeholder__in=self.stakeholders.all())
            .exclude(email__in=existing_notification_emails)
        )

        emails_created = Email.objects.bulk_create(
            Email(
                address=contact.email,
                template_id=stakeholder_template,
                context={"recipient name": contact.name, **email_context},
            )
            for contact in contacts_to_email
        )
        relation.add(*emails_created)

        logger.info(f"Created {len(emails_created)} stakeholder emails")

        if settings.PHE_COMMUNICATIONS_EMAIL not in existing_notification_emails:
            comms_email = Email.objects.create(
                address=settings.PHE_COMMUNICATIONS_EMAIL,
                template_id=comms_template,
                context={
                    "recipient name": settings.PHE_COMMUNICATIONS_NAME,
                    **email_context,
                },
            )
            relation.add(comms_email)
            logger.info("Created communications email")

    def send_open_consultation_notifications(self):
        self.send_notifications(
            self.open_consultation_notifications,
            settings.NOTIFY_TEMPLATE_CONSULTATION_OPEN,
            settings.NOTIFY_TEMPLATE_CONSULTATION_OPEN,
        )

        # send notifications to all subscribers to the conditions
        for policy in self.policies.all():
            policy.send_open_consultation_notifications(
                self.open_consultation_notifications,
                {
                    "review manager full name": self.user.get_full_name(),
                    "consultation end date": (
                        self.consultation_end.strftime("%d %B %Y")
                        if self.consultation_end
                        else ""
                    ),
                },
            )

    def send_decision_notifications(self):
        stakeholders = self.stakeholders.all()

        # Simple check: Do we have stakeholders?
        logger.info(f"Review '{self.name}' has {stakeholders.count()} stakeholders")
        if stakeholders.count() == 0:
            logger.warning(
                f"NO STAKEHOLDERS - No stakeholder emails will be sent for "
                f"'{self.name}'"
            )

        self.send_notifications(
            self.decision_published_notifications,
            settings.NOTIFY_TEMPLATE_DECISION_PUBLISHED,
            settings.NOTIFY_TEMPLATE_DECISION_PUBLISHED,
        )

        # send notifications to all subscribers to the conditions
        for policy in self.policies.all():
            subscribers = policy.subscriptions.all()
            logger.info(f"Policy '{policy.name}' has {subscribers.count()} subscribers")
            if subscribers.count() == 0:
                logger.warning(
                    f"NO SUBSCRIBERS - No subscriber emails will be sent for "
                    f"policy '{policy.name}'"
                )

            policy.send_decision_notifications(
                self.decision_published_notifications,
                {
                    "review manager full name": self.user.get_full_name(),
                    "consultation end date": (
                        self.consultation_end.strftime("%d %B %Y")
                        if self.consultation_end
                        else ""
                    ),
                },
            )

    @property
    def is_open(self):
        return self.review_start <= now().date()


class SummaryDraft(TimeStampedModel):
    text = models.TextField()
    policy = models.ForeignKey(
        "policy.Policy", on_delete=models.CASCADE, related_name="summary_drafts"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="summary_drafts"
    )
    updated = models.BooleanField(default=False)

    class Meta:
        unique_together = (("policy", "review"),)

    def __str__(self):
        return f"Plain English Summary for {self.policy} (review {self.review})."


class ReviewRecommendation(TimeStampedModel):
    recommendation = models.BooleanField(null=True, blank=True)
    policy = models.ForeignKey(
        "policy.Policy", on_delete=models.CASCADE, related_name="review_recommendations"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="review_recommendations"
    )

    class Meta:
        unique_together = (("policy", "review"),)

    def __str__(self):
        return f"Review recommendation for {self.policy} (review {self.review})."


@receiver(models.signals.post_delete, sender=Review)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    from nsc.document.models import document_path

    folder = document_path(instance)
    default_storage.delete(folder)
