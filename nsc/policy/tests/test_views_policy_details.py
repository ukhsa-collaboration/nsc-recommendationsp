from django.urls import reverse
from django.utils.translation import ugettext

import pytest
from bs4 import BeautifulSoup
from model_bakery import baker

from nsc.policy.models import Policy
from nsc.review.models import Review


# All tests require the database
pytestmark = pytest.mark.django_db


def test_detail_view(erm_user, django_app):
    """
    Test that we can view an instance via the detail view.
    """
    instance = baker.make(Policy)
    response = django_app.get(instance.get_admin_url(), user=erm_user)
    assert response.context["policy"] == instance


def test_detail_view__when_archived(erm_user, django_app):
    """
    Test that we can view an instance via the detail view when archived.
    """
    instance = baker.make(Policy, archived=True)
    response = django_app.get(instance.get_admin_url(), user=erm_user)
    assert response.context["policy"] == instance


def test_detail_view__no_user(test_access_no_user):
    instance = baker.make(Policy)
    test_access_no_user(url=instance.get_edit_url())


def test_detail_view__incorrect_permission(test_access_forbidden):
    instance = baker.make(Policy)
    test_access_forbidden(url=instance.get_edit_url())


def test_back_link(erm_user, django_app):
    """
    Test the back link returns to the policy list page.
    """
    instance = baker.make(Policy, name="condition", ages="{child}")
    detail = django_app.get(instance.get_admin_url(), user=erm_user)
    results = detail.click(linkid="back-link-id")
    assert results.request.path == reverse("policy:list")


def test_back_link_discards_search_results(erm_user, django_app):
    """
    Test returning to the policy list page discards previous search results.

    NOTE: In the current design, search is only used to find a condition. The
    search results do not need to be maintained when returning to the policy
    list page.
    """
    instance = baker.make(Policy, name="condition", ages="{child}")
    form = django_app.get(reverse("policy:list"), user=erm_user).forms[1]
    form["name"] = "condition"
    results = form.submit()
    detail = results.click(href=instance.get_admin_url())
    results = detail.click(linkid="back-link-id")
    assert results.request.path == reverse("policy:list")
    assert results.request.environ["QUERY_STRING"] == ""


def test_create_review_button(erm_user, django_app):
    """
    Test that the page contains a link (button) to create a new review for the condition.
    """
    instance = baker.make(Policy, name="name")
    response = django_app.get(instance.get_admin_url(), user=erm_user)
    nodes = BeautifulSoup(response.content, "html.parser")
    link = nodes.find("a", {"id": "create-review-link-id"})
    assert link.text.strip() == ugettext("Create a new product")
    assert link["href"] == "%s?policy=%s" % (reverse("review:add"), instance.slug)


def test_manage_review_button(erm_user, django_app):
    """
    Test that the page contains a link (button) to manage a review for the condition
    if there is a review in progress.
    """
    policy = baker.make(Policy, name="name")
    review = baker.make(Review)
    policy.reviews.add(review)
    response = django_app.get(policy.get_admin_url(), user=erm_user)
    nodes = BeautifulSoup(response.content, "html.parser")
    link = nodes.find("a", {"id": "manage-review-link-id"})
    assert link.text.strip() == ugettext("Manage product")
    assert link["href"] == (reverse("review:detail", kwargs={"slug": review.slug}))


def test_manage_versus_create_button(erm_user, django_app):
    """
    If a review is in progress then the manage button is displayed and the
    create button is not and vice versa.
    """
    policy = baker.make(Policy, name="name")
    response = django_app.get(policy.get_admin_url(), user=erm_user)
    nodes = BeautifulSoup(response.content, "html.parser")
    assert nodes.find("a", {"id": "create-review-link-id"}) is not None
    assert nodes.find("a", {"id": "manage-review-link-id"}) is None
    review = baker.make(Review)
    policy.reviews.add(review)
    response = django_app.get(policy.get_admin_url(), user=erm_user)
    nodes = BeautifulSoup(response.content, "html.parser")
    assert nodes.find("a", {"id": "create-review-link-id"}) is None
    assert nodes.find("a", {"id": "manage-review-link-id"}) is not None
