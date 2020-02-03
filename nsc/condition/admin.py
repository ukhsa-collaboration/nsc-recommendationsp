from django.contrib import admin

from .filters import AgeGroupFilter
from .models import Condition


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):

    list_display = ('name', 'ages_display')
    list_filter = (AgeGroupFilter, )

    search_fields = ('name',)

    readonly_fields = ('slug', 'description_html', )
