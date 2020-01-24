from django.urls import reverse_lazy
from vanilla import ListView, CreateView, DetailView, UpdateView, DeleteView
from .forms import ConditionForm
from .models import Condition


class ConditionList(ListView):
    model = Condition
    paginate_by = 20


class ConditionCreate(CreateView):
    model = Condition
    form_class = ConditionForm
    success_url = reverse_lazy('core:condition:list')


class ConditionDetail(DetailView):
    model = Condition


class ConditionUpdate(UpdateView):
    model = Condition
    form_class = ConditionForm
    success_url = reverse_lazy('core:condition:list')


class ConditionDelete(DeleteView):
    model = Condition
    success_url = reverse_lazy('core:condition:list')
