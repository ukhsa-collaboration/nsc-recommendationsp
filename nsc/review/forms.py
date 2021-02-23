from distutils.util import strtobool

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import modelformset_factory
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import ngettext_lazy
from django.utils.translation import ugettext_lazy as _

from dateutil.relativedelta import relativedelta
from model_utils import Choices

from nsc.stakeholder.models import Stakeholder
from nsc.utils.datetime import get_today

from ..document.models import Document
from ..policy.formsets import PolicySelectionFormset
from ..policy.models import Policy
from ..stakeholder.formsets import StakeholderSelectionFormset
from ..utils.markdown import convert
from .models import Review, ReviewRecommendation, SummaryDraft


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

    name = forms.CharField(
        label=_("Internal product name"),
        help_text=_(
            "This will be produced automatically unless filled in specifically"
        ),
    )

    review_type = forms.MultipleChoiceField(
        label=_("What type of product is this?"),
        help_text=_("Select all that apply"),
        choices=Review.TYPE,
        widget=forms.CheckboxSelectMultiple,
        error_messages={"required": _("Select which type of review this is")},
    )

    class Meta:
        model = Review
        fields = ["name", "review_type"]

    def clean_name(self):
        name = self.cleaned_data["name"]
        slug = slugify(name)

        if Review.objects.filter(slug=slug).exists():
            raise ValidationError(_("A review with this name already exists"))

        return name

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
                else [{"policy": policy} for policy in self.initial.get("policies", [])]
            ),
        )

    def is_valid(self):
        policies_is_valid = self.policy_formset.is_valid()
        return super(ReviewForm, self).is_valid() and policies_is_valid

    def save(self, *args, **kwargs):
        instance = super(ReviewForm, self).save(*args, **kwargs)

        policy_ids = [entry["policy"].id for entry in self.policy_formset.cleaned_data]
        instance.policies.set(policy_ids)
        instance.stakeholders.set(
            Stakeholder.objects.filter(policies__pk__in=policy_ids).distinct()
        )
        return instance


