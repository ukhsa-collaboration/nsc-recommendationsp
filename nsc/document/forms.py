from django import forms
from django.forms import HiddenInput
from django.utils.translation import ugettext_lazy as _

from .models import Document


class ExternalReviewForm(forms.ModelForm):

    upload = forms.FileField(
        label=_("Upload a file"),
        error_messages={"required": _("Select the external review for upload")},
    )

    class Meta:
        model = Document
        fields = ["name", "document_type", "review", "upload"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields["upload"].widget.attrs.update({"class": "govuk-file-upload"})
        self.fields["name"].widget = HiddenInput()
        self.fields["document_type"].widget = HiddenInput()
        self.fields["review"].widget = HiddenInput()


class ReviewDocumentsForm(forms.Form):

    evidence_review = forms.FileField(
        label=_("Cover sheet"),
        error_messages={"required": _("Select the evidence review for upload")},
    )

    cover_sheet = forms.FileField(
        label=_("Cover sheet"),
        error_messages={"required": _("Select the cover sheet for upload")},
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields["evidence_review"].widget.attrs.update(
            {"class": "govuk-file-upload"}
        )
        self.fields["cover_sheet"].widget.attrs.update({"class": "govuk-file-upload"})
