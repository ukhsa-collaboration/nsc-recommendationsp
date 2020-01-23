from django.urls import reverse_lazy
from vanilla import ListView, CreateView, DetailView, UpdateView, DeleteView
from .forms import PolicyForm
from .models import Policy


class PolicyList(ListView):
    model = Policy
    paginate_by = 20


class PolicyCreate(CreateView):
    model = Policy
    form_class = PolicyForm
    success_url = reverse_lazy('policy:list')


class PolicyDetail(DetailView):
    model = Policy


class PolicyUpdate(UpdateView):
    model = Policy
    form_class = PolicyForm
    success_url = reverse_lazy('policy:list')


class PolicyDelete(DeleteView):
    model = Policy
    success_url = reverse_lazy('policy:list')
