from django.urls import reverse

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def url(make_review):
    review = make_review()
    return reverse("review:detail", kwargs={"slug": review.slug})


@pytest.fixture
def response(url, erm_user, django_app):
    return django_app.get(url, user=erm_user)


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_view(response):
    """
    Test that the page can be displayed.
    """
    assert response.status == "200 OK"


def test_view__no_user(url, test_access_no_user):
    test_access_no_user(url=url)


def test_view__incorrect_permission(url, test_access_forbidden):
    test_access_forbidden(url=url)


def test_view__not_user(url, test_access_not_user):
    test_access_not_user(url=url)


def test_back_link(dom):
    """
    Test the back link returns to the dashboard.
    """
    link = dom.find(id="back-link-id")
    assert link["href"] == reverse("dashboard")
