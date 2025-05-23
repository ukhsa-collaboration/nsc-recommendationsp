from django.urls import reverse

import pytest


# All tests require the database
pytestmark = pytest.mark.django_db


def test_view(erm_user, client):
    """
    Test that the page can be displayed
    """
    client.force_login(erm_user)
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200


def test_view__own_reviews(make_review, erm_user, non_user, client):
    """
    Test that the page can be displayed
    """
    client.force_login(erm_user)
    expected = make_review()
    make_review(user=non_user)
    response = client.get(reverse("dashboard"))

    assert response.status_code == 200
    assert len(response.context["reviews"]) == 1
    assert response.context["reviews"][0].pk == expected.pk


def test_view__no_user(test_access_no_user):
    test_access_no_user(url=reverse("dashboard"))


def test_view__incorrect_permission(test_access_forbidden):
    test_access_forbidden(url=reverse("dashboard"))
