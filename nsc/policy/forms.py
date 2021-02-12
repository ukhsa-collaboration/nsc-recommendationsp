import datetime
import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices

from nsc.document.forms import document_formset_form_factory
from nsc.document.models import Document, DocumentPolicy
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
        label=_("Date next review expected to open"),
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


class ArchiveForm(forms.ModelForm):
    archived_reason_error = _(
        "You must add to the template provided a public statement before pressing Archive."
    )
    archived_reason_initial = _("This condition has been archived because:")

    archived_reason = forms.CharField(
        required=True,
        label=_("Why has this form recommendation been archived?"),
        help_text=_(
            "Write a public statement to explain reasons for archiving recommendation (mandatory)"
            "<br/>"
            "Use markdown to format the text."
        ),
        widget=forms.Textarea,
        initial=archived_reason_initial,
    )

    class Meta:
        model = Policy
        fields = ["archived_reason"]

    def clean_archived_reason(self):
        value = self.cleaned_data["archived_reason"]

        if not value:
            raise ValidationError(self.archived_reason_error)

        if value == self.archived_reason_initial:
            raise ValidationError(self.archived_reason_error)

        return value

    def save(self, commit=True):
        self.instance.archived = True
        return super().save(commit=commit)


class ArchiveDocumentForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = []

    @cached_property
    def documents_formset(self):
        return modelformset_factory(
            Document,
            min_num=1,
            extra=0,
            form=document_formset_form_factory(
                Document.TYPE.archive,
                _("Select file for upload"),
                required=True,
                policy=self.instance,
                source=DocumentPolicy.SOURCE.archive,
            ),
            fields=["upload", "name"],
        )(
            data=self.data or None,
            files=self.files or None,
            prefix="document",
            queryset=Document.objects.none(),
        )

    def is_valid(self):
        is_valid = self.documents_formset.is_valid()
        return super().is_valid() and is_valid

    def save(self, commit=True):
        self.documents_formset.save()
        return self.instance
