from django.urls import reverse

import pytest


# All tests require the database
pytestmark = pytest.mark.django_db


def test_view(erm_user, make_review, client):
    """
    Test that the page can be displayed.
    """
    make_review()
    response = client.get(reverse("review:list"), user=erm_user)
    assert response.status == "200 OK"


def test_view__no_user(test_access_no_user):
    test_access_no_user(url=reverse("review:list"))


def test_view__incorrect_permission(test_access_forbidden):
    test_access_forbidden(url=reverse("review:list"))
