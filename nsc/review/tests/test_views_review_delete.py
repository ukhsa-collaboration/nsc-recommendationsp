from django.urls import reverse

import pytest


# All tests require the database
pytestmark = pytest.mark.django_db
pytest_plugins = ["nsc.review.tests.fixtures"]


def test_view(make_review, django_app):
    """
    Test that the page can be displayed.
    """
    review = make_review()
    response = django_app.get(reverse("review:delete", kwargs={"slug": review.slug}))
    assert response.status == "200 OK"
