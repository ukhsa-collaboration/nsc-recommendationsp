from distutils.util import strtobool

from django import forms
from django.forms import HiddenInput
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices

from .models import Document


class DocumentForm(forms.ModelForm):

    is_public = forms.TypedChoiceField(
        label=_(
            "Would you like this file to be available for download on the policy page?"
        ),
        choices=((True, _("Yes")), (False, _("No"))),
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Document
        fields = ["name", "document_type", "is_public", "review", "document"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields["name"].widget.attrs.update({"class": "govuk-input"})
        self.fields["is_public"].widget.attrs.update({"class": "govuk-radios__input"})
        self.fields["document_type"].widget = HiddenInput()
        self.fields["document"].label = _("Upload a file")
        self.fields["review"].widget = HiddenInput()


class UploadAnotherForm(forms.Form):
    YES_NO_CHOICES = Choices(("yes", _("Yes")), ("no", _("No")))

    another = forms.TypedChoiceField(
        label=_("Would you like to upload another document?"),
        choices=YES_NO_CHOICES,
        widget=forms.RadioSelect,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields["another"].widget.attrs.update({"class": "govuk-radios__input"})

    def clean_another(self):
        return strtobool(self.cleaned_data["another"])


class ReviewDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["name", "document_type", "is_public", "review", "document"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields["document"].label = _("Upload a file")
        self.fields["name"].widget = HiddenInput()
        self.fields["document_type"].widget = HiddenInput()
        self.fields["is_public"].widget = HiddenInput()
        self.fields["review"].widget = HiddenInput()
