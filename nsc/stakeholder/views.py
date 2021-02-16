from urllib.parse import urlencode

from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from nsc.permissions import AdminRequiredMixin

from .filters import SearchFilter
from .forms import ExportForm, SearchForm, StakeholderForm
from .models import Stakeholder


class StakeholderList(AdminRequiredMixin, generic.ListView):
    queryset = (
        Stakeholder.objects.all()
        .prefetch_related("policies", "contacts")
        .order_by("name")
    )
    paginate_by = 20

    def get_queryset(self):
        return SearchFilter(self.request.GET, queryset=self.queryset).qs

    def get_context_data(self, **kwargs):
        form = SearchForm(initial=self.request.GET)
        return super().get_context_data(form=form)

    def get(self, *args, **kwargs):
        if self.request.GET.get("export"):
            params = self.request.GET.copy()
            params.pop("export")
            return redirect(reverse("stakeholder:export") + "?" + urlencode(params))
        return super().get(*args, **kwargs)


class StakeholderExport(StakeholderList):
    template_name = "stakeholder/stakeholder_export.html"
    paginate_by = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["form"] = ExportForm(initial=self.request.GET)
        context["total"] = Stakeholder.objects.all().count()

        mailto = []
        for stakeholder in context["object_list"]:
            for email in stakeholder.contacts_emails():
                mailto.append(email)

        context["mailto"] = ",".join(mailto)

        return context


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
