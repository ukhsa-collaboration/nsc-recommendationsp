from django import forms
from django.utils.translation import gettext_lazy as _

from ..policy.models import Policy
from .models import Subscription


class ManageSubscriptionsForm(forms.ModelForm):
    policies = forms.ModelMultipleChoiceField(
        Policy.objects, widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Subscription
        fields = ("policies",)


class SubscriptionStart(forms.Form):
    policies = forms.ModelMultipleChoiceField(
        Policy.objects, widget=forms.CheckboxSelectMultiple
    )


class CreateSubscriptionForm(ManageSubscriptionsForm):
    email_confirmation = forms.EmailField(label=_("Please confirm your email address"))
    email = forms.EmailField(label=_("What's your email address?"))
    policies = forms.ModelMultipleChoiceField(
        Policy.objects, widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Subscription
        fields = (
            "email",
            "policies",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["policies"].widget.attrs.update({"hidden": True})

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data["email"] != cleaned_data["email_confirmation"]:
            self.add_error(
                "email_confirmation",
                _("Your email and email confirmation do not match"),
            )

        return cleaned_data
