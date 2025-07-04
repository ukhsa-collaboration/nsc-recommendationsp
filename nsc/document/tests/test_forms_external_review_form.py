import socket

from django.core.files.uploadedfile import SimpleUploadedFile

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


def _clamav_available(host="clamav", port=3310, timeout=1):  # helper
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except OSError:
        return False


@pytest.fixture
def clean_pdf():
    """Minimal, harmless PDF that satisfies your FileExtensionValidator."""
    return SimpleUploadedFile(
        "clean.pdf",
        b"%PDF-1.4\n%EOF\n",
        content_type="application/pdf",
    )


@pytest.fixture
def eicar_pdf():
    """
    The official EICAR antivirus‑test signature wrapped in a .pdf file name.
    This is NOT malware – just a string every AV engine recognises.
    """
    eicar_bytes = (
        b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$" b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    )
    return SimpleUploadedFile(
        "eicar.pdf",
        eicar_bytes,
        content_type="application/pdf",
    )


@pytest.mark.skipif(
    not _clamav_available(),
    reason="ClamAV daemon is not reachable – skipping integration test",
)
def test_real_virus_scan_rejects_eicar(eicar_pdf):
    form = ExternalReviewForm(
        instance=baker.make(Review),
        data={
            "document-TOTAL_FORMS": 1,
            "document-INITIAL_FORMS": 0,
            "document-MIN_NUM_FORMS": 1,
            "document-MAX_NUM_FORMS": 1000,
            "document-0-id": "",
        },
        files={"document-0-upload": eicar_pdf},
    )

    assert not form.is_valid()
    assert "Malware detected" in form.formset.errors[0]["upload"][0]


@pytest.mark.skipif(
    not _clamav_available(),
    reason="ClamAV daemon is not reachable – skipping integration test",
)
def test_real_virus_scan_accepts_clean_file(clean_pdf):
    form = ExternalReviewForm(
        instance=baker.make(Review),
        data={
            "document-TOTAL_FORMS": 1,
            "document-INITIAL_FORMS": 0,
            "document-MIN_NUM_FORMS": 1,
            "document-MAX_NUM_FORMS": 1000,
            "document-0-id": "",
        },
        files={"document-0-upload": clean_pdf},
    )

    assert form.is_valid()
