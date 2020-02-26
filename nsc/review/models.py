from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from simple_history.models import HistoricalRecords

from nsc.organisation.models import Organisation


class ReviewQuerySet(models.QuerySet):
    def current(self):
        return self.filter(
            status__in=(
                Review.STATUS_CHOICES.pre_consultation,
                Review.STATUS_CHOICES.consultation,
                Review.STATUS_CHOICES.post_consultation,
            )
        )


class Review(TimeStampedModel):

    STATUS_CHOICES = Choices(
        ("pending", _("Due to be reviewed")),
        ("pre_consultation", _("Pre-consultation")),
        ("consultation", _("Consultation")),
        ("post_consultation", _("Post consultation")),
        ("completed", _("Completed")),
    )

    TYPE_CHOICES = Choices(("rapid", _("Rapid review")), ("other", _("Other")))

    name = models.CharField(verbose_name=_("name"), max_length=256)
    slug = models.SlugField(verbose_name=_("slug"), max_length=256, unique=True)
    status = models.CharField(
        verbose_name=_("status"),
        choices=STATUS_CHOICES,
        max_length=50,
        default=STATUS_CHOICES.pre_consultation,
    )
    review_type = models.CharField(
        verbose_name=_("type of review"), choices=TYPE_CHOICES, max_length=50
    )
    consultation_start = models.DateField(
        verbose_name=_("consultation start date"), null=True, blank=True
    )
    consultation_end = models.DateField(
        verbose_name=_("consultation end date"), null=True, blank=True
    )
    review_date = models.DateField(verbose_name=_("review date"), null=True, blank=True)

    recommendation = models.NullBooleanField(
        verbose_name=_("recommendation"), default=None
    )

    summary = models.TextField(verbose_name=_("summary"))
    summary_html = models.TextField(verbose_name=_("HTML summary"))

    policies = models.ManyToManyField(
        "policy.Policy", verbose_name=_("policies"), related_name="reviews"
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

    def clean(self):
        if not self.slug:
            self.slug = slugify(self.name)

    def policies_display(self):
        return mark_safe("<br/>".join([policy.name for policy in self.policies.all()]))

    def stakeholders(self):
        # ToDo this is just a way of generating data. It is nowhere close to
        # being correct.
        if self.policies:
            return self.policies.first().organisations.all()
        else:
            return Organisation.objects.none()
