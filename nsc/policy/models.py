from django.urls import reverse
from django.db import models


class Policy(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name', 'pk', )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('policy:detail', args=[str(self.id)])