class ReviewDatesForm(forms.ModelForm):

    consultation_open = forms.TypedChoiceField(
        label=_("Consultation open date"),
        help_text=_("When do you want to open this consultation?"),
        choices=Choices((True, "now"), (False, "later"),),
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

    nsc_meeting_date_month = forms.IntegerField(label=_("Month"), required=False)
    nsc_meeting_date_year = forms.IntegerField(label=_("Year"), required=False)

    class Meta:
        model = Review
        fields = ["consultation_start", "consultation_end", "nsc_meeting_date"]

    def __init__(self, *args, initial=None, **kwargs):
        three_months_time = self.today + relativedelta(months=+3)

        initial = {
            "consultation_start_day": self.today.day,
            "consultation_start_month": self.today.month,
            "consultation_start_year": self.today.year,
            "consultation_end_day": three_months_time.day,
            "consultation_end_month": three_months_time.month,
            "consultation_end_year": three_months_time.year,
            **(initial or {}),
        }

        super().__init__(*args, initial=initial, **kwargs)

        self.fields["consultation_open"].choices = (
            (
                True,
                _("Now - open this consultation and email {} stakeholders").format(
                    self.instance.stakeholders.count()
                ),
            ),
            (
                False,
                _("Schedule this consultation to automatically open on a later date"),
            ),
        )

        # if the dates have already been confirmed disable the fields
        for field in self.fields.values():
            field.widget.attrs["disabled"] = self.instance.dates_confirmed

    @cached_property
    def today(self):
        return get_today()

    def clean_consultation_open(self):
        value = self.cleaned_data["consultation_open"]
        return strtobool(value) if value else None

    def clean(self):
        if self.instance.dates_confirmed:
            self.add_error(None, _("The dates have already been confirmed."))

        data = self.cleaned_data

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
                data["consultation_start"] = self.today.replace(
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
                data["consultation_end"] = self.today.replace(
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

        month = data.get("nsc_meeting_date_month", None)
        year = data.get("nsc_meeting_date_year", None)

        if month is not None or year is not None:
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

        if month is not None and year is not None:
            try:
                data["nsc_meeting_date"] = self.today.replace(
                    year=year, month=month, day=1
                )
            except ValueError:
                self.add_error(
                    "nsc_meeting_date", _("Enter a correct date for the NSC Meeting")
                )

        if month is None and year is None:
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
            if data["nsc_meeting_date"].replace(day=1) < data[
                "consultation_end"
            ].replace(day=1):
                self.add_error(
                    "nsc_meeting_date",
                    _(
                        "Enter a date for the NSC meeting which is after the consultation end."
                    ),
                )

        return data


class ReviewDateConfirmationForm(forms.ModelForm):
    dates_confirmed = forms.TypedChoiceField(
        choices=((True, _("Yes")), (False, _("No")),),
        widget=forms.RadioSelect,
        initial=None,
    )

    class Meta:
        model = Review
        fields = ("dates_confirmed",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["dates_confirmed"].label = _(
            "Confirm you want to open the {review} consultation now?"
        ).format(review=self.instance)

        if self.instance.review_start >= get_today():
            self.fields["dates_confirmed"].help_text = _(
                "This will update the public condition page to show the consultation is open and notify "
                "{stakeholders} by email"
            ).format(stakeholders=self.instance.stakeholders.count())
        else:
            self.fields["dates_confirmed"].help_text = _(
                "This will schedule the public condition page to show the consultation is open and notify "
                "{stakeholders} by email on {date}"
            ).format(
                stakeholders=self.instance.stakeholders.count(),
                date=self.instance.consultation_start.strftime("%d %m %Y"),
            )

        # if the dates have already been confirmed disable the fields
        for field in self.fields.values():
            field.widget.attrs["disabled"] = self.instance.dates_confirmed

    def clean(self):
        if self.instance.dates_confirmed:
            self.add_error(None, _("The dates have already been confirmed."))

        if not self.instance.consultation_start:
            self.add_error(
                None, _("The review consultation start date has not been set.")
            )
        if not self.instance.consultation_end:
            self.add_error(
                None, _("The review consultation end date has not been set.")
            )
        if not self.instance.nsc_meeting_date:
            self.add_error(None, _("The review UK NSC meeting date has not been set."))

        return super().clean()


class ReviewStakeholdersForm(forms.ModelForm):

    stakeholders = forms.ModelMultipleChoiceField(
        label=_("Stakeholders"),
        queryset=Stakeholder.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        help_text=_("Deselect any stakeholders that are not to be notified"),
    )

    class Meta:
        model = Review
        fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["stakeholders"].queryset = (
            (self.instance.stakeholders.distinct() | self.instance.policy_stakeholders)
            .distinct()
            .order_by("name")
        )

    def is_valid(self):
        formset_valid = self.extra_stakeholders_formset.is_valid()
        return super().is_valid() and formset_valid

    @cached_property
    def extra_stakeholders_formset(self):
        formset = StakeholderSelectionFormset(
            self.data or None,
            prefix="stakeholders",
            initial=(
                [{"stakeholder": s} for s in self.instance.stakeholders.none()]
                if self.instance.id
                else None
            ),
        )
        formset.min_num = 0
        return formset

    def save(self, commit=True):
        self.instance.stakeholders.set(
            set(self.cleaned_data["stakeholders"])
            | set(
                f.cleaned_data["stakeholder"] for f in self.extra_stakeholders_formset
            )
        )

        self.instance.stakeholders_confirmed = True
        self.instance.save()
        return self.instance


class SummaryDraftFormsetForm(forms.ModelForm):
    review = forms.ModelChoiceField(Review.objects.all(), widget=forms.HiddenInput)
    policy = forms.ModelChoiceField(Policy.objects.all(), widget=forms.HiddenInput)
    updated = forms.NullBooleanField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = SummaryDraft
        fields = ("review", "policy", "text", "updated")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["text"].label = self.instance.policy.name
        self.fields["text"].help_text = _(
            "Use markdown to complete the text field below."
        )

    def has_changed(self):
        # force the form to update the "updated" status even if the text is unchanged
        return True

    def clean_updated(self):
        return True


class ReviewSummaryForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = []

    @cached_property
    def formset(self):
        summaries = {s.policy: s for s in self.instance.summary_drafts.all()}
        policies = self.instance.policies.all()
        for p in policies:
            if p not in summaries:
                SummaryDraft.objects.create(
                    policy=p, review=self.instance, text=p.summary
                )

        return modelformset_factory(
            SummaryDraft,
            form=SummaryDraftFormsetForm,
            min_num=len(policies),
            max_num=len(policies),
            can_delete=False,
            can_order=False,
            extra=False,
        )(
            queryset=self.instance.summary_drafts.all().order_by("policy__name"),
            prefix="summary",
            data=self.data or None,
        )

    def is_valid(self):
        formset_valid = self.formset.is_valid()
        return super().is_valid() and formset_valid

    def save(self, commit=True):
        self.formset.save(commit=commit)
        return super().save(commit=commit)


class ReviewHistoryForm(forms.ModelForm):

    background = forms.CharField(
        label=_("Upload product history"),
        help_text=_("Use markdown to format the text"),
        widget=forms.Textarea,
        error_messages={"required": "Enter the history of this review."},
    )

    class Meta:
        model = Review
        fields = ["background"]


class RecommendationFormsetForm(forms.ModelForm):
    review = forms.ModelChoiceField(Review.objects.all(), widget=forms.HiddenInput)
    policy = forms.ModelChoiceField(Policy.objects.all(), widget=forms.HiddenInput)
    recommendation = forms.TypedChoiceField(
        choices=Choices((True, _("Yes")), (False, _("No"))),
        widget=forms.RadioSelect,
        required=True,
    )

    class Meta:
        model = ReviewRecommendation
        fields = (
            "review",
            "policy",
            "recommendation",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["recommendation"].label = self.instance.policy.name


class ReviewRecommendationForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = []

    @cached_property
    def formset(self):
        summaries = {s.policy: s for s in self.instance.review_recommendations.all()}
        policies = self.instance.policies.all()
        for p in policies:
            if p not in summaries:
                ReviewRecommendation.objects.create(
                    policy=p, review=self.instance, recommendation=None
                )

        return modelformset_factory(
            ReviewRecommendation,
            form=RecommendationFormsetForm,
            min_num=len(policies),
            max_num=len(policies),
            can_delete=False,
            can_order=False,
            extra=False,
        )(
            queryset=self.instance.review_recommendations.all().order_by(
                "policy__name"
            ),
            prefix="recommendation",
            data=self.data or None,
        )

    def is_valid(self):
        formset_valid = self.formset.is_valid()
        return super().is_valid() and formset_valid

    def save(self, commit=True):
        self.formset.save(commit=commit)
        return super().save(commit=commit)


class ReviewPublishForm(forms.ModelForm):

    published = forms.BooleanField(
        widget=forms.RadioSelect(choices=Choices((True, _("Yes")), (False, _("No")))),
    )

    class Meta:
        model = Review
        fields = ["published"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        conditions = list(self.instance.policies.values_list("name", flat=True))
        joined_conditions = conditions[0]
        if len(conditions) > 1:
            joined_conditions = _("{list} and {final}").format(
                list=", ".join(conditions[:-1]), final=conditions[-1]
            )

        self.fields["published"].help_text = ngettext_lazy(
            "This will publish the recommendation decision, plain text summary and supporting "
            "documents to the public {conditions} page",
            "This will publish the recommendation decision, plain text summary and supporting "
            "documents to the public {conditions} pages",
            len(conditions),
        ).format(conditions=joined_conditions)

    def save(self, commit=True):
        if not self.cleaned_data["published"]:
            return self.instance

        summaries = self.instance.summary_drafts.values_list("policy_id", "text")
        recommendations = self.instance.review_recommendations.values_list(
            "policy_id", "recommendation"
        )

        with transaction.atomic():
            # attach the supporting documents to the policies
            supporting_document_types = [
                Document.TYPE.cover_sheet,
                Document.TYPE.evidence_review,
                Document.TYPE.evidence_map,
                Document.TYPE.cost,
                Document.TYPE.systematic,
                Document.TYPE.other,
            ]
            supporting_documents = self.instance.documents.filter(
                document_type__in=supporting_document_types
            )
            for doc in supporting_documents:
                doc.policies.set(self.instance.policies.all())

            # update the plain english summary of each policy
            for policy_id, text in summaries:
                Policy.objects.filter(id=policy_id).update(
                    summary=text, summary_html=convert(text)
                )

            # update the recommendation of each policy
            for policy_id, recommendation in recommendations:
                Policy.objects.filter(id=policy_id).update(
                    recommendation=recommendation
                )

            _today = get_today()
            self.instance.review_end = _today
            self.instance.policies.update(
                next_review=_today.replace(year=_today.year + 3)
            )

            return super().save(commit=commit)
