from distutils.util import strtobool

from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from dateutil.relativedelta import relativedelta
from model_utils import Choices

from nsc.utils.datetime import get_today

from ..organisation.models import Organisation
from ..policy.models import Policy
from .models import Review


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


class ReviewForm(forms.ModelForm):

    review_type = forms.TypedChoiceField(
        label=_("What type of review is this?"),
        choices=Review.TYPE,
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
        self.fields["review_type"].label = _("What type of review is this?")

    def clean_name(self):
        name = self.cleaned_data["name"]
        slug = slugify(name)

        if Review.objects.filter(slug=slug).exists():
            raise ValidationError(_("A review with this name already exists"))

        return name


class ReviewConsultationForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["name"]


class ReviewAddOrganisationForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["name"]


class ReviewDatesForm(forms.ModelForm):

    consultation_open = forms.TypedChoiceField(
        label=_("Consultation open date"),
        help_text=_("When do you want to open this consultation?"),
        choices=Choices(
            (True, _("Now - open this consultation and email {} stakeholders")),
            (
                False,
                _("Schedule this consultation to automatically open on a later date"),
            ),
        ),
        widget=forms.RadioSelect,
        required=False,
    )

    consultation_start = forms.DateField(
        label=_(""), help_text=_(""), widget=forms.HiddenInput(), required=False
    )

    consultation_start_day = forms.IntegerField(label=_("Day"), required=False)
    consultation_start_month = forms.IntegerField(label=_("Month"), required=False)
    consultation_start_year = forms.IntegerField(label=_("Year"), required=False)

    consultation_end = forms.DateField(
        label=_("Consultation end date"),
        help_text=_(
            "The consultation will automatically close 3 months after it is opened "
            "unless you specify a different date."
        ),
        widget=forms.HiddenInput(),
        required=False,
    )

    consultation_end_day = forms.IntegerField(label=_("Day"), required=False)
    consultation_end_month = forms.IntegerField(label=_("Month"), required=False)
    consultation_end_year = forms.IntegerField(label=_("Year"), required=False)

    nsc_meeting_date = forms.DateField(
        label=_("UK NSC meeting date"),
        help_text=mark_safe(
            _(
                "Select the date of the UK NSC meeting when this consultation will be discussed. "
                'View <a href="https://www.gov.uk/government/groups/uk-national-screening-'
                'committee-uk-nsc#meetings">spreadsheet of meeting dates</a> for reference.'
            )
        ),
        widget=forms.HiddenInput(),
        required=False,
    )

    nsc_meeting_date_day = forms.IntegerField(label=_("Day"), required=False)
    nsc_meeting_date_month = forms.IntegerField(label=_("Month"), required=False)
    nsc_meeting_date_year = forms.IntegerField(label=_("Year"), required=False)

    class Meta:
        model = Review
        fields = ["consultation_start", "consultation_end", "nsc_meeting_date"]

    def clean_consultation_open(self):
        value = self.cleaned_data["consultation_open"]
        return strtobool(value) if value else None

    def clean(self):
        data = self.cleaned_data

        consultation_open = data.get("consultation_open", None)

        if consultation_open:
            date = get_today()
            data["consultation_start_day"] = date.day
            data["consultation_start_month"] = date.month
            data["consultation_start_year"] = date.year

            day = data.get("consultation_end_day", None)
            month = data.get("consultation_end_month", None)
            year = data.get("consultation_end_year", None)

            if not (day or month or year):
                date = get_today() + relativedelta(months=+3)
                data["consultation_end_day"] = date.day
                data["consultation_end_month"] = date.month
                data["consultation_end_year"] = date.year

        day = data["consultation_start_day"]
        month = data["consultation_start_month"]
        year = data["consultation_start_year"]

        if day is not None or month is not None or year is not None:
            if day is None:
                self.add_error(
                    "consultation_start_day",
                    _("Enter the day for the consultation start date"),
                )
            if month is None:
                self.add_error(
                    "consultation_start_month",
                    _("Enter the month for the consultation start date"),
                )
            if year is None:
                self.add_error(
                    "consultation_start_year",
                    _("Enter the year for the consultation start date"),
                )

        if day is not None and month is not None and year is not None:
            try:
                data["consultation_start"] = get_today().replace(
                    year=year, month=month, day=day
                )
            except ValueError:
                self.add_error(
                    "consultation_end",
                    _(
                        "Enter a correct date for the opening of the consultation period"
                    ),
                )

        if day is None and month is None and year is None:
            data["consultation_start"] = None

        day = data.get("consultation_end_day", None)
        month = data.get("consultation_end_month", None)
        year = data.get("consultation_end_year", None)

        if day is not None or month is not None or year is not None:
            if day is None:
                self.add_error(
                    "consultation_end_day",
                    _("Enter the day for the consultation end date"),
                )
            if month is None:
                self.add_error(
                    "consultation_end_month",
                    _("Enter the month for the consultation end date"),
                )
            if year is None:
                self.add_error(
                    "consultation_end_year",
                    _("Enter the year for the consultation end date"),
                )

        if day is not None and month is not None and year is not None:
            try:
                data["consultation_end"] = get_today().replace(
                    year=year, month=month, day=day
                )
            except ValueError:
                self.add_error(
                    "consultation_end",
                    _(
                        "Enter a correct date for the closing of the consultation period"
                    ),
                )

        if day is None and month is None and year is None:
            data["consultation_end"] = None

        day = data.get("nsc_meeting_date_day", None)
        month = data.get("nsc_meeting_date_month", None)
        year = data.get("nsc_meeting_date_year", None)

        if day is not None or month is not None or year is not None:
            if day is None:
                self.add_error(
                    "nsc_meeting_date_day",
                    _("Enter the day the NSC Meeting takes place"),
                )
            if month is None:
                self.add_error(
                    "nsc_meeting_date_month",
                    _("Enter the month the NSC Meeting takes place"),
                )
            if year is None:
                self.add_error(
                    "nsc_meeting_date_year",
                    _("Enter the year the NSC Meeting takes place"),
                )

        if day is not None and month is not None and year is not None:
            try:
                data["nsc_meeting_date"] = get_today().replace(
                    year=year, month=month, day=day
                )
            except ValueError:
                self.add_error(
                    "nsc_meeting_date", _("Enter a correct date for the NSC Meeting")
                )

        if day is None and month is None and year is None:
            data["nsc_meeting_date"] = None

        if "consultation_start" in data and "consultation_end" in data:

            if bool(data["consultation_start"]) != bool(data["consultation_end"]):
                if data["consultation_start"]:
                    self.add_error(
                        "consultation_end",
                        _("Enter the date the consultation period closes"),
                    )
                else:
                    self.add_error(
                        "consultation_start",
                        _("Enter the date the consultation period opens"),
                    )

        if data.get("consultation_start", False) and data.get(
            "consultation_end", False
        ):
            if data["consultation_end"] < data["consultation_start"]:
                self.add_error(
                    "consultation_end",
                    _(
                        "Enter a consultation end date which is after the consultation start."
                    ),
                )

        if data.get("consultation_end", False) and data.get("nsc_meeting_date", False):
            if data["nsc_meeting_date"] < data["consultation_end"]:
                self.add_error(
                    "nsc_meeting_date",
                    _(
                        "Enter a date for the NSC meeting which is after the consultation end."
                    ),
                )

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

    def clean(self):
        self.add_error(None, "TEST")


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

        # Make the condition field optional so we can correctly report
        # validations errors using GDS markup and suppress errors being
        # reported in popovers.

        self.fields["summary"].required = False
        self.fields["summary"].label = _("Plain English evidence summary (optional)")
        self.fields["summary"].help_text = _("Use markdown to format the text")
        self.fields["summary"].widget = forms.Textarea()
