from django.urls import reverse

import pytest
from model_bakery import baker

from nsc.review.models import Review
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db


def test_view(erm_user, client):
    """
    Test that the page can be displayed
    """
    client.force_login(erm_user)
    review = baker.make(Review)
    response = client.get(
        reverse("review:add-external-review", kwargs={"slug": review.slug}),
        user=erm_user,
    )
    assert response.status_code == 200


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


def test_initial_values(erm_user, client):
    """
    Test the form fields are initialised to upload the external review.
    """
    # review = baker.make(Review, name="Review", slug="review")
    # form = client.get(
    #     reverse("review:add-external-review", kwargs={"slug": review.slug}),
    #     user=erm_user,
    # ).forms[1]
    # assert form["document-0-upload"].value == ""
    # review.delete()
    client.force_login(erm_user)
    review = baker.make(Review, name="Review", slug="review")

    response = client.get(reverse("review:add-external-review", kwargs={"slug": review.slug}))
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")
    upload_input = soup.find("input", {"name": "document-0-upload"})

    assert upload_input is not None
    assert upload_input.get("value", "") == ""  # value should be empty

    review.delete()


def test_document_created(erm_user, minimal_pdf, client):
    """
    Test the external review document is uploaded and the document is created.
    """
    # review = baker.make(Review, name="Review", slug="review", user=erm_user)
    # form = client.get(
    #     reverse("review:add-external-review", kwargs={"slug": review.slug}),
    #     user=erm_user,
    # ).forms[1]
    # form["document-TOTAL_FORMS"] = 1
    # form["document-0-upload"] = (
    #     "document.pdf",
    #     minimal_pdf.encode(),
    #     "application/pdf",
    # )
    # response = form.submit().follow()
    # document = review.get_external_reviews().first()
    # assert response.status == "200 OK"
    # assert response.request.path == reverse(
    #     "review:detail", kwargs={"slug": review.slug}
    # )
    # assert document is not None
    # assert document.file_exists()
    # document.delete()
    # review.delete()

def test_add_external_review_upload(client, erm_user):
    # Log in as user
    client.force_login(erm_user)

    # Create a Review instance with the user
    review = baker.make("Review", name="Review", slug="review", user=erm_user)

    # Minimal PDF content
    minimal_pdf = b"%PDF-1.4\n%EOF\n"

    # Formset POST data
    post_data = {
        "document-TOTAL_FORMS": "1",
        "document-INITIAL_FORMS": "0",
        "document-MIN_NUM_FORMS": "0",
        "document-MAX_NUM_FORMS": "1",
    }

    # File upload
    file_data = {
        "document-0-upload": ("document.pdf", minimal_pdf, "application/pdf"),
    }

    url = reverse("review:add-external-review", kwargs={"slug": review.slug})

    # POST with form and file data
    response = client.post(url, data={**post_data, **file_data}, follow=True)

    # Assert the redirect landed on review detail page
    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("review:detail", kwargs={"slug": review.slug})

    # Check that the external review was created and file exists
    document = review.get_external_reviews().first()
    assert document is not None
    assert document.file_exists()

    # Cleanup
    document.delete()
    review.delete()
