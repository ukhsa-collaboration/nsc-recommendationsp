from django import forms
from django.forms import HiddenInput, modelformset_factory
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from ..review.models import Review
from .models import Document, DocumentPolicy


def document_formset_form_factory(
    _document_type, required_error_message, required=True, review=None, policy=None, source=None
):
    class DocumentFormsetForm(forms.ModelForm):
        document_type = _document_type
        upload = forms.FileField(
            label=_("Upload a file"),
            error_messages={"required": required_error_message},
            required=required,
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
            self.instance.name = self.instance.upload.name

            if review:
                self.instance.review = review

            if policy:
                DocumentPolicy.objects.create(document=self.instance, policy=policy, source=source)

            return super().save(commit=commit)

    return DocumentFormsetForm


class ReviewDocumentForm(forms.ModelForm):
    document_type = None
    required_error_message = _("Select the file for upload")

    class Meta:
        model = Review
        fields = ()

    @cached_property
    def formset(self):
        return modelformset_factory(
            Document,
            min_num=1,
            extra=0,
            form=document_formset_form_factory(
                self.document_type, self.required_error_message,
            ),
            fields=["upload"],
        )(
            data=self.data or None,
            files=self.files or None,
            queryset=Document.objects.none(),
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
    required_error_message = _("Select the external review for upload")


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


class ReviewDocumentsForm(forms.ModelForm):

    cover_sheet = forms.FileField(label=_("Cover sheet"), required=False,)

    evidence_review = forms.FileField(label=_("Evidence review"), required=False,)

    evidence_map = forms.FileField(label=_("Evidence map"), required=False,)

    cost_effective_model = forms.FileField(
        label=_("Cost-effective model"), required=False,
    )

    systematic_review = forms.FileField(label=_("Systematic review"), required=False,)

    class Meta:
        model = Review
        fields = ()

    def __init__(self, instance=None, initial=None, **kwargs):
        initial = {
            "cover_sheet": getattr(instance.cover_sheet, "upload", None),
            "evidence_review": getattr(instance.evidence_review, "upload", None),
            "evidence_map": getattr(instance.evidence_map, "upload", None),
            "cost_effective_model": getattr(
                instance.cost_effective_model, "upload", None
            ),
            "systematic_review": getattr(instance.systematic_review, "upload", None),
            **(initial or {}),
        }

        super().__init__(instance=instance, initial=initial, **kwargs)

        if Review.TYPE.evidence not in self.instance.review_type:
            del self.fields["evidence_review"]

        if Review.TYPE.map not in self.instance.review_type:
            del self.fields["evidence_map"]

        if Review.TYPE.cost not in self.instance.review_type:
            del self.fields["cost_effective_model"]

        if Review.TYPE.systematic not in self.instance.review_type:
            del self.fields["systematic_review"]

        for field in self.fields.values():
            field.widget.attrs.update({"class": "govuk-file-upload"})

    @cached_property
    def others_formset(self):
        return modelformset_factory(
            Document,
            min_num=0,
            extra=0,
            form=document_formset_form_factory(
                Document.TYPE.other,
                _("Select on other file for upload"),
                required=False,
                review=self.instance,
            ),
            fields=["upload"],
        )(
            data=self.data or None,
            files=self.files or None,
            prefix="document",
            queryset=Document.objects.none(),
        )

    def is_valid(self):
        others_is_valid = self.others_formset.is_valid()
        return super().is_valid() and others_is_valid

    def update_doc(self, doc_type, field_name):
        if field_name in self.files:
            existing = getattr(self.instance, field_name, None)
            if existing and existing.id:
                existing.delete()

            Document.objects.create(
                review=self.instance,
                document_type=doc_type,
                upload=self.cleaned_data[field_name],
                name=Document.TYPE[doc_type],
            )

    def save(self, commit=True):
        self.update_doc(Document.TYPE.cover_sheet, "cover_sheet")
        self.update_doc(Document.TYPE.evidence_review, "evidence_review")
        self.update_doc(Document.TYPE.evidence_map, "evidence_map")
        self.update_doc(Document.TYPE.cost, "cost_effective_model")
        self.update_doc(Document.TYPE.systematic, "systematic_review")

        if self.others_formset:
            self.others_formset.save()

        return self.instance
