from django.contrib import admin

from .models import Stakeholder


@admin.register(Stakeholder)
class StakeholderAdmin(admin.ModelAdmin):

    list_display = ("name",)
    search_fields = ("name", "policies__name")
