from django.urls import reverse

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db
pytest_plugins = ["nsc.review.tests.fixtures"]


@pytest.fixture
def response(make_review, django_app):
    review = make_review()
    url = reverse("review:delete", kwargs={"slug": review.slug})
    return django_app.get(url)


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_view(response):
    """
    Test that the page can be displayed.
    """
    assert response.status == "200 OK"


def test_back_link(response, dom):
    """
    Test the back link returns to the review detail page.
    """
    review = response.context["object"]
    link = dom.find(id="back-link-id")
    assert link["href"] == review.get_absolute_url()
