from django.urls import reverse

import pytest


# All tests require the database
pytestmark = pytest.mark.django_db


def test_view(review_document, django_app):
    """
    Test that the page can be displayed
    """
    response = django_app.get(
        reverse("document:download", kwargs={"uuid": review_document.uuid})
    )
    assert response.status == "200 OK"
    review_document.delete()
    review_document.review.delete()
