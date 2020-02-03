from django.urls import reverse
from django.views.generic import ListView, DetailView

from .filters import PolicyFilter
from .models import Policy
from .forms import PolicySearchForm


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
    lookup_field = 'slug'

    def get_context_data(self, **kwargs):
        referrer = self.request.META.get('HTTP_REFERER', reverse('policy:list'))
        return super().get_context_data(referrer=referrer)
