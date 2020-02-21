from django.contrib import admin

from .models import Review


@admin.register(Review)
class PolicyAdmin(admin.ModelAdmin):

    list_display = ("name", "status")
    list_filter = ("status",)
    search_fields = ("name",)
    readonly_fields = ("slug",)
