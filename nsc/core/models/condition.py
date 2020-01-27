from django.urls import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from nsc.core.fields import ChoiceArrayField


class Condition(TimeStampedModel):

    ANTENATAL = 'antenatal'
    NEWBORN = 'newborn'
    CHILD = 'child'
    ADULT = 'adult'
    ALL = 'all'

    AGE_GROUP_VALUES = (ANTENATAL, NEWBORN, CHILD, ADULT, ALL)

    AGE_GROUP_CHOICES = (
        (ANTENATAL, _('Antenatal')),
        (NEWBORN, _('Newborn')),
        (CHILD, _('Child')),
        (ADULT, _('Adult')),
        (ALL, _('All ages')),
    )

    AGE_GROUP_LOOKUP = {
        ANTENATAL: _('Antenatal'),
        NEWBORN: _('Newborn'),
        CHILD: _('Child'),
        ADULT: _('Adult'),
        ALL: _('All ages'),
    }

    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    is_active = models.BooleanField(default=True)
    is_screened = models.BooleanField(null=True, blank=True)
    ages = ChoiceArrayField(models.CharField(choices=AGE_GROUP_CHOICES, max_length=50))

    description = models.TextField()
    markup = models.TextField()

    history = HistoricalRecords()

    class Meta:
        ordering = ('name', 'pk', )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:condition:detail', args=[str(self.id)])
