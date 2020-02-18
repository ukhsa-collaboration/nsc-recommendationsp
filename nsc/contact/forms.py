from django import forms
from django.forms import HiddenInput

from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["name", "email", "phone", "organisation"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].widget.attrs.update(
            {"class": "govuk-input govuk-input--width-30"}
        )
        self.fields["email"].widget.attrs.update(
            {"class": "govuk-input govuk-input--width-30"}
        )
        self.fields["phone"].widget.attrs.update(
            {"class": "govuk-input govuk-input--width-20"}
        )

        if "organisation" in self.fields:
            self.fields["organisation"].widget = HiddenInput()
