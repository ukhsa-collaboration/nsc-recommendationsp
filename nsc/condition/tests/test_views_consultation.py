from django.urls import reverse

import pytest
from bs4 import BeautifulSoup


# All tests require the database
pytestmark = pytest.mark.django_db
pytest_plugins = ["nsc.review.tests.fixtures"]


@pytest.fixture
def response(review_in_consultation, django_app):
    policy = review_in_consultation.policies.first()
    url = reverse("condition:consultation", kwargs={"slug": policy.slug})
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


def test_evidence_review_link(response):
    """
    Test a link to download the evidence review summary is displayed.
    """
    review = response.context["review"]
    assert review.get_evidence_review_url() in response.text


def test_consultation_start_date_is_shown(response):
    """
    Test the date of the start of the consultation period is displayed.

    Note: this is rather a crude test since it does not check the context in
    which the date is displayed.
    """
    review = response.context["review"]
    assert review.consultation_start_display() in response.text


def test_consultation_end_date_is_shown(response):
    """
    Test the date of the end of the consultation period is displayed.

    Note: this is rather a crude test since it does not check the context in
    which the date is displayed. There are two cases where the date is shown,
    first when the dates of the period are reported and second when the reader
    is rem
    """
    review = response.context["review"]
    assert review.consultation_end_display() in response.text
