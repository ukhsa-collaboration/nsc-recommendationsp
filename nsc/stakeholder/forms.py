from django import forms
from django.db import transaction
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from ..contact.formsets import ContactFormSet
from ..policy.formsets import PolicySelectionFormset
from .models import Stakeholder


class SearchForm(forms.Form):

    name = forms.CharField(label=_("Stakeholder name"), required=False)
    condition = forms.CharField(label=_("Condition of interest"), required=False)


class StakeholderForm(forms.ModelForm):
    """Form for adding and editing a Stakeholder.

    When the form is used for adding an Stakeholder all the fields are
    shown and the formsets for the related Contacts are set as an attribute.
    That simplifies the view code a lot.

    When editing an existing stakeholder the attributes are presented in a
    summary table where the user can edit the fields individually. The fields
    that are not being edited are hidden, except for fields showing the list
    of conditions which is deleted as there is no way to hide the list of
    checkboxes. The Contacts are added, edited or deleted individually so
    formsets are not needed.

    """

    is_public = forms.TypedChoiceField(
        label=_("Publish online"),
        help_text=_("Should this organisation be published on the condition pages?"),
        choices=(
            (True, _("Yes, publish this organisation online")),
            (False, _("No, do not show this organisation as a stakeholder publicly")),
        ),
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Stakeholder
        fields = ["name", "url", "is_public", "type", "twitter", "country", "comments"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields["url"].label = _("Website")

    def is_valid(self):
        formsets_valid = all([formset.is_valid() for formset in self.formsets])
        return super().is_valid() and formsets_valid

    @cached_property
    def policy_formset(self):
        return PolicySelectionFormset(
            self.data or None,
            prefix="policies",
            initial=(
                [
                    {"policy": p}
                    for p in self.instance.policies.values_list("id", flat=True)
                ]
                if self.instance.id
                else None
            ),
        )

    @cached_property
    def contact_formset(self):
        return ContactFormSet(
            self.data or None, instance=self.instance if self.instance.id else None
        )

    @cached_property
    def formsets(self):
        return [
            self.policy_formset,
            self.contact_formset,
        ]

    @transaction.atomic
    def save(self):
        stakeholder = super().save()
        stakeholder.policies.set(
            [entry["policy"] for entry in self.policy_formset.cleaned_data]
        )

        for contact in self.contact_formset.save(commit=False):
            contact.stakeholder = stakeholder
            contact.save()

        return stakeholder
