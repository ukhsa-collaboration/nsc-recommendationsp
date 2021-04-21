from django import forms
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=255, error_messages={"required": _("Enter your name")}
    )
    organisation = forms.CharField(
        max_length=255, required=False, label=_("Organisation (if any)")
    )
    role = forms.CharField(
        max_length=255, required=False, label=_("Your role (if appropriate)"),
    )
    country = forms.ChoiceField(
        choices=(
            ("", ""),
            ("England", "England"),
            ("Wales", "Wales"),
            ("Scotland", "Scotland"),
            ("Northern Ireland", "Northern Ireland"),
            ("Other", "Other"),
        ),
        required=True,
        error_messages={"required": _("Select your country")},
    )
    subject = forms.CharField(
        max_length=255,
        help_text=_("Please write what your email is about"),
        error_messages={"required": _("Enter a subject for your enquiry")},
    )
    message = forms.CharField(
        widget=forms.TextInput, error_messages={"required": _("Enter a message")}
    )
    email = forms.EmailField(
        error_messages={
            "required": _("Entry your email address"),
            "invalid": _(
                "Enter your email address in the correct format, like name@example.com."
            ),
        }
    )
