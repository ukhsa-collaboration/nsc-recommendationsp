from django.urls import reverse

import pytest
from model_bakery import baker

from nsc.policy.models import Policy


# All tests require the database
pytestmark = pytest.mark.django_db


def test_detail_view(django_app):
    """
    Test that we can view an instance via the detail view.
    """
    instance = baker.make(Policy)
    response = django_app.get(reverse("policy:edit", kwargs={"slug": instance.slug}))
    assert response.context["policy"] == instance


def test_back_link(django_app):
    """
    Test the back link returns to the previous page. This ensures that search results
    are not lost.
    """
    instance = baker.make(Policy, name="condition", ages="{child}")
    form = django_app.get(reverse("policy:list")).form
    form["name"] = "condition"
    results = form.submit()
    detail = results.click(href=instance.get_admin_url())
    referer = detail.click(linkid="back-link-id")
    assert results.request.url == referer.request.url
