import datetime
import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices

from nsc.utils.datetime import get_today

from .models import Policy


class SearchForm(forms.Form):

    REVIEW_STATUS_CHOICES = Choices(
        ("due_for_review", _("Due to be reviewed")),
        ("in_review", _("In review")),
        ("in_consultation", _("In consultation")),
        ("post_consultation", _("Post consultation")),
    )

    YES_NO_CHOICES = Choices(("yes", _("Yes")), ("no", _("No")))

    name = forms.CharField(label=_("Search by condition name"), required=False)

    status = forms.TypedChoiceField(
        label=_("Status of the recommendation"),
        choices=REVIEW_STATUS_CHOICES,
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
        help_text=_("Enter keywords which can help people find a condition"),
        error_messages={
            "required": _(
                "Enter keywords to make it easier for people to find a condition"
            )
        },
        widget=forms.Textarea,
    )

    class Meta:
        model = Policy
        fields = ["next_review", "condition", "keywords"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.instance.next_review:
            self.initial["next_review"] = self.instance.next_review.year

        self.fields["condition"].label = _("More about %s" % self.instance.name)

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
