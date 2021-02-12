from django.db import models
from django.db.models import Prefetch, Q
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from dateutil.relativedelta import relativedelta
from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from simple_history.models import HistoricalRecords

from nsc.document.models import Document
from nsc.review.models import Review
from nsc.utils.datetime import get_today
from nsc.utils.markdown import convert

from .fields import ChoiceArrayField


class PolicyQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def overdue(self):
        """
        Get the policies where the next review is in the past.
        """
        return self.filter(Q(next_review__lt=get_today()) | Q(next_review__isnull=True))

    def upcoming(self):
        """
        Get the policies due for a review in the next 12 month, ordered by the
        next review date, soonest, first.
        """
        today = get_today()
        next_year = today + relativedelta(months=12)
        return self.filter(next_review__gte=today, next_review__lt=next_year)

    def search(self, keywords):
        return self.filter(
            Q(name__icontains=keywords) | Q(keywords__icontains=keywords)
        )

    def open_for_comments(self):
        """
        Get the policies which are currently in review and where the period for
        public comments is open.
        """
        today = get_today()
        return self.filter(
            reviews__consultation_start__lte=today, reviews__consultation_end__gte=today
        )

    def closed_for_comments(self):
        """
        Get the policies which are currently not open for public comments - either
        because they are not in review or in review but not in that particular phase.
        """
        today = get_today()
        return self.filter(
            ~(
                models.Q(reviews__consultation_start__lte=today)
                & models.Q(reviews__consultation_end__gte=today)
            )
        )

    def prefetch_reviews_in_consultation(self):
        """
        Get the list of Policies, pre-fetching any reviews that are currently open for comment.
        """
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

    name = models.CharField(verbose_name=_("name"), max_length=256)
    slug = models.SlugField(verbose_name=_("slug"), max_length=256, unique=True)

    is_active = models.BooleanField(verbose_name=_("is_active"), default=True)
    recommendation = models.BooleanField(
        verbose_name=_("recommendation"), default=False
    )

    last_review = models.DateField(verbose_name=_("last review"), null=True, blank=True)
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

    background = models.TextField(verbose_name=_("summary"))
    background_html = models.TextField(verbose_name=_("HTML summary"))

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

    def last_review_display(self):
        return (
            self.last_review.strftime("%B %Y")
            if self.last_review
            else _("This policy has not been reviewed")
        )

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

    def latest_review(self):
        return self.reviews.all().published().first()

    def get_archive_documents(self):
        return Document.objects.for_policy(self).archive()
