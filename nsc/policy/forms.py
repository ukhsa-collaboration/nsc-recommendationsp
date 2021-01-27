import datetime
import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices

from nsc.utils.datetime import get_today

from .models import Policy


# TODO The SearchForm is currently identical to the one in condition/forms.py
#      check later once the development is finished to see if it can be shared.


class SearchForm(forms.Form):

    CONSULTATION = Choices(("open", _("Open")), ("closed", _("Closed")))
    YES_NO_CHOICES = Choices(("yes", _("Yes")), ("no", _("No")))

    name = forms.CharField(label=_("Condition name"), required=False)

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
        label=_("Current recommendation"),
        choices=YES_NO_CHOICES,
        widget=forms.RadioSelect,
        required=False,
    )


class PolicyForm(forms.ModelForm):

    next_review = forms.CharField(
        required=False,
        label=_("Expected next review start date"),
        help_text=_("Enter the year in which the policy will be reviewed next"),
    )
    condition = forms.CharField(
        required=True,
        label=_("Expected next review start date"),
        help_text=_("Use markdown to format the text"),
        widget=forms.Textarea,
    )
    keywords = forms.CharField(
        required=False,
        label=_("Search keywords"),
        help_text=_("Enter keywords which can help people find a condition."),
        error_messages={
            "required": _(
                "Enter keywords to make it easier for people to find a condition."
            )
        },
        widget=forms.Textarea,
    )
    summary = forms.CharField(
        required=True,
        label=_("Plain English summary"),
        help_text=_("Use markdown to format the text."),
        widget=forms.Textarea,
        error_messages={
            "required": _(
                "Enter a simple description of the condition that people would find easy to understand."
            )
        },
    )
    background = forms.CharField(
        required=True,
        label=_("Review history"),
        help_text=_("Use markdown to format the text"),
        widget=forms.Textarea,
        error_messages={
            "required": _("Enter a simple description of the review process.")
        },
    )

    class Meta:
        model = Policy
        fields = ["next_review", "condition", "keywords", "summary", "background"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.instance.next_review:
            self.initial["next_review"] = self.instance.next_review.year

        self.fields["condition"].label = _("More about %s" % self.instance.name)
        self.fields["keywords"].widget.attrs.update({"rows": 3})

    def clean_next_review(self):
        value = self.cleaned_data["next_review"]

        if not value:
            return None

        if re.match(r"\d{4}", value) is None:
            raise ValidationError(_("Please enter a valid year"))

        value = int(value)

        if value < get_today().year:
            raise ValidationError(_("The next review cannot be in the past"))

        return datetime.date(year=value, month=1, day=1)


class PolicySelectionForm(forms.Form):
    policy = forms.ModelChoiceField(Policy.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["policy"].widget.attrs.update({"class": "govuk-select"})
        self.fields["policy"].queryset = Policy.objects.all()
