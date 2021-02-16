from django import forms
from django.utils.translation import gettext_lazy as _

from ..policy.models import Policy
from .models import StakeholderSubscription, Subscription


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
        Policy.objects, widget=forms.CheckboxSelectMultiple(attrs={"hidden": True})
    )

    class Meta:
        model = Subscription
        fields = (
            "email",
            "policies",
        )

    def clean_policies(self):
        value = self.cleaned_data["policies"]

        if self.instance and self.instance.id:
            return [*value, *self.instance.policies.all()]

        return value

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data["email"] != cleaned_data["email_confirmation"]:
            self.add_error(
                "email_confirmation",
                _("Your email and email confirmation do not match"),
            )

        return cleaned_data


class CreateStakeholderSubscriptionForm(forms.ModelForm):
    email = forms.EmailField(label=_("Enter your email address"))
    email_confirmation = forms.EmailField(label=_("Re-enter your email address"))

    class Meta:
        model = StakeholderSubscription
        fields = (
            "title",
            "first_name",
            "last_name",
            "organisation",
            "email",
        )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data["email"] != cleaned_data["email_confirmation"]:
            self.add_error(
                "email_confirmation",
                _("Your email and email confirmation do not match"),
            )

        return cleaned_data
