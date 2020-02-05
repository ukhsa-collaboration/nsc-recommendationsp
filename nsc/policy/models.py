from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from simple_history.models import HistoricalRecords

from nsc.utils.markdown import convert

from .fields import ChoiceArrayField


class PolicyManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)


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
    is_screened = models.BooleanField(verbose_name=_("is_screened"), default=False)

    ages = ChoiceArrayField(
        models.CharField(
            verbose_name=_("age groups"), choices=AGE_GROUPS, max_length=50
        )
    )

    condition = models.TextField(verbose_name=_("condition"))
    condition_html = models.TextField(verbose_name=_("HTML condition"))

    policy = models.TextField(verbose_name=_("policy"))
    policy_html = models.TextField(verbose_name=_("HTML policy"))

    history = HistoricalRecords()
    objects = PolicyManager()

    class Meta:
        ordering = ("name", "pk")
        verbose_name_plural = _("policies")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("policy:detail", kwargs={"slug": self.slug})

    def recommendation_display(self):
        return _("Recommended") if self.is_screened else _("Not recommended")

    def ages_display(self):
        return ", ".join(str(Policy.AGE_GROUPS[age]) for age in self.ages)

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.condition_html = convert(self.condition)
        self.policy_html = convert(self.policy)
        super().save(**kwargs)
