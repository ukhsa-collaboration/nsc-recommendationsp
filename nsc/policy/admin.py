from django.contrib import admin

from .models import Policy


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):

    list_display = ("name", "is_screened", "is_active")
    list_filter = ("is_screened", "is_active")

    search_fields = ("name",)
