import datetime
import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields["name"].widget.attrs.update(
            {"class": "govuk-input", "style": "width: 80%"}
        )
        self.fields["status"].widget.attrs.update({"class": "govuk-radios__input"})
        self.fields["screen"].widget.attrs.update({"class": "govuk-radios__input"})


class PolicyForm(forms.ModelForm):

    next_review = forms.CharField(
        label=_(" Expected next review start date "), required=False
    )

    class Meta:
        model = Policy
        fields = ["next_review", "condition"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields["next_review"].help_text = _(
            "Enter the year in which the policy will be reviewed next"
        )
        self.fields["next_review"].widget.attrs.update(
            {
                "class": "govuk-input  govuk-input--width-4",
                "aria-describedby": "next-review-hint",
            }
        )

        if self.instance.next_review:
            self.initial["next_review"] = self.instance.next_review.year

        # Make the condition field optional so we can correctly report
        # validations errors using GDS markup and suppress errors being
        # reported in popovers.

        self.fields["condition"].required = False
        self.fields["condition"].label = _("More about %s" % self.instance.name)
        self.fields["condition"].help_text = _("Use markdown to format the text")
        self.fields["condition"].widget = forms.Textarea()
        self.fields["condition"].widget.attrs.update(
            {"class": "govuk-textarea", "aria-describedby": "condition-hint"}
        )

    def clean_next_review(self):
        value = self.cleaned_data["next_review"]

        if not value:
            return None

        if re.match(r"\d{4}", value) is None:
            raise ValidationError(_("Please enter a valid year"))

        value = int(value)

        if value < datetime.date.today().year:
            raise ValidationError(_("The next review cannot be in the past"))

        return datetime.date(year=value, month=1, day=1)

    def clean(self):
        data = self.cleaned_data

        if not data["condition"]:
            return self.add_error(
                "condition", _("The description of the condition cannot be empty")
            )

        return data
