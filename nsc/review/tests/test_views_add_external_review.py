import os

from django.urls import reverse

import pytest
from model_bakery import baker

from nsc.review.models import Review


# All tests require the database
pytestmark = pytest.mark.django_db
pytest_plugins = ["nsc.document.tests.fixtures"]


def test_view(django_app):
    """
    Test that the page can be displayed
    """
    review = baker.make(Review)
    response = django_app.get(
        reverse("review:add-external-review", kwargs={"slug": review.slug})
    )
    assert response.status == "200 OK"


def test_initial_values(django_app):
    """
    Test the form fields are initialised to upload the external review.
    """
    review = baker.make(Review, name="Review", slug="review")
    form = django_app.get(
        reverse("review:add-external-review", kwargs={"slug": review.slug})
    ).form
    assert form["document-0-upload"].value == ""
    review.delete()


def test_document_created(minimal_pdf, django_app):
    """
    Test the external review document is uploaded and the document is created.
    """
    review = baker.make(Review, name="Review", slug="review")
    form = django_app.get(
        reverse("review:add-external-review", kwargs={"slug": review.slug})
    ).form
    form["document-TOTAL_FORMS"] = 1
    form["document-0-upload"] = (
        "document.pdf",
        minimal_pdf.encode(),
        "application/pdf",
    )
    response = form.submit().follow()
    document = review.get_external_review().first()
    assert response.status == "200 OK"
    assert response.request.path == reverse(
        "review:detail", kwargs={"slug": review.slug}
    )
    assert document is not None
    assert document.file_exists()
    document.delete()
    review.delete()


def test_existing_document_is_replaced(external_review, minimal_pdf, django_app):
    """
    Test any existing external review document is replaced by the new upload.
    """
    review = external_review.review
    existing = external_review.upload.name

    form = django_app.get(
        reverse("review:add-external-review", kwargs={"slug": review.slug})
    ).form
    form["document-TOTAL_FORMS"] = 1
    form["document-0-id"] = external_review.id
    form["document-0-upload"] = ("new.pdf", minimal_pdf.encode(), "application/pdf")
    form.submit().follow()
    document = review.get_external_review().first()
    assert os.path.basename(document.upload.name) == "new.pdf"
    assert document.file_exists()
    assert not document.upload.storage.exists(existing)
    document.delete()
    review.delete()
