from django.urls import reverse

import pytest


# All tests require the database

pytestmark = pytest.mark.django_db


def test_view(erm_user, make_review, client):
    """
    Test that the page can be displayed.
    """
    review = make_review()
    response = client.get(
        reverse("review:dates", kwargs={"slug": review.slug}), user=erm_user
    )
    assert response.status == "200 OK"


def test_view__no_user(make_review, test_access_no_user):
    review = make_review()
    test_access_no_user(url=reverse("review:dates", kwargs={"slug": review.slug}))


def test_view__incorrect_permission(make_review, test_access_forbidden):
    review = make_review()
    test_access_forbidden(url=reverse("review:dates", kwargs={"slug": review.slug}))


def test_view__not_user(make_review, test_access_not_user_can_access):
    review = make_review()
    test_access_not_user_can_access(
        url=reverse("review:dates", kwargs={"slug": review.slug})
    )
