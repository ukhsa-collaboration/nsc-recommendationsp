from django import forms
from django.forms import HiddenInput
from django.utils.translation import gettext_lazy as _

from model_utils import Choices

from nsc.mixins.formmixin import BaseMixin
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


class PublicCommentForm(BaseMixin, forms.Form):
    COMMENT_FIELDS = {
        "comment_affected": "Please tell us if this condition has affected you, your family or your friends?",
        "comment_evidence": "Do you have any comments on the evidence considered by the UK NSC in the review? "
        "For instance, was any important evidence missed?",
        "comment_discussion": "Do you have any comments on the discussion, conclusion or recommendation in the review?",
        "comment_recommendation": "Do you think screening should or should not be recommended? Why?",
        "comment_alternatives": "There could be many alternatives to a screening programme. How else do you think "
        "the NHS or the government could help people with the condition?",
        "comment_other": "Do you have any other recommendations?",
    }

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
    condition = forms.CharField(required=False, widget=HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field, label in self.COMMENT_FIELDS.items():
            self.fields[field] = forms.CharField(
                label=label, widget=forms.Textarea, required=False
            )

    def clean(self):
        cleaned_data = super().clean()

        comment_valid = False
        for field in self.COMMENT_FIELDS.keys():
            if cleaned_data.get(field) != "":
                comment_valid = True
                break

        if not comment_valid:
            self.add_error(None, _("Please submit at least one comment."))

        return cleaned_data


class StakeholderCommentForm(BaseMixin, forms.Form):
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
    behalf = forms.TypedChoiceField(
        label=_(
            "Is your submission an official response on behalf of your organisation?"
        ),
        choices=((True, _("Yes")), (False, _("No"))),
        widget=forms.RadioSelect,
    )
    comment = forms.CharField(
        label="",
        widget=forms.Textarea,
        error_messages={"required": _("Enter your comment")},
    )
    condition = forms.CharField(required=False, widget=HiddenInput)
