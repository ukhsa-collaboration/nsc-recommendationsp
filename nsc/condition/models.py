import markdown

from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from model_utils import Choices
from simple_history.models import HistoricalRecords

from nsc.condition.fields import ChoiceArrayField


class Condition(TimeStampedModel):

    AGE_GROUPS = Choices(
        ('antenatal', _('Antenatal')),
        ('newborn', _('Newborn')),
        ('child', _('Child')),
        ('adult', _('Adult')),
        ('all', _('All ages')),
    )

    name = models.CharField(verbose_name=_('name'), max_length=256)
    slug = models.SlugField(verbose_name=_('slug'), max_length=256, unique=True)

    ages = ChoiceArrayField(models.CharField(
        verbose_name=_('age groups'), choices=AGE_GROUPS, max_length=50))

    description = models.TextField(verbose_name=_('description'))
    description_html = models.TextField(verbose_name=_('HTML description'))

    history = HistoricalRecords()

    class Meta:
        ordering = ('name', 'pk', )

    def __str__(self):
        return self.name

    def ages_display(self):
        return ', '.join(str(Condition.AGE_GROUPS[age]) for age in self.ages)

    def save(self, **kwargs):
        self.description_html = markdown.markdown(self.description, extensions=['attr_list'])
        super().save(**kwargs)
