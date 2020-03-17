from django.urls import reverse

import pytest
from model_bakery import baker

from nsc.policy.models import Policy
from nsc.review.models import Review
from nsc.utils.datetime import get_today


# All tests require the database
pytestmark = pytest.mark.django_db


def test_view(django_app):
    """
    Test that the page can be displayed.
    """
    response = django_app.get(reverse("review:add"))
    assert response.status == "200 OK"


def test_initialize_form_for_policy(django_app):
    """
    Test passing the policy as a query parameter initializes the form.
    """
    policy = baker.make(Policy, name="name", slug="name")
    response = django_app.get("%s?policy=%s" % (reverse("review:add"), policy.slug))
    form = response.context["form"]
    assert form.initial["name"] == "%s %d review" % (policy.name, get_today().year)
    assert form.initial["policies"] == [policy.pk]


def test_review_is_created(django_app):
    """
    Test submitting the form creates a new review for a condition.
    """
    policy = baker.make(Policy, name="name", slug="name")
    assert policy.reviews.count() == 0

    form = django_app.get(reverse("review:add")).form
    form["name"] = "Review"
    form["review_type"] = Review.TYPE.evidence
    form["policies"] = [policy.pk]
    response = form.submit().follow()
    review = response.context["object"]

    assert response.status == "200 OK"
    assert response.request.path == reverse(
        "review:detail", kwargs={"slug": review.slug}
    )
