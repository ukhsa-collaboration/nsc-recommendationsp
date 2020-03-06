from django import forms
from django.forms import HiddenInput
from django.utils.translation import ugettext_lazy as _

from nsc.policy.models import Policy


class SearchForm(forms.Form):

    name = forms.CharField(label=_("Search by condition name"), required=False)

    affects = forms.TypedChoiceField(
        label=_("Who the condition affects"),
        choices=Policy.AGE_GROUPS,
        widget=forms.RadioSelect,
        required=False,
    )

    screen = forms.TypedChoiceField(
        label=_("Current recommendation"),
        choices=(("yes", _("Yes")), ("no", _("No"))),
        widget=forms.RadioSelect,
        required=False,
    )


class SubmissionForm(forms.Form):

    name = forms.CharField(label=_("Name"))
    email = forms.EmailField(label=_("Email"))
    organisation = forms.CharField(
        label=_("Organisation (if appropriate)"), required=False
    )
    role = forms.CharField(label=_("Role (if appropriate)"), required=False)
    publish = forms.TypedChoiceField(
        label=_("Publish online"),
        help_text=_(
            "Do you consent to your name and organisation being published on the NSC web site?"
        ),
        choices=((True, _("Yes")), (False, _("No"))),
        widget=forms.RadioSelect,
    )
    comments = forms.CharField(required=False)

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.fields["name"].widget.attrs.update(
            {"class": "govuk-input govuk-input--width-30", "autofocus": "autofocus"}
        )

        self.fields["email"].widget.attrs.update(
            {"class": "govuk-input govuk-input--width-30"}
        )

        self.fields["organisation"].widget.attrs.update(
            {"class": "govuk-input govuk-input--width-30"}
        )

        self.fields["role"].widget.attrs.update(
            {"class": "govuk-input govuk-input--width-30"}
        )

        self.fields["publish"].widget.attrs.update({"class": "govuk-radios__input"})
        self.initial["publish"] = False

        self.fields["comments"].widget = forms.Textarea()
        self.fields["comments"].widget.attrs.update(
            {
                "class": "govuk-textarea govuk-js-character-count",
                "aria-describedby": "comments-hint",
            }
        )
