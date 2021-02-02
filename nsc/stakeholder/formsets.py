from django.forms import formset_factory

from .forms import StakeholderSelectionForm


StakeholderSelectionFormset = formset_factory(
    StakeholderSelectionForm, min_num=1, extra=0, can_delete=False, validate_min=True
)
