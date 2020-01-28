from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .filters import AgeGroupFilter
from .models import Condition, Policy


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):

    list_display = ('name', 'ages_display')
    list_filter = (AgeGroupFilter, )

    search_fields = ('name',)

    def ages_display(self, obj):
        return ', '.join(str(Condition.AGE_GROUPS[age]) for age in obj.ages)
    ages_display.short_description = _('Ages')


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):

    list_display = ('name', 'is_screened', 'is_active')
    list_filter = ('is_screened', 'is_active')

    search_fields = ('name',)
