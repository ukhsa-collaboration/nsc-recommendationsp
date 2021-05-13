from django import forms
from django.forms import HiddenInput
from django.utils.translation import gettext as _

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
        self.fields["email"].error_messages["invalid"] = _(
            "Enter an email address in the correct format, like name@example.com."
        )
        self.fields["phone"].widget.attrs.update({"class": "govuk-input"})
        self.fields["phone"].error_messages["invalid"] = _(
            "Enter a phone number in the correct format, like 01234567890."
        )

        if "stakeholder" in self.fields:
            self.fields["stakeholder"].widget = HiddenInput()
