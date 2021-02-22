from django import forms
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    name = forms.CharField(max_length=255)
    organisation = forms.CharField(
        max_length=255, required=False, label=_("Organisation (if any)")
    )
    role = forms.CharField(
        max_length=255,
        required=False,
        label=_("Your role (put 'member of the public' if appropriate)"),
    )
    region = forms.ChoiceField(
        choices=(
            ("", ""),
            ("North", "North"),
            ("Mids & East", "Mids & East"),
            ("London", "London"),
            ("South", "South"),
            ("National", "National"),
            ("Scotland", "Scotland"),
            ("Ireland", "Ireland"),
            ("Northern Ireland", "Northern Ireland"),
            ("Wales", "Wales"),
            ("International", "International"),
        ),
        required=True,
    )
    subject = forms.CharField(
        max_length=255, help_text=_("Please write what your email is about")
    )
    message = forms.CharField(widget=forms.TextInput)
    email = forms.EmailField()
