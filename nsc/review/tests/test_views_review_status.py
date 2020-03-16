from django.urls import reverse

import pytest


# All tests require the database
pytestmark = pytest.mark.django_db


def test_view(django_app):
    """
    Test that the page can be displayed
    """
    response = django_app.get(reverse("home"))
    assert response.status == "200 OK"
