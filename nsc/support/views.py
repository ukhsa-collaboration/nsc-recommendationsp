from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic

from django_ratelimit.decorators import ratelimit

from ..notify.models import Email
from .forms import ContactForm


@method_decorator(
    ratelimit(key="ip", rate="3/h", method="POST", block=True), name="post"
)
@method_decorator(
    ratelimit(key="header:x-forwarded-for", rate="3/h", method="POST", block=True),
    name="post",
)
class ContactHelpDesk(generic.FormView):
    form_class = ContactForm
    template_name = "support/contact_help_desk.html"

    def form_valid(self, form):
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
