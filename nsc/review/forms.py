from datetime import date
from dateutil.relativedelta import relativedelta

from django import forms
from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices

from .models import Review
from ..organisation.models import Organisation
from ..policy.models import Policy


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


class ReviewForm(forms.ModelForm):

    review_type = forms.TypedChoiceField(
        label=_("What type of review is this?"),
        choices=Review.TYPE_CHOICES,
        widget=forms.RadioSelect,
    )

    policies = forms.ModelMultipleChoiceField(
        label=_("Conditions"),
        queryset=Policy.objects.active(),
        widget=forms.CheckboxSelectMultiple,
        help_text=_("Select all the conditions that will be included in this review"),
        required=False,
    )

    class Meta:
        model = Review
        fields = ["name", "review_type", "policies"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].label = _("Internal review name")
        self.fields["name"].help_text = _(
            "This will be produced automatically unless filled in specifically"
        )
        self.fields["name"].widget.attrs.update(
            {"class": "govuk-input govuk-input--width-30"}
        )

        self.fields["review_type"].label = _("What type of review is this?")
        self.fields["review_type"].widget.attrs.update({"class": "govuk-radios__input"})

        self.fields["policies"].widget.attrs.update(
            {"class": "govuk-checkboxes__input", "autofocus": "autofocus"}
        )

    def clean_name(self):
        name = self.cleaned_data["name"]
        slug = slugify(name)

        if Review.objects.filter(slug=slug).exists():
            raise ValidationError(_("A review with this name already exists"))

        return name


class ReviewDatesForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            "name",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].widget.attrs.update(
            {"class": "govuk-input govuk-input--width-30"}
        )


class ReviewOrganisationsForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            "name",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].widget.attrs.update(
            {"class": "govuk-input govuk-input--width-30"}
        )


class ReviewAddOrganisationForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            "name",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].widget.attrs.update(
            {"class": "govuk-input govuk-input--width-30"}
        )


class ReviewConsultationForm(forms.ModelForm):

    open_now = forms.TypedChoiceField(
        label=_("Do you want to open this consultation now?"),
        help_text=_(
            "It is possible to automatically open the consultation on a later pre-determined date"
        ),
        choices=Choices(
            (True, _("Yes, open this consultation now and notify the stakeholders")),
            (False, _("No, open this consultation on a later pre-determined date")),
        ),
        widget=forms.RadioSelect,
    )

    day = forms.IntegerField(label=_("Day"), required=False)
    month = forms.IntegerField(label=_("Month"), required=False)
    year = forms.IntegerField(label=_("Year"), required=False)

    class Meta:
        model = Review
        fields = ["consultation_start", "consultation_end"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["open_now"].widget.attrs.update({"class": "govuk-radios__input"})

        self.fields["year"].widget.attrs.update(
            {
                "class": "govuk-input govuk-date-input__input govuk-input--width-4",
                "pattern": "[0-9]*",
                "inputmode": "numeric",
            }
        )
        self.fields["month"].widget.attrs.update(
            {
                "class": "govuk-input govuk-date-input__input govuk-input--width-2",
                "pattern": "[0-9]*",
                "inputmode": "numeric",
            }
        )
        self.fields["day"].widget.attrs.update(
            {
                "class": "govuk-input govuk-date-input__input govuk-input--width-2",
                "pattern": "[0-9]*",
                "inputmode": "numeric",
            }
        )

    def clean(self):
        data = self.cleaned_data

        if data["open_now"]:
            start = date.today()
        else:
            start = date(data["year"], data["month"], data["day"])

        data["consultation_start"] = start

        if not data["consultation_end"]:
            data["consultation_end"] = start + relativedelta(months=+3)

        return data


class ReviewOrganisationsForm(forms.Form):

    organisations = forms.ModelMultipleChoiceField(
        label=_("Stakeholders"),
        queryset=Organisation.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        help_text=_(
            "Select the stakeholders who will be notified when the consultation opens"
        ),
    )

    def __init__(self, *args, **kwargs):
        review = kwargs.pop("instance")
        super().__init__(*args, **kwargs)

        self.fields["organisations"].queryset = review.stakeholders()
        self.fields["organisations"].widget.attrs.update(
            {"class": "govuk-checkboxes__input", "autofocus": "autofocus"}
        )


class ReviewRecommendationForm(forms.ModelForm):

    document = forms.FileField(label=_("Upload evidence document"), required=False)

    recommendation = forms.TypedChoiceField(
        label=_("What is the recommended decision for screening?"),
        choices=Choices((True, _("Recommened")), (False, _("Not recommended"))),
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Review
        fields = ["summary", "recommendation"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["recommendation"].widget.attrs.update(
            {"class": "govuk-radios__input"}
        )

        # Make the condition field optional so we can correctly report
        # validations errors using GDS markup and suppress errors being
        # reported in popovers.

        self.fields["summary"].required = False
        self.fields["summary"].label = _("Plain English evidence summary (optional)")
        self.fields["summary"].help_text = _("Use markdown to format the text")
        self.fields["summary"].widget = forms.Textarea()
        self.fields["summary"].widget.attrs.update(
            {"class": "govuk-textarea", "aria-describedby": "summary-hint"}
        )
