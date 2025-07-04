import pytest
from model_bakery import baker

from nsc.review.models import Review

from ..forms import ExternalReviewForm
from ..models import Document


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def form_data(form_pdf):
    return {
        "data": {
            "document-TOTAL_FORMS": 1,
            "document-INITIAL_FORMS": 0,
            "document-MIN_NUM_FORMS": 1,
            "document-MAX_NUM_FORMS": 1000,
            "document-0-id": "",
        },
        "files": {"document-0-upload": form_pdf},
    }


def test_form_configuration():
    formset = ExternalReviewForm(instance=baker.make(Review)).formset
    assert Document == formset.form._meta.model
    assert Document.TYPE.external_review == formset.form.document_type
    assert "upload" in formset.form._meta.fields


def test_form_is_valid(form_data):
    form = ExternalReviewForm(instance=baker.make(Review), **form_data)
    assert form.is_valid()


def test_file_is_required(form_data):
    form_data["files"]["document-0-upload"] = None
    form = ExternalReviewForm(instance=baker.make(Review), **form_data)
    assert not form.is_valid()
    assert "upload" in form.formset.errors[0]