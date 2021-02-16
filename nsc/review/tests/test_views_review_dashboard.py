from django.urls import reverse

import pytest


# All tests require the database
pytestmark = pytest.mark.django_db


def test_view(erm_user, django_app):
    """
    Test that the page can be displayed
    """
    response = django_app.get(reverse("dashboard"), user=erm_user)
    assert response.status == "200 OK"


def test_view__no_user(test_access_no_user):
    test_access_no_user(url=reverse("dashboard"))


def test_view__incorrect_permission(test_access_forbidden):
    test_access_forbidden(url=reverse("dashboard"))
