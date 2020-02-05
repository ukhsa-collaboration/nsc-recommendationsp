from django.urls import reverse
from django.views.generic import DetailView, ListView

from nsc.policy.models import Policy

from .filters import SearchFilter
from .forms import SearchForm


class ConditionList(ListView):
    template_name = "policy/public/policy_list.html"
    queryset = Policy.objects.active()
    paginate_by = 20

    def get_queryset(self):
        return SearchFilter(self.request.GET, queryset=self.queryset).qs

    def get_context_data(self, **kwargs):
        form = SearchForm(initial=self.request.GET)
        return super().get_context_data(form=form)


class ConditionDetail(DetailView):
    template_name = "policy/public/policy_detail.html"
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"

    def get_context_data(self, **kwargs):
        referer = self.request.META.get("HTTP_REFERER", reverse("condition:list"))
        return super().get_context_data(back_url=referer)
