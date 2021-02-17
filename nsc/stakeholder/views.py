import csv
from urllib.parse import urlencode

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.generic import FormView

from nsc.permissions import AdminRequiredMixin

from .filters import SearchFilter
from .forms import ExportForm, SearchForm, StakeholderForm
from .models import Stakeholder


class StakeholderFilterMixin:
    queryset = (
        Stakeholder.objects.all()
        .prefetch_related("policies", "contacts")
        .order_by("name")
    )

    def get_queryset(self):
        return SearchFilter(self.request.GET, queryset=self.queryset).qs


class StakeholderList(AdminRequiredMixin, StakeholderFilterMixin, generic.ListView):
    paginate_by = 20

    def get_context_data(self, **kwargs):
        form = SearchForm(initial=self.request.GET)
        return super().get_context_data(form=form)

    def get(self, *args, **kwargs):
        if self.request.GET.get("export"):
            return redirect(
                reverse("stakeholder:export") + "?" + urlencode(self.request.GET)
            )
        return super().get(*args, **kwargs)


class StakeholderExport(AdminRequiredMixin, StakeholderFilterMixin, FormView):
    form_class = ExportForm
    template_name = "stakeholder/stakeholder_export.html"

    def get_context_data(self, **kwargs):
        stakeholders = self.get_queryset()
        mailto = []
        for stakeholder in stakeholders:
            for email in stakeholder.contacts_emails():
                mailto.append(email)

        return super().get_context_data(
            total=Stakeholder.objects.count(),
            object_list=self.get_queryset(),
            mailto=",".join(mailto),
            **kwargs
        )

    def _as_individual_contact(self, writer):
        writer.writerow(
            [
                "Stakeholder name",
                "Contact Name",
                "Contact Email",
                "Contact Role",
                "Contact Phone",
            ]
        )
        for stakeholder in self.get_queryset():
            for contact in stakeholder.contacts.all():
                writer.writerow(
                    [
                        stakeholder.name,
                        contact.name,
                        contact.email,
                        contact.role,
                        contact.phone,
                    ]
                )

    def _as_conditions(self, writer):
        writer.writerow(
            [
                "Stakeholder name",
                "Contact Name",
                "Contact Email",
                "Contact Role",
                "Contact Phone",
            ]
        )
        for stakeholder in self.get_queryset():
            for contact in stakeholder.contacts.all():
                writer.writerow(
                    [
                        stakeholder.name,
                        contact.name,
                        contact.email,
                        contact.role,
                        contact.phone,
                    ]
                )

    def form_valid(self, form):
        """
        Export stakeholders - format depending on form.
        """
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="stakeholders.csv"'
        writer = csv.writer(response)

        if form.cleaned_data["export_type"] == "individual":
            self._as_individual_contact(writer)
        else:
            self._as_conditions(writer)

        return response


class StakeholderDetail(AdminRequiredMixin, generic.DetailView):
    model = Stakeholder

    def get_context_data(self, **kwargs):
        self.request.session["stakeholder"] = self.object.pk
        return super().get_context_data(**kwargs)


class StakeholderAdd(AdminRequiredMixin, generic.CreateView):
    model = Stakeholder
    form_class = StakeholderForm

    def get_success_url(self):
        return self.request.GET.get("next") or reverse(
            "stakeholder:detail", kwargs={"pk": self.object.pk}
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            back_title=_("Back to stakeholders"),
            back_url=reverse_lazy("stakeholder:list"),
            **kwargs
        )


class StakeholderEdit(AdminRequiredMixin, generic.UpdateView):
    model = Stakeholder
    form_class = StakeholderForm

    def get_success_url(self):
        return self.request.GET.get("next") or reverse(
            "stakeholder:detail", kwargs={"pk": self.object.pk}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["back_title"] = _("Back to %s" % self.object.name)
        context["back_url"] = self.get_success_url()
        return context


class StakeholderDelete(AdminRequiredMixin, generic.DeleteView):
    model = Stakeholder
    success_url = reverse_lazy("stakeholder:list")
