import pytest
from model_bakery import baker

from nsc.document.models import Document

from ..forms import ArchiveForm, PolicyDocumentForm
from ..models import Policy


# All tests require the database
pytestmark = pytest.mark.django_db


def test_form_configuration():
    assert Policy == ArchiveForm.Meta.model
    assert "archived_reason" in ArchiveForm.Meta.fields


@pytest.mark.parametrize(
    "archived_reason,expected",
    [
        (None, False),  # The condition cannot be None
        ("", False),  # The condition cannot be blank
        (" ", False),  # The condition cannot be empty
        ("# Heading", True),  # The condition can be markdown
        ("<h1>Heading</h1>", True),  # The condition can be HTML
        # The condition can not be the initial only.
        (ArchiveForm.archived_reason_initial, False),
    ],
)
def test_condition_validation(archived_reason, expected):
    data = {
        "archived_reason": archived_reason,
    }
    assert ArchiveForm(data=data).is_valid() == expected


@pytest.fixture
def form_data(form_pdf):
    return {
        "data": {
            "document-TOTAL_FORMS": 1,
            "document-INITIAL_FORMS": 1,
            "document-MIN_NUM_FORMS": 1,
            "document-MAX_NUM_FORMS": 1000,
            "document-0-id": "0",
            "document-0-name": "test",
        },
        "files": {"document-0-upload": form_pdf},
    }


def test_document_form_configuration():
    formset = PolicyDocumentForm(instance=baker.make(Policy)).documents_formset
    assert Document == formset.form._meta.model
    assert Document.TYPE.archive == formset.form.document_type
    assert "upload" in formset.form._meta.fields
    assert "name" in formset.form._meta.fields


def test_document_is_required(form_data):
    form_data["files"]["document-0-upload"] = None
    form_data["data"]["document-0-name"] = None
    form = PolicyDocumentForm(instance=baker.make(Policy), **form_data)
    assert not form.is_valid()
    assert "upload" in form.documents_formset.errors[0]
    assert "name" in form.documents_formset.errors[0]
