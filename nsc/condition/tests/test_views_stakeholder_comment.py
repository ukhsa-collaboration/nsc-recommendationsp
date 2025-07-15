from urllib.parse import urlsplit

from django.conf import settings
from django.urls import reverse

import pytest
from bs4 import BeautifulSoup

from nsc.notify.models import Email


# All tests require the database

pytestmark = pytest.mark.django_db


@pytest.fixture
def response(review_in_consultation, client):
    policy = review_in_consultation.policies.first()
    url = reverse("condition:stakeholder-comment", kwargs={"slug": policy.slug})
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
    assert (
        reverse(
            "review:review-document-download",
            kwargs={"slug": review.slug, "doc_type": "submission_form"},
        )
        in response.content.decode()
    )


def test_submit(response, client):
    condition = response.context["condition"]

    url = reverse("condition:stakeholder-comment", kwargs={"slug": condition.slug})
    form_data = {
        "name": "name",
        "email": "email@email.com",
        "role": "role",
        "organisation": "organisation",
        "behalf": True,
        "publish": True,
        "comment": "comment",
        "condition": condition.pk,
    }

    result = client.post(url, form_data)
    assert result.status_code == 302

    expected = reverse(
        "condition:stakeholder-comment-submitted", args=(condition.slug,)
    )
    actual = result.url
    assert urlsplit(actual)._replace(fragment="") == urlsplit(expected)

    assert (
        Email.objects.filter(
            address=settings.CONSULTATION_COMMENT_ADDRESS,
            template_id=settings.NOTIFY_TEMPLATE_STAKEHOLDER_COMMENT,
        ).count()
        == 1
    )
