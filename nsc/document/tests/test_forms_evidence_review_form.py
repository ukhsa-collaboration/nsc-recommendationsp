import pytest
from model_bakery import baker

from nsc.review.models import Review

from ..forms import EvidenceReviewUploadForm
from ..models import Document


# All tests require the database
pytestmark = pytest.mark.django_db
pytest_plugins = ["nsc.document.tests.fixtures"]


@pytest.fixture
def form_data(form_pdf):
    review = baker.make(Review, name="Review", slug="review")
    return {
        "data": {
            "name": "Document",
            "document_type": Document.TYPE.evidence_review,
            "is_public": True,
            "review": review.pk,
        },
        "files": {"upload": form_pdf},
    }


def test_form_configuration():
    assert Document == EvidenceReviewUploadForm.Meta.model
    assert "name" in EvidenceReviewUploadForm.Meta.fields
    assert "document_type" in EvidenceReviewUploadForm.Meta.fields
    assert "is_public" in EvidenceReviewUploadForm.Meta.fields
    assert "upload" in EvidenceReviewUploadForm.Meta.fields


def test_form_is_valid(form_data):
    form = EvidenceReviewUploadForm(**form_data)
    assert form.is_valid()


def test_name_is_required(form_data):
    form_data["data"]["name"] = None
    form = EvidenceReviewUploadForm(**form_data)
    assert not form.is_valid()
    assert "name" in form.errors


def test_document_type_is_required(form_data):
    form_data["data"]["document_type"] = None
    form = EvidenceReviewUploadForm(**form_data)
    assert not form.is_valid()
    assert "document_type" in form.errors


def test_file_is_required(form_data):
    form_data["files"]["upload"] = None
    form = EvidenceReviewUploadForm(**form_data)
    assert not form.is_valid()
    assert "upload" in form.errors
