from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .filters import AgeGroupFilter
from .models import Condition


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):

    list_display = ('name', 'is_screened', 'ages_display')
    list_filter = ('is_screened', AgeGroupFilter)

    search_fields = ('name',)

    def ages_display(self, obj):
        return ', '.join(str(Condition.AGE_GROUP_LOOKUP[age]) for age in obj.ages)
    ages_display.short_description = _('Ages')
