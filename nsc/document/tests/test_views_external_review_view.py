import os

from django.urls import reverse
from django.utils.translation import ugettext

import pytest
from model_bakery import baker

from nsc.document.models import Document
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
    assert form["name"].value == ugettext("External review")
    assert form["document_type"].value == Document.TYPE.external_review
    assert form["review"].value == str(review.pk)
    assert form["upload"].value == ""
    review.delete()


def test_document_created(minimal_pdf, django_app):
    """
    Test the external review document is uploaded and the document is created.
    """
    review = baker.make(Review, name="Review", slug="review")
    form = django_app.get(
        reverse("review:add-external-review", kwargs={"slug": review.slug})
    ).form
    form["upload"] = ("document.pdf", minimal_pdf.encode(), "application/pdf")
    response = form.submit().follow()
    document = review.get_external_review()
    assert response.status == "200 OK"
    assert response.request.path == reverse(
        "review:detail", kwargs={"slug": review.slug}
    )
    assert document is not None
    assert document.file_exists()
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
    form["upload"] = ("new.pdf", minimal_pdf.encode(), "application/pdf")
    form.submit().follow()

    document = review.get_external_review()
    assert os.path.basename(document.upload.name) == "new.pdf"
    assert document.file_exists()
    assert not document.upload.storage.exists(existing)

    review.delete()
