from django import forms
from django.forms import HiddenInput
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices

from nsc.policy.models import Policy


class SearchForm(forms.Form):

    name = forms.CharField(label=_("Condition name"), required=False)

    CONSULTATION = Choices(("open", _("Open")), ("closed", _("Closed")))

    comments = forms.TypedChoiceField(
        label=_("Public comments"),
        choices=CONSULTATION,
        widget=forms.RadioSelect,
        required=False,
    )

    affects = forms.TypedChoiceField(
        label=_("Who the condition affects"),
        choices=Policy.AGE_GROUPS,
        widget=forms.RadioSelect,
        required=False,
    )

    screen = forms.TypedChoiceField(
        label=_("Screening recommended"),
        choices=(("yes", _("Yes")), ("no", _("No"))),
        widget=forms.RadioSelect,
        required=False,
    )

    archived = forms.TypedChoiceField(
        label=_("Archive recommendations"),
        choices=(("yes", _("Yes")), ("no", _("No"))),
        widget=forms.CheckboxInput,
        required=False,
    )


class PublicCommentForm(forms.Form):

    name = forms.CharField(
        label=_("Full name"), error_messages={"required": _("Enter your full name.")}
    )
    email = forms.EmailField(
        label=_("Email address"),
        error_messages={
            "required": _("Enter your email address"),
            "invalid": _(
                "Enter an email address in the correct format, like name@example.com."
            ),
        },
    )
    publish = forms.TypedChoiceField(
        label=_("Do you consent to your name being published on the NSC web site?"),
        choices=((True, _("Yes")), (False, _("No"))),
        widget=forms.RadioSelect,
        error_messages={
            "required": _(
                "Select yes if you would like to shown as a contributor to this consultation."
            )
        },
    )
    notify = forms.TypedChoiceField(
        label=_(
            "Would you like to be updated when the UK NSC has reviewed the condition?"
        ),
        choices=((True, _("Yes")), (False, _("No"))),
        widget=forms.RadioSelect,
        error_messages={
            "required": _(
                "Select yes if you would to be notified when the NSC have completed the review."
            )
        },
    )
    comment = forms.CharField(
        label="",
        widget=forms.Textarea,
        error_messages={"required": _("Enter your comment")},
    )
    condition = forms.CharField(required=False, widget=HiddenInput)


class StakeholderCommentForm(forms.Form):

    name = forms.CharField(
        label=_("Full name"), error_messages={"required": _("Enter your full name.")}
    )
    email = forms.EmailField(
        label=_("Email address"),
        error_messages={
            "required": _("Enter your email address"),
            "invalid": _(
                "Enter an email address in the correct format, like name@example.com."
            ),
        },
    )
    organisation = forms.CharField(
        label=_("Organisation (if appropriate)"), required=False
    )
    role = forms.CharField(label=_("Role (if appropriate)"), required=False)
    publish = forms.TypedChoiceField(
        label=_("Do you consent to your name being published on the NSC web site?"),
        choices=((True, _("Yes")), (False, _("No"))),
        widget=forms.RadioSelect,
        error_messages={
            "required": _(
                "Select yes if you would like to shown as a contributor to this consultation."
            )
        },
    )
    comment = forms.CharField(
        label="",
        widget=forms.Textarea,
        error_messages={"required": _("Enter your comment")},
    )
    condition = forms.CharField(required=False, widget=HiddenInput)
