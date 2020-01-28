from django.urls import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords


class Policy(TimeStampedModel):

    name = models.CharField(verbose_name=_('name'), max_length=256)
    slug = models.SlugField(verbose_name=_('slug'), max_length=256, unique=True)

    is_active = models.BooleanField(verbose_name=_('is_active'), default=True)
    is_screened = models.BooleanField(verbose_name=_('is_screened'), null=True, blank=True)

    description = models.TextField(verbose_name=_('description'))
    markup = models.TextField(verbose_name=_('markup'))

    condition = models.OneToOneField(
        'core.Condition', verbose_name=_('condition'), on_delete=models.PROTECT)

    history = HistoricalRecords()

    class Meta:
        ordering = ('name', 'pk', )
        verbose_name_plural = _('policies')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:condition:detail', args=[str(self.id)])
