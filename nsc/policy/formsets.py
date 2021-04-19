from django.forms import formset_factory

from .forms import PolicySelectionForm


PolicySelectionFormset = formset_factory(
    PolicySelectionForm, min_num=1, extra=0, can_delete=False, validate_min=True
)
