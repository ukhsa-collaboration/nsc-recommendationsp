from django import forms
from django.forms import HiddenInput, modelformset_factory
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from ..review.models import Review
from .models import Document


def review_document_formset_form_factory(
    _document_type, _filename, required_error_message
):
    class ReviewDocumentFormsetForm(forms.ModelForm):
        filename = _filename
        document_type = _document_type
        upload = forms.FileField(
            label=_("Upload a file"),
            error_messages={"required": required_error_message},
        )

        class Meta:
            model = Document
            fields = ["upload"]

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.orig_filename = None
            if self.instance.id:
                self.orig_filename = self.instance.upload.name

            self.fields["upload"].widget.attrs.update({"class": "govuk-file-upload"})

        def save(self, commit=True):
            if f"{self.prefix}-upload" in self.files and self.orig_filename:
                self.instance.upload.storage.delete(self.orig_filename)
            self.instance.document_type = self.document_type
            self.instance.name = self.filename
            return super().save(commit=False)

    return ReviewDocumentFormsetForm


class ReviewDocumentForm(forms.ModelForm):
    document_type = None
    file_name = "Document"
    requires_error_message = _("Select the file for upload")

    class Meta:
        model = Review
        fields = ()

    @cached_property
    def formset(self):
        return modelformset_factory(
            Document,
            min_num=1,
            extra=0,
            form=review_document_formset_form_factory(
                self.document_type, self.file_name, self.requires_error_message,
            ),
            fields=["upload"],
        )(
            data=self.data or None,
            files=self.files or None,
            queryset=self.instance.get_external_review(),
            prefix="document",
        )

    def is_valid(self):
        formset_valid = self.formset.is_valid()
        return super().is_valid() and formset_valid

    def save(self, commit=True):
        for doc in self.formset.save(commit=False):
            doc.review = self.instance
            if commit:
                doc.save()

        return super().save(commit=commit)


class ExternalReviewForm(ReviewDocumentForm):
    document_type = Document.TYPE.external_review
    file_name = "External review"
    requires_error_message = _("Select the external review for upload")


class SubmissionForm(forms.ModelForm):

    upload = forms.FileField(
        label=_("Upload a file"),
        error_messages={"required": _("Select the response form for upload")},
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
