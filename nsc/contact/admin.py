from django.contrib import admin

from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):

    list_display = ("name", "phone", "email", "stakeholder")
    search_fields = ("^name", "=phone", "email", "stakeholder__name")
