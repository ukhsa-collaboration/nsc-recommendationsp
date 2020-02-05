from django.contrib import admin

from .filters import AgeGroupFilter
from .models import Policy


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):

    list_display = ("name", "ages_display", "is_screened", "is_active")
    list_filter = (AgeGroupFilter, "is_screened", "is_active")
    search_fields = ("name",)

    readonly_fields = ("slug", "condition_html", "policy_html")
