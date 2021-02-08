from django.urls import reverse

import pytest


# All tests require the database
pytestmark = pytest.mark.django_db


def test_view(make_review, django_app):
    """
    Test that the page can be displayed.
    """
    make_review()
    response = django_app.get(reverse("review:list"))
    assert response.status == "200 OK"
