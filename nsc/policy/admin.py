from django.contrib import admin

from .filters import AgeGroupFilter
from .models import Policy


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "ages_display",
        "recommendation",
        "last_review",
        "next_review",
        "is_active",
    )
    list_filter = (AgeGroupFilter, "recommendation", "is_active")
    search_fields = ("name",)

    readonly_fields = ("slug", "condition_html", "summary_html")
