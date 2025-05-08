from urllib.parse import urljoin

from django.apps import apps
from django.conf import settings
from django.db import models
from django.db.models import Prefetch, Q
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from dateutil.relativedelta import relativedelta
from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from simple_history.models import HistoricalRecords

from nsc.document.models import Document
from nsc.notify.models import Email
from nsc.review.models import Review
from nsc.utils.datetime import get_today
from nsc.utils.forms import ChoiceArrayField
from nsc.utils.markdown import convert


class PolicyQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def overdue(self):
        return self.filter(Q(next_review__lt=get_today()) | Q(next_review__isnull=True))

    def upcoming(self):
        today = get_today()
        next_year = today + relativedelta(months=12)
        return self.filter(next_review__gte=today, next_review__lt=next_year)

    def search(self, keywords):
        return self.filter(
            Q(name__icontains=keywords) | Q(keywords__icontains=keywords)
        )

    def in_progress(self):
        return self.exclude(reviews__published=True)

    def open_for_comments(self):
        review_model = apps.get_model(app_label="review", model_name="Review")
        return self.filter(
            reviews__in=review_model.objects.open_for_comments()
        ).distinct()

    def closed_for_comments(self):
        review_model = apps.get_model(app_label="review", model_name="Review")
        return self.filter(
            reviews__in=review_model.objects.closed_for_comments()
        ).distinct()

    def prefetch_reviews_in_consultation(self):
        return self.prefetch_related(
            Prefetch(
                "reviews",
                queryset=Review.objects.open_for_comments(),
                to_attr="reviews_in_consultation",
            )
        )

    def exclude_archived(self):
        return self.filter(archived=False)


class Policy(TimeStampedModel):

    AGE_GROUPS = Choices(
        ("antenatal", _("Antenatal")),
        ("newborn", _("Newborn")),
        ("child", _("Child")),
        ("adult", _("Adult")),
        ("all", _("All ages")),
    )

    CONDITION_TYPES = Choices(
        ("general", _("General Population")),
        ("targeted", _("Targeted")),
    )

    name = models.CharField(verbose_name=_("name"), max_length=100)
    slug = models.SlugField(verbose_name=_("slug"), max_length=100, unique=True)
    condition_type = models.CharField(choices=CONDITION_TYPES, max_length=8, null=True)

    is_active = models.BooleanField(verbose_name=_("is_active"), default=True)
    recommendation = models.BooleanField(
        verbose_name=_("recommendation"), null=True, default=None
    )

    next_review = models.DateField(verbose_name=_("next review"), null=True, blank=True)

    ages = ChoiceArrayField(
        models.CharField(
            verbose_name=_("age groups"), choices=AGE_GROUPS, max_length=50
        )
    )

    condition = models.TextField(verbose_name=_("condition name"))
    condition_html = models.TextField(verbose_name=_("HTML condition"))

    summary = models.TextField(verbose_name=_("summary"))
    summary_html = models.TextField(verbose_name=_("HTML summary"))

    background = models.TextField(verbose_name=_("background"))
    background_html = models.TextField(verbose_name=_("HTML background"))

    keywords = models.TextField(
        verbose_name=_("Search keywords"), blank=True, default=""
    )

    archived = models.BooleanField(default=False)
    archived_reason = models.TextField(verbose_name=_("Archived Reason"), blank=True)
    archived_reason_html = models.TextField(
        verbose_name=_("HTML Archived Reason"), blank=True
    )

    reviews = models.ManyToManyField(
        "review.Review", verbose_name=_("reviews"), related_name="policies"
    )

    history = HistoricalRecords()
    objects = PolicyQuerySet.as_manager()

    class Meta:
        ordering = ("name", "pk")
        verbose_name_plural = _("policies")

    def __str__(self):
        return self.name

    def get_public_url(self):
        return reverse("condition:detail", kwargs={"slug": self.slug})

    def get_admin_url(self):
        return reverse("policy:detail", kwargs={"slug": self.slug})

    def get_edit_url(self):
        return reverse("policy:edit", kwargs={"slug": self.slug})

    def recommendation_display(self):
        if self.archived:
            return _("Archived")
        return _("Recommended") if self.recommendation else _("Not recommended")

    def next_review_display(self):
        today = get_today()
        if self.next_review is None:
            return _("No review has been scheduled")
        if self.next_review < today:
            return _("Overdue")
        else:
            return self.next_review.strftime("%B %Y")

    def ages_display(self):
        return ", ".join(str(Policy.AGE_GROUPS[age]) for age in self.ages)

    def clean(self):
        if not self.slug:
            self.slug = slugify(self.name)
        self.condition_html = convert(self.condition)
        self.summary_html = convert(self.summary)
        self.background_html = convert(self.background)
        self.archived_reason_html = convert(self.archived_reason)

    @cached_property
    def current_review(self):
        return self.reviews.in_progress().first()

    @cached_property
    def latest_review(self):
        return self.reviews.published().first()

    @cached_property
    def reviews_for_public_documents(self):
        limit = 2
        if self.current_review and self.current_review.in_consultation():
            limit = 1
        return self.reviews.published()[:limit]

    def get_archive_documents(self):
        return Document.objects.for_policy(self).archive()

    def get_ages_display(self):
        return ", ".join(map(lambda a: str(self.AGE_GROUPS[a]), self.ages))

    def get_email_context(self, **extra):
        return {
            "policy url": urljoin(settings.EMAIL_ROOT_DOMAIN, self.get_public_url()),
            "policy": self.name,
            **extra,
        }

    def send_notifications(self, relation, template, extra_context=None):
        email_context = self.get_email_context(**(extra_context or {}))

        existing_notification_emails = relation.values_list("address", flat=True)
        relation.add(
            *Email.objects.bulk_create(
                Email(
                    address=sub.email,
                    template_id=template,
                    context={
                        **email_context,
                        "manage subscription url": urljoin(
                            settings.EMAIL_ROOT_DOMAIN, sub.management_url
                        ),
                        "subscribe url": urljoin(
                            settings.EMAIL_ROOT_DOMAIN,
                            reverse("subscription:public-start"),
                        ),
                    },
                )
                for sub in self.subscriptions.all().exclude(
                    email__in=existing_notification_emails
                )
            )
        )

    def send_open_consultation_notifications(
        self, review_notification_relation, extra_context
    ):
        self.send_notifications(
            review_notification_relation,
            settings.NOTIFY_TEMPLATE_SUBSCRIBER_CONSULTATION_OPEN,
            extra_context,
        )

    def send_decision_notifications(self, review_notification_relation, extra_context):
        self.send_notifications(
            review_notification_relation,
            settings.NOTIFY_TEMPLATE_SUBSCRIBER_DECISION_PUBLISHED,
            extra_context,
        )
