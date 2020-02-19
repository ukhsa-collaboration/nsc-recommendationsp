from django import forms
from django.db import transaction
from django.forms import HiddenInput
from django.utils.translation import ugettext_lazy as _

from nsc.policy.models import Policy

from .models import Organisation


class SearchForm(forms.Form):

    name = forms.CharField(label=_("Search by name"), required=False)
    condition = forms.CharField(label=_("Search by condition"), required=False)

    name.widget.attrs.update({"class": "govuk-input", "style": "width: 80%"})
    condition.widget.attrs.update({"class": "govuk-input", "style": "width: 80%"})


class OrganisationForm(forms.ModelForm):
    """Form for adding and editing and Organisation.

    When the form is used for adding an Organisation all the fields are
    shown and the formsets for the related Contacts are set as an attribute.
    That simplifies the view code a lot.

    When editing an existing organisation the attributes are presented in a
    summary table where the user can edit the fields individually. The fields
    that are not being edited are hidden, except for fields showing the list
    of conditions which is deleted as there is no way to hide the list of
    checkboxes. The Contacts are added, edited or deleted individually so
    formsets are not needed.

    """

    is_public = forms.TypedChoiceField(
        label=_("Publish online"),
        help_text=_(
            "Do you consent to your name and organisation being published on the NSC web site?"
        ),
        choices=((True, _("Yes")), (False, _("No"))),
        widget=forms.RadioSelect,
    )

    policies = forms.ModelMultipleChoiceField(
        label=_("Conditions"),
        queryset=Policy.objects.active(),
        widget=forms.CheckboxSelectMultiple,
        help_text=_("Select all the conditions that this stakeholder is interested in"),
        required=False,
    )

    class Meta:
        model = Organisation
        fields = ["name", "url", "is_public", "policies"]

    def __init__(self, **kwargs):
        show_field = kwargs.pop("field", None)
        self.formsets = kwargs.pop("formsets", [])

        super().__init__(**kwargs)

        self.fields["name"].widget.attrs.update(
            {"class": "govuk-input govuk-input--width-30", "autofocus": "autofocus"}
        )

        self.fields["url"].label = _("Web site")
        self.fields["url"].widget.attrs.update(
            {"class": "govuk-input govuk-input--width-30"}
        )

        self.fields["is_public"].widget.attrs.update({"class": "govuk-radios__input"})

        self.fields["policies"].widget.attrs.update(
            {"class": "govuk-checkboxes__input", "autofocus": "autofocus"}
        )

        self.initial["is_public"] = False

        if show_field:

            if show_field != "policies":
                del self.fields["policies"]

            for name, field in self.fields.items():
                if name == show_field:
                    field.widget.attrs.update({"autofocus": "autofocus"})
                else:
                    field.widget = HiddenInput()

    def is_valid(self):
        formsets_valid = all([formset.is_valid() for formset in self.formsets])
        return super().is_valid() and formsets_valid

    @transaction.atomic
    def save(self):
        organisation = super().save()
        for formset in self.formsets:
            for instance in formset.save(commit=False):
                instance.organisation = organisation
                instance.save()
        return organisation
