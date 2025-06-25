import os

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from notifications_python_client.errors import HTTPError

from nsc.mixins.notifymixin import Notify429ExceptionMixin

from ..notify.models import Email
from .forms import ContactForm


class ContactHelpDesk(Notify429ExceptionMixin, generic.FormView):
    form_class = ContactForm
    template_name = "support/contact_help_desk.html"

    def form_valid(self, form):
        if settings.DEBUG and simulate_429:
            print("Simulating 429 error in GET")
            response = type("obj", (object,), {"status_code": 429})()
            raise HTTPError(response=response)

        Email.objects.create(
            address=settings.PHE_HELP_DESK_EMAIL,
            template_id=settings.NOTIFY_TEMPLATE_HELP_DESK,
            context=form.cleaned_data,
        )
        Email.objects.create(
            address=form.cleaned_data["email"],
            template_id=settings.NOTIFY_TEMPLATE_HELP_DESK_CONFIRMATION,
            context=form.cleaned_data,
        )
        return HttpResponseRedirect(reverse("support:complete"))
