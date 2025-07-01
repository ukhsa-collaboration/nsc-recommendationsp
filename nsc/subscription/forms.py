from itertools import chain

from django import forms
from django.core.paginator import EmptyPage, Paginator
from django.forms.forms import DeclarativeFieldsMetaclass
from django.utils.translation import gettext_lazy as _

from nsc.mixins.formmixin import BaseMixin

from ..policy.filters import SearchFilter
from ..policy.models import Policy
from .models import StakeholderSubscription, Subscription


class SubscriptionPolicySearchFormMixin(metaclass=DeclarativeFieldsMetaclass):
    PAGE_SIZE = 15

    hidden_policies = forms.ModelMultipleChoiceField(
        Policy.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )
    policies = forms.ModelMultipleChoiceField(
        Policy.objects, widget=forms.CheckboxSelectMultiple, required=False
    )

    def __init__(self, *args, data=None, **kwargs):
        instance = kwargs.get("instance")

        if data and "clear-search" in data:
            self.search_filter = SearchFilter(queryset=Policy.objects.all())
        else:
            self.search_filter = SearchFilter(data=data, queryset=Policy.objects.all())

        self.paginator = Paginator(self.search_filter.qs, self.PAGE_SIZE)
        if data and "page" in data:
            try:
                self.page = self.paginator.page(int(data["page"]))
            except (EmptyPage, ValueError):
                self.page = self.paginator.page(1)
        else:
            self.page = self.paginator.page(1)

        visible_policy_ids = [str(p.id) for p in self.page.object_list]
        hidden_policy_ids = []

        if data:
            data = data.copy()

            if "policies" in data or "hidden_policies" in data:
                selected_policies = [
                    str(p)
                    for p in chain(
                        data.getlist("policies", []),
                        data.getlist("hidden_policies", []),
                    )
                ]
            elif instance and instance.pk:
                selected_policies = [
                    str(p) for p in instance.policies.values_list("id", flat=True)
                ]
            else:
                selected_policies = []

            data.setlist(
                "policies",
                [p for p in selected_policies if str(p) in visible_policy_ids],
            )

            hidden_policy_ids = [
                p for p in selected_policies if str(p) not in visible_policy_ids
            ]
            data.setlist("hidden_policies", hidden_policy_ids)

        super().__init__(*args, data=data, **kwargs)

        self.fields["policies"].queryset = Policy.objects.filter(
            id__in=visible_policy_ids
        )
        self.fields["hidden_policies"].queryset = Policy.objects.filter(
            id__in=hidden_policy_ids
        )

    def clean(self):
        cleaned_data = super().clean()

        if "save" not in self.data:
            return cleaned_data

        if not cleaned_data.get("policies") and not cleaned_data.get("hidden_policies"):
            self.add_error(None, _("At least 1 condition must be selected"))

        return cleaned_data

    def is_valid(self):
        search_form_valid = self.search_filter.is_valid()
        return super().is_valid() and search_form_valid


class ManageSubscriptionsForm(SubscriptionPolicySearchFormMixin, forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ("policies",)


class SubscriptionStart(SubscriptionPolicySearchFormMixin, forms.Form):
    pass


class CreateSubscriptionForm(BaseMixin, forms.ModelForm):
    email_confirmation = forms.EmailField(
        label=_("Please confirm your email address"),
        error_messages={"required": _("Confirm your email address")},
    )
    email = forms.EmailField(
        label=_("What's your email address?"),
        error_messages={"required": _("Enter your email address")},
    )
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

        if cleaned_data.get("email") != cleaned_data.get("email_confirmation"):
            self.add_error(
                "email_confirmation",
                _("Your email and email confirmation do not match"),
            )

        return cleaned_data


class CreateStakeholderSubscriptionForm(forms.ModelForm):
    email = forms.EmailField(
        label=_("Enter your email address"),
        error_messages={"required": _("Enter your email address")},
    )
    email_confirmation = forms.EmailField(
        label=_("Re-enter your email address"),
        error_messages={"required": _("Confirm your email address")},
    )

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

        if cleaned_data.get("email") != cleaned_data.get("email_confirmation"):
            self.add_error(
                "email_confirmation",
                _("Your email and email confirmation do not match"),
            )

        return cleaned_data
