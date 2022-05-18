from django.urls import reverse
from django.utils.translation import gettext_lazy as _

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def response(review_in_consultation, django_app):
    policy = review_in_consultation.policies.first()
    url = reverse("condition:public-comment-submitted", kwargs={"slug": policy.slug})
    return django_app.get(url)


@pytest.fixture
def dom(response):
    return BeautifulSoup(response.content, "html.parser")


def test_page(response):
    """
    Test the consultation page can be displayed.
    """
    assert response.status == "200 OK"


def test_back_link(response, dom):
    """
    Test the back link returns to the public comment page.
    """
    policy = response.context["condition"]
    expected = reverse("condition:public-comment", kwargs={"slug": policy.slug})
    link = dom.find(id="back-link-id")
    assert link["href"] == expected


def test_heading_caption(response, dom):
    """
    Test the name of the condition is displayed as caption for the page title.
    """
    condition = response.context["condition"]
    title = dom.find("h1")
    assert condition.name in title.text


def test_consultation_end_date(response):
    """
    Test the date of the end of the consultation period is displayed.
    """
    review = response.context["review"]
    message = _("This consultation closes on %s" % review.consultation_end_display())
    assert str(message) in response.text
