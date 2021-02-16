from django.urls import reverse
from django.views import generic

from nsc.permissions import AdminRequiredMixin
from nsc.stakeholder.models import Stakeholder

from .forms import ContactForm
from .models import Contact


class ContactAdd(AdminRequiredMixin, generic.CreateView):
    model = Contact
    form_class = ContactForm

    def get_success_url(self):
        return reverse("stakeholder:detail", kwargs={"pk": self.object.stakeholder.pk})

    def get_initial(self):
        initial = super().get_initial()

        if self.request.method == "GET":
            initial["stakeholder"] = Stakeholder.objects.get(pk=self.kwargs["org_pk"])

        return initial

    def get_context_data(self, **kwargs):
        stakeholder = Stakeholder.objects.get(pk=self.kwargs["org_pk"])
        return super().get_context_data(stakeholder=stakeholder, **kwargs)


class ContactEdit(AdminRequiredMixin, generic.UpdateView):
    model = Contact
    form_class = ContactForm

    def get_context_data(self, **kwargs):
        stakeholder = self.object.stakeholder
        return super().get_context_data(stakeholder=stakeholder, **kwargs)

    def get_success_url(self):
        return reverse("stakeholder:detail", kwargs={"pk": self.object.stakeholder.pk})


class ContactDelete(AdminRequiredMixin, generic.DeleteView):
    model = Contact

    def get_success_url(self):
        return reverse("stakeholder:detail", kwargs={"pk": self.object.stakeholder.pk})
