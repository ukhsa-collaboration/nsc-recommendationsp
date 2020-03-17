from django.urls import reverse

import pytest


# All tests require the database
pytestmark = pytest.mark.django_db
pytest_plugins = ["nsc.document.tests.fixtures"]


def test_view(review_document, django_app):
    """
    Test that the page can be displayed
    """
    response = django_app.get(
        reverse("document:download", kwargs={"pk": review_document.pk})
    )
    assert response.status == "200 OK"
    review_document.delete()
    review_document.review.delete()
