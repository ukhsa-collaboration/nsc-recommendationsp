from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import pytest
from model_bakery import baker

from nsc.policy.models import Policy
from nsc.utils.datetime import get_date_display


# All tests require the database
pytestmark = pytest.mark.django_db
pytest_plugins = ["nsc.review.tests.fixtures"]


def test_detail_view(django_app):
    """
    Test that we can view an instance via the detail view.
    """
    instance = baker.make(Policy)
    response = django_app.get(instance.get_public_url())
    assert response.context["policy"] == instance


def test_back_link(django_app):
    """
    Test the back link returns to the previous page. This ensures that search results
    are not lost.
    """
    instance = baker.make(Policy, name="condition", ages="{child}")
    form = django_app.get(reverse("condition:list")).form
    form["affects"] = "child"
    results = form.submit()
    detail = results.click(href=instance.get_public_url())
    referer = detail.click(linkid="back-link-id")
    assert results.request.url == referer.request.url


def test_submission_link_for_review_in_pre_consultation(
    review_in_pre_consultation, django_app
):
    """
    Test the link to submit a comment is not visible when a review is
    in the pre-consultation phase.
    """
    policy = review_in_pre_consultation.policies.first()
    page = django_app.get(policy.get_public_url())
    assert reverse("condition:consultation", kwargs={"slug": policy.slug}) not in page


def test_submission_link_for_review_in_consultation(review_in_consultation, django_app):
    """
    Test the link to submit a comment is not visible when a review is
    in the pre-consultation phase.
    """
    policy = review_in_consultation.policies.first()
    page = django_app.get(policy.get_public_url())
    assert reverse("condition:consultation", kwargs={"slug": policy.slug}) in page


def test_submission_link_for_review_in_post_consultation(
    review_in_post_consultation, django_app
):
    """
    Test the link to submit a comment is not visible when a review is
    in this post-consultation phase.
    """
    policy = review_in_post_consultation.policies.first()
    page = django_app.get(policy.get_public_url())
    assert reverse("condition:consultation", kwargs={"slug": policy.slug}) not in page


def test_submission_link_for_review_is_completed(review_completed, django_app):
    """
    Test the link to submit a comment is not visible when a review has been completed.
    """
    policy = review_completed.policies.first()
    page = django_app.get(policy.get_public_url())
    assert reverse("condition:consultation", kwargs={"slug": policy.slug}) not in page


def test_submission_link_for_published_review(review_published, django_app):
    """
    Test the link to submit a comment is not visible when a review has been published.
    """
    policy = review_published.policies.first()
    page = django_app.get(policy.get_public_url())
    assert reverse("condition:consultation", kwargs={"slug": policy.slug}) not in page


def test_consultation_closing_date(review_in_consultation, django_app):
    """
    Test the closing date is shown for a review in the consultation phase.
    """
    policy = review_in_consultation.policies.first()
    page = django_app.get(policy.get_public_url())
    date = get_date_display(review_in_consultation.consultation_end)
    assert str(_("Closing date: %s" % date)) in page
