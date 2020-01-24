from django import forms
from .models import Condition


class ConditionForm(forms.ModelForm):
    class Meta:
        model = Condition
        fields = ['name', ]
