from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView

from .filters import SearchFilter
from .forms import PolicyForm, SearchForm
from .models import Policy


class PolicyList(ListView):
    queryset = Policy.objects.active()
    paginate_by = 20
    template_name = "policy/admin/policy_list.html"

    def get_queryset(self):
        return SearchFilter(self.request.GET, queryset=self.queryset).qs

    def get_context_data(self, **kwargs):
        form = SearchForm(initial=self.request.GET)
        return super().get_context_data(form=form)


class PolicyDetail(DetailView):
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"
    template_name = "policy/admin/policy_detail.html"

    def get_context_data(self, **kwargs):
        referer = self.request.META.get("HTTP_REFERER", reverse("policy:list"))
        return super().get_context_data(back_url=referer)


class PolicyEdit(UpdateView):
    model = Policy
    lookup_field = "slug"
    form_class = PolicyForm
    success_url = reverse_lazy("policy:list")
    template_name = "policy/admin/policy_form.html"

    def is_preview(self):
        return self.request.POST.get("preview")

    def get_context_data(self, **kwargs):
        referer = self.request.META.get("HTTP_REFERER", reverse("policy:list"))
        return super().get_context_data(back_url=referer, **kwargs)

    def form_valid(self, form):
        if self.is_preview():
            return self.render_to_response(
                self.get_context_data(form=form, preview=True)
            )
        else:
            return super().form_valid(form=form)
