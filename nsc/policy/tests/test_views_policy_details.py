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
    response = django_app.get(instance.get_admin_url())
    assert response.context["policy"] == instance


def test_back_link(django_app):
    """
    Test the back link returns to the policy list page.
    """
    instance = baker.make(Policy, name="condition", ages="{child}")
    detail = django_app.get(instance.get_admin_url())
    results = detail.click(linkid="back-link-id")
    assert results.request.path == reverse("policy:list")


def test_back_link_discards_search_results(django_app):
    """
    Test returning to the policy list page discards previous search results.

    NOTE: In the current design, search is only used to find a condition. The
    search results do not need to be maintained when returning to the policy
    list page.
    """
    instance = baker.make(Policy, name="condition", ages="{child}")
    form = django_app.get(reverse("policy:list")).form
    form["name"] = "condition"
    results = form.submit()
    detail = results.click(href=instance.get_admin_url())
    results = detail.click(linkid="back-link-id")
    assert results.request.path == reverse("policy:list")
    assert results.request.environ["QUERY_STRING"] == ""
