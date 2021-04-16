from django.conf import settings
from django.urls import reverse

import pytest
from bs4 import BeautifulSoup

from nsc.notify.models import Email


# All tests require the database

pytestmark = pytest.mark.django_db


@pytest.fixture
def response(review_in_consultation, django_app):
    policy = review_in_consultation.policies.first()
    url = reverse("condition:stakeholder-comment", kwargs={"slug": policy.slug})
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
    Test the back link returns to the consultation page.
    """
    policy = response.context["condition"]
    expected = reverse("condition:consultation", kwargs={"slug": policy.slug})
    link = dom.find(id="back-link-id")
    assert link["href"] == expected


def test_heading_caption(response, dom):
    """
    Test the name of the condition is displayed as caption for the page title.
    """
    condition = response.context["condition"]
    title = dom.find("h1")
    assert condition.name in title.text


def test_submission_form_link(response):
    """
    Test a link to submission form for comments is displayed.
    """
    review = response.context["condition"].current_review
    assert review.submission_form.get_download_url() in response.text


def test_submit(response):
    form = response.form

    form["name"] = "name"
    form["email"] = "email@email.com"
    form["role"] = "role"
    form["organisation"] = "organisation"
    form["behalf"] = True
    form["publish"] = True
    form["comment"] = "comment"
    form["condition"] = response.context["condition"].pk

    result = form.submit()

    assert result.status == "302 Found"
    assert result.url == reverse(
        "condition:stakeholder-comment-submitted",
        args=(response.context["condition"].slug,),
    )
    assert (
        Email.objects.filter(
            address=settings.CONSULTATION_COMMENT_ADDRESS,
            template_id=settings.NOTIFY_TEMPLATE_STAKEHOLDER_COMMENT,
        ).count()
        == 1
    )
