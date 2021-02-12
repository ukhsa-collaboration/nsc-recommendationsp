from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from .filters import SearchFilter
from .forms import SearchForm, StakeholderForm
from .models import Stakeholder


class StakeholderList(generic.ListView):
    queryset = Stakeholder.objects.all().prefetch_related("policies").order_by("name")
    paginate_by = 20

    def get_queryset(self):
        return SearchFilter(self.request.GET, queryset=self.queryset).qs

    def get_context_data(self, **kwargs):
        form = SearchForm(initial=self.request.GET)
        return super().get_context_data(form=form)


class StakeholderDetail(generic.DetailView):
    model = Stakeholder

    def get_context_data(self, **kwargs):
        self.request.session["stakeholder"] = self.object.pk
        return super().get_context_data(**kwargs)


class StakeholderAdd(generic.CreateView):
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


class StakeholderEdit(generic.UpdateView):
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


class StakeholderDelete(generic.DeleteView):
    model = Stakeholder
    success_url = reverse_lazy("stakeholder:list")
