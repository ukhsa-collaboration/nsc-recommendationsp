from datetime import date

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

import pytest
from django_webtest import WebTest
from model_bakery import baker

from nsc.policy.models import Policy
from nsc.utils.datetime import get_date_display


# All tests require the database
pytestmark = pytest.mark.django_db


def test_detail_view(client):
    """
    Test that we can view an instance via the detail view.
    """
    instance = baker.make(Policy)
    response = client.get(instance.get_public_url())
    assert response.context["policy"] == instance


def test_consultation_status_for_review_in_pre_consultation(
    review_in_pre_consultation, client
):
    """
    Test the link to submit a comment is not visible when a review is
    in the pre-consultation phase.
    """
    policy = review_in_pre_consultation.policies.first()
    response = client.get(policy.get_public_url())

    html = response.content.decode("utf-8")

    assert reverse("condition:consultation", kwargs={"slug": policy.slug}) not in html
    assert "This condition is currently under review." in html


def test_consultation_status_for_review_in_consultation(review_in_consultation, client):
    """
    Test the link to submit a comment is not visible when a review is
    in the pre-consultation phase.
    """
    policy = review_in_consultation.policies.first()
    response = client.get(policy.get_public_url())

    html = response.content.decode("utf-8")

    assert reverse("condition:consultation", kwargs={"slug": policy.slug}) in html
    assert (
        "The UK NSC is consulting on whether to change its "
        "recommendation on this condition and is accepting public comments."
    ) in html


def test_consultation_status_for_review_in_post_consultation(
    review_in_post_consultation, client
):
    """
    Test the link to submit a comment is not visible when a review is
    in this post-consultation phase.
    """
    policy = review_in_post_consultation.policies.first()
    response = client.get(policy.get_public_url())
    html = response.content.decode("utf-8")

    assert reverse("condition:consultation", kwargs={"slug": policy.slug}) not in html
    assert "We are no longer accepting comments on this condition." in html


def test_consultation_status_for_review_is_completed(review_completed, client):
    """
    Test the link to submit a comment is not visible when a review has been completed.
    """
    policy = review_completed.policies.first()
    page = client.get(policy.get_public_url())
    assert reverse("condition:consultation", kwargs={"slug": policy.slug}) not in page


def test_consultation_status_for_published_review(review_published, client):
    """
    Test the link to submit a comment is not visible when a review has been published.
    """
    policy = review_published.policies.first()
    page = client.get(policy.get_public_url())
    assert reverse("condition:consultation", kwargs={"slug": policy.slug}) not in page


def test_consultation_closing_date(review_in_consultation, client):
    """
    Test the closing date is shown for a review in the consultation phase.
    """
    policy = review_in_consultation.policies.first()
    response = client.get(policy.get_public_url())
    html = response.content.decode("utf-8")
    date = get_date_display(review_in_consultation.consultation_end)

    expected_text = str(_("Closing date: %s" % date))
    assert expected_text in html


def test_consultation_archived(client):
    """
    Test the link to submit a comment is not visible when a review has been published.
    """
    policy = baker.make(Policy, name="condition", archived=True)
    response = client.get(policy.get_public_url())
    html = response.content.decode("utf-8")

    assert (
        "This recommendation has been archived and is no longer regularly reviewed by the UK NSC."
        in html
    )


def test_previous_documents__in_consultation(
    review_in_consultation, make_review, make_review_recommendation, client
):
    """
    Test that the correct number of review documents is shown when in consultation.
    """
    # instance = review_in_consultation.policies.first()
    # for year in [2019, 2018]:
    #     review = make_review(
    #         name="review_a",
    #         review_start=date(year, 1, 1),
    #         review_end=date(year, 2, 1),
    #         published=True,
    #     )
    #     instance.reviews.add(review)
    #     make_review_recommendation(policy=instance, review=review, recommendation=True)

    # page = client.get(instance.get_public_url())
    # assert str("Supporting documents from the 2019 review") in page
    # assert str("Supporting documents from the 2018 review") not in page

    instance = review_in_consultation.policies.first()

    for year in [2019, 2018]:
        review = make_review(
            name="review_a",
            review_start=date(year, 1, 1),
            review_end=date(year, 2, 1),
            published=True,
        )
        instance.reviews.add(review)
        make_review_recommendation(policy=instance, review=review, recommendation=True)

    response = client.get(instance.get_public_url())
    html = response.content.decode("utf-8")

    assert "Supporting documents from the 2019 review" in html
    assert "Supporting documents from the 2018 review" not in html


def test_previous_documents__not_in_consultation(
    make_review, make_review_recommendation, client
):
    """
    Test that the correct number of review documents is shown when not in consultation.
    """
    instance = baker.make(Policy)

    for year in [2019, 2018]:
        review = make_review(
            name="review_a",
            review_start=date(year, 1, 1),
            review_end=date(year, 2, 1),
            published=True,
        )
        instance.reviews.add(review)
        make_review_recommendation(policy=instance, review=review, recommendation=True)

    response = client.get(instance.get_public_url())
    html = response.content.decode("utf-8")

    assert "Supporting documents from the 2019 review" in html
    assert "Supporting documents from the 2018 review" in html


class TestViewConditionDetail(WebTest):
    def test_back_link(self):
        # Create a test Policy instance
        instance = baker.make(Policy, name="condition", ages="{child}")

        # Load the search form page and submit the form
        page = self.app.get(reverse("condition:list"))
        form = page.forms[1]
        form["affects"] = "child"
        results = form.submit()

        # Click the link to the detail page
        detail = results.click(href=instance.get_public_url())

        # Click the "back" link
        referer = detail.click(linkid="back-link-id")

        # Assert that we returned to the search results page
        assert results.request.url == referer.request.url
