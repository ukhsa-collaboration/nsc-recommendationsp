from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

import pytest
from bs4 import BeautifulSoup
from model_bakery import baker

from nsc.review.models import Review


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
    client.force_login(erm_user)
    review = baker.make(Review, name="Review", slug="review")

    response = client.get(
        reverse("review:add-external-review", kwargs={"slug": review.slug})
    )
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")
    upload_input = soup.find("input", {"name": "document-0-upload"})

    assert upload_input is not None
    assert upload_input.get("value", "") == ""

    review.delete()


def test_document_created(erm_user, minimal_pdf, client):
    """
    Test the external review document is uploaded and the document is created.
    """
    # Create a review
    review = baker.make(Review, name="Review", slug="review", user=erm_user)

    # User login
    client.force_login(erm_user)

    # Prepare the file upload
    uploaded_file = SimpleUploadedFile(
        "document.pdf", minimal_pdf.encode(), content_type="application/pdf"
    )

    # Prepare form data
    post_data = {
        "document-TOTAL_FORMS": "1",
        "document-INITIAL_FORMS": "0",
        "document-0-upload": uploaded_file,
    }

    # Post the form
    url = reverse("review:add-external-review", kwargs={"slug": review.slug})
    response = client.post(url, post_data, follow=True)

    # Fetch the document and validate
    document = review.get_external_reviews().first()

    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse(
        "review:detail", kwargs={"slug": review.slug}
    )
    assert document is not None
    assert document.file_exists()

    # Cleanup
    document.delete()
    review.delete()
