import markdown

from django.urls import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords


class PolicyManager(models.Manager):

    def active(self):
        return self.filter(is_active=True).select_related('condition')


class Policy(TimeStampedModel):

    name = models.CharField(verbose_name=_('name'), max_length=256)
    slug = models.SlugField(verbose_name=_('slug'), max_length=256, unique=True)

    is_active = models.BooleanField(verbose_name=_('is_active'), default=True)
    is_screened = models.BooleanField(verbose_name=_('is_screened'), default=False)

    description = models.TextField(verbose_name=_('description'))
    description_html = models.TextField(verbose_name=_('HTML description'))

    condition = models.OneToOneField(
        'condition.Condition', verbose_name=_('condition'), on_delete=models.PROTECT)

    history = HistoricalRecords()
    objects = PolicyManager()

    class Meta:
        ordering = ('name', 'pk', )
        verbose_name_plural = _('policies')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('policy:detail', kwargs={'slug': self.slug})

    @property
    def recommendation(self):
        return _('Recommended') if self.is_screened else _('Not recommended')

    def save(self, **kwargs):
        self.description_html = markdown.markdown(self.description, extensions=['attr_list'])
        super().save(**kwargs)
