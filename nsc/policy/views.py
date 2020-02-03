from django.views.generic import DetailView, ListView

from .filters import PolicyFilter
from .forms import PolicySearchForm
from .models import Policy


class PolicyList(ListView):
    queryset = Policy.objects.active()
    paginate_by = 20

    def get_queryset(self):
        return PolicyFilter(self.request.GET, queryset=self.queryset).qs

    def get_context_data(self, **kwargs):
        form = PolicySearchForm(initial=self.request.GET)
        return super().get_context_data(form=form)


class PolicyDetail(DetailView):
    model = Policy
    lookup_field = "slug"
