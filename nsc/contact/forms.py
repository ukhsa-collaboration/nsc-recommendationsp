from django import forms
from django.forms import HiddenInput

from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["name", "role", "email", "phone", "stakeholder"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].widget.attrs.update({"class": "govuk-input"})
        self.fields["role"].widget.attrs.update({"class": "govuk-input"})
        self.fields["email"].widget.attrs.update({"class": "govuk-input"})
        self.fields["phone"].widget.attrs.update({"class": "govuk-input"})

        if "stakeholder" in self.fields:
            self.fields["stakeholder"].widget = HiddenInput()
