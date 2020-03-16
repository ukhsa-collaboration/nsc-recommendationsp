import random

from django.core.files.uploadedfile import SimpleUploadedFile

import pytest
from model_bakery import baker

from nsc.document.models import Document
from nsc.review.models import Review


@pytest.fixture
def minimal_pdf():
    """
    Return the contents of a minimum viable PDF. Thanks to
    https://stackoverflow.com/questions/17279712/what-is-the-smallest-possible-valid-pdf
    """
    return (
        "%PDF-1.0\x0D"
        "1 0 obj<</Pages 2 0 R>>endobj 2 0 obj<</Kids[3 0 R]/Count 1>>endobj 3 0 obj<</MediaBox[0 0 3 3]>>endobj\x0D"
        "trailer<</Root 1 0 R>>\x0D"
        "%EOF"
    )


@pytest.fixture
def form_pdf(minimal_pdf):
    """
    Return a minimum viable PDF that can be used in a form.
    """
    return SimpleUploadedFile(
        "document.pdf", minimal_pdf.encode(), content_type="application/pdf"
    )


@pytest.fixture
def model_pdf(minimal_pdf):
    """
    Return a minimum viable PDF that can be used in a model.
    """
    return SimpleUploadedFile(
        "document.pdf", minimal_pdf.encode(), content_type="application/pdf"
    )
    # return ContentFile(minimal_pdf, name="document.pdf")


@pytest.fixture
def make_document(model_pdf):
    def _make_document(**kwargs):
        return baker.make(Document, upload=model_pdf, **kwargs)

    return _make_document


@pytest.fixture
def review_document(make_document):
    types = [item[0] for item in Document.TYPE]
    return make_document(
        name="Document",
        document_type=random.choice(types),
        review=baker.make(Review, name="Review", slug="name"),
    )


@pytest.fixture
def external_review(make_document):
    return make_document(
        name="External review",
        document_type=Document.TYPE.external_review,
        review=baker.make(Review, name="Review", slug="name"),
    )


@pytest.fixture
def submission_form(make_document):
    return make_document(
        name="Submission form",
        document_type=Document.TYPE.submission_form,
        review=baker.make(Review, name="Review", slug="name"),
    )


@pytest.fixture
def evidence_review(make_document):
    return make_document(
        name="Evidence review",
        document_type=Document.TYPE.evidence_review,
        review=baker.make(Review, name="Review", slug="name"),
    )


@pytest.fixture
def cover_sheet(make_document):
    return make_document(
        name="Cover sheet",
        document_type=Document.TYPE.cover_sheet,
        review=baker.make(Review, name="Review", slug="name"),
    )
