from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = ("name", "recommendation")
    search_fields = ("name",)
    readonly_fields = ("slug", "summary_html")
