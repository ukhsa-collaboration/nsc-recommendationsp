from django.urls import reverse

import pytest
from model_bakery import baker

from nsc.review.models import Review


# All tests require the database
pytestmark = pytest.mark.django_db


def test_view(erm_user, django_app):
    """
    Test that the page can be displayed
    """
    review = baker.make(Review)
    response = django_app.get(
        reverse("review:add-external-review", kwargs={"slug": review.slug}),
        user=erm_user,
    )
    assert response.status == "200 OK"


def test_view__no_user(test_access_no_user):
    review = baker.make(Review)
    test_access_no_user(
        url=reverse("review:add-external-review", kwargs={"slug": review.slug}),
    )


def test_view__incorrect_permission(test_access_forbidden):
    review = baker.make(Review)
    test_access_forbidden(
        url=reverse("review:add-external-review", kwargs={"slug": review.slug}),
    )


def test_initial_values(erm_user, django_app):
    """
    Test the form fields are initialised to upload the external review.
    """
    review = baker.make(Review, name="Review", slug="review")
    form = django_app.get(
        reverse("review:add-external-review", kwargs={"slug": review.slug}),
        user=erm_user,
    ).forms[1]
    assert form["document-0-upload"].value == ""
    review.delete()


def test_document_created(erm_user, minimal_pdf, django_app):
    """
    Test the external review document is uploaded and the document is created.
    """
    review = baker.make(Review, name="Review", slug="review", user=erm_user)
    form = django_app.get(
        reverse("review:add-external-review", kwargs={"slug": review.slug}),
        user=erm_user,
    ).forms[1]
    form["document-TOTAL_FORMS"] = 1
    form["document-0-upload"] = (
        "document.pdf",
        minimal_pdf.encode(),
        "application/pdf",
    )
    response = form.submit().follow()
    document = review.get_external_reviews().first()
    assert response.status == "200 OK"
    assert response.request.path == reverse(
        "review:detail", kwargs={"slug": review.slug}
    )
    assert document is not None
    assert document.file_exists()
    document.delete()
    review.delete()
