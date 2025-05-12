from django.urls import reverse

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def response(review_in_consultation, client):
    policy = review_in_consultation.policies.first()
    url = reverse("condition:consultation", kwargs={"slug": policy.slug})
    return client.get(url)


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_page(response):
    """
    Test the consultation page can be displayed.
    """
    assert response.status_code == 200


def test_back_link(response, dom):
    """
    Test the back link returns to the public policy page.
    """
    policy = response.context["condition"]
    expected = reverse("condition:detail", kwargs={"slug": policy.slug})
    link = dom.find(id="back-link-id")
    assert link["href"] == expected


def test_heading_caption(response, dom):
    """
    Test the name of the condition is displayed as caption for the page title.
    """
    condition = response.context["condition"]
    title = dom.find("h1")
    assert condition.name in title.text
