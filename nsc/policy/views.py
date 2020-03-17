from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, UpdateView

from django_filters.views import FilterView

from .filters import SearchFilter
from .forms import PolicyForm, SearchForm
from .models import Policy


class PolicyList(FilterView):
    queryset = Policy.objects.active()
    paginate_by = 20
    template_name = "policy/admin/policy_list.html"
    filterset_class = SearchFilter

    def get_context_data(self, **kwargs):
        # Setting the from on the filter does not quite work so we pass
        # it in explicitly, for now.
        form = SearchForm(initial=self.request.GET)
        return super().get_context_data(form=form)


class PolicyDetail(DetailView):
    model = Policy
    lookup_field = "slug"
    context_object_name = "policy"
    template_name = "policy/admin/policy_detail.html"


class PolicyEdit(UpdateView):
    model = Policy
    lookup_field = "slug"
    form_class = PolicyForm
    template_name = "policy/admin/policy_form.html"
    success_url = reverse_lazy("policy:list")

    def is_preview(self):
        return self.request.POST.get("preview")

    def is_publish(self):
        return self.request.POST.get("publish")

    def form_valid(self, form):
        if self.is_publish():
            msg = _("Published changes to conditions page for %s." % self.object.name)
            messages.info(self.request, msg)
            return super().form_valid(form=form)
        else:
            return self.render_to_response(
                self.get_context_data(form=form, preview=self.is_preview())
            )
