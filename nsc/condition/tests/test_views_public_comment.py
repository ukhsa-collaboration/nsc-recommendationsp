from django.conf import settings
from django.urls import reverse

import pytest
from bs4 import BeautifulSoup

from nsc.notify.models import Email
from nsc.subscription.models import Subscription


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def response(review_in_consultation, client):
    policy = review_in_consultation.policies.first()
    url = reverse("condition:public-comment", kwargs={"slug": policy.slug})
    return client.get(url)


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


def test_submit(response):
    form = response.forms[1]

    form["name"] = "name"
    form["email"] = "email@email.com"
    form["notify"] = True
    form["comment_affected"] = "comment_affected"
    form["comment_evidence"] = "comment_evidence"
    form["comment_discussion"] = "comment_discussion"
    form["comment_recommendation"] = "comment_recommendation"
    form["comment_alternatives"] = "comment_alternatives"
    form["comment_other"] = "comment_other"
    form["condition"] = response.context["condition"].pk

    result = form.submit()

    assert result.status == "302 Found"
    assert result.url == reverse(
        "condition:public-comment-submitted", args=(response.context["condition"].slug,)
    )
    assert (
        Email.objects.filter(
            address=settings.CONSULTATION_COMMENT_ADDRESS,
            template_id=settings.NOTIFY_TEMPLATE_PUBLIC_COMMENT,
        ).count()
        == 1
    )

    assert Subscription.objects.count() == 1
    subscription = Subscription.objects.get(email="email@email.com")
    assert subscription.policies.all()[0].pk == response.context["condition"].pk


def test_submit__no_subscribe(response):
    form = response.forms[1]

    form["name"] = "name"
    form["email"] = "email@email.com"
    form["notify"] = False
    form["comment_affected"] = "comment_affected"
    form["comment_evidence"] = "comment_evidence"
    form["comment_discussion"] = "comment_discussion"
    form["comment_recommendation"] = "comment_recommendation"
    form["comment_alternatives"] = "comment_alternatives"
    form["comment_other"] = "comment_other"
    form["condition"] = response.context["condition"].pk

    result = form.submit()

    assert result.status == "302 Found"
    assert result.url == reverse(
        "condition:public-comment-submitted", args=(response.context["condition"].slug,)
    )
    assert (
        Email.objects.filter(
            address=settings.CONSULTATION_COMMENT_ADDRESS,
            template_id=settings.NOTIFY_TEMPLATE_PUBLIC_COMMENT,
        ).count()
        == 1
    )
    assert Subscription.objects.count() == 0
