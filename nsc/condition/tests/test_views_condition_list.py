from django.urls import reverse

import pytest
from dateutil.relativedelta import relativedelta
from model_bakery import baker

from nsc.policy.models import Policy
from nsc.review.models import Review
from nsc.utils.datetime import get_today


# All tests require the database
pytestmark = pytest.mark.django_db

condition_list_url = reverse("condition:list")


def test_list_view(client):
    """
    Test that the list view returns the list of policies.
    """
    instance = baker.make(Policy)
    response = client.get(condition_list_url)
    assert instance in response.context["object_list"]
    assert not response.context["is_paginated"]
    assert response.context["paginator"].num_pages == 1


def test_policy_is_open(client):
    """
    Test a policy is annotated with the current review when it is open
    for public comment
    """
    today = get_today()
    later = get_today() + relativedelta(months=+3)
    policy = baker.make(Policy)
    review = baker.make(Review, consultation_start=today, consultation_end=later)
    policy.reviews.add(review)

    response = client.get(condition_list_url)
    policies = response.context["object_list"]

    assert policy in policies
    assert policies.first().reviews_in_consultation[0].pk == review.pk
    assert "OPEN" in response.content.decode()


def test_policy_is_closed(client):
    """
    Test a policy is not annotated with the current review outside of the
    public consultation period
    """
    tomorrow = get_today() + relativedelta(days=+1)
    later = get_today() + relativedelta(months=+1)
    policy = baker.make(Policy)
    review = baker.make(Review, consultation_start=tomorrow, consultation_end=later)
    policy.reviews.add(review)

    response = client.get(condition_list_url)
    policies = response.context["object_list"]

    assert not policies.first().reviews_in_consultation
    assert "OPEN" not in response.content.decode()


@pytest.mark.parametrize("num_policies", [1, 9])
def test_list_view_query_count(num_policies, client, django_assert_num_queries):
    """
    Test that fetching the list takes a fixed number of queries.
    """
    baker.make(Policy, _quantity=num_policies)
    with django_assert_num_queries(3):
        client.get(condition_list_url)


def test_list_view_is_paginated(client):
    """
    Test response is paginated.
    """
    baker.make(Policy, _quantity=50)
    response = client.get(condition_list_url)
    assert response.context["is_paginated"]
    assert response.context["paginator"].num_pages > 1


def test_search_form_blank(client):
    """
    Test that the fields in the search form are initially blank.
    """
    response = client.get(condition_list_url)
    form = response.context["form"]

    assert form.fields["name"].initial in (None, "")
    assert form.fields["comments"].initial is None
    assert form.fields["affects"].initial is None
    assert form.fields["screen"].initial is None


def test_search_on_condition_name(client):
    """
    Test the list of policies can be filtered by the condition name.
    """
    baker.make(Policy, name="name")
    response = client.get(condition_list_url, {"name": "other"})
    assert not response.context["object_list"]


def test_search_on_open_for_comment(client):
    """
    Test the list of policies can be filtered by whether the policy is
    under review and currently open for the public to comment.
    """
    tomorrow = get_today() + relativedelta(days=+1)
    later = get_today() + relativedelta(months=+3)
    policy = baker.make(Policy, name="name")
    review = baker.make(Review, consultation_start=tomorrow, consultation_end=later)
    policy.reviews.add(review)
    response = client.get(condition_list_url, {"comments": "open"})
    assert not response.context["object_list"]


def test_search_on_age_affected(client):
    """
    Test the list of policies can be filtered by the age of those affected.
    """
    baker.make(Policy, ages="{adult}")
    response = client.get(condition_list_url, {"affects": "child"})
    assert not response.context["object_list"]


def test_search_on_recommendation(client):
    """
    Test the list of policies can be filtered by whether the condition is
    screened for or not.
    """
    baker.make(Policy, recommendation=False)
    response = client.get(condition_list_url, {"screen": "yes"})
    assert not response.context["object_list"]


def test_search_form_shows_name_term(client):
    """
    Test when the search results are shown the form shows the entered condition name.
    """
    response = client.get(condition_list_url, {"name": "name"})
    form = response.context["form"]
    assert form["name"].value() == "name"
    assert form["affects"].value() is None
    assert form["screen"].value() is None


def test_search_form_shows_affects_term(client):
    """
    Test when the search results are shown the form shows the selected age.
    """
    response = client.get(condition_list_url, {"affects": "child"})
    form = response.context["form"]
    assert form["name"].value() is None
    assert form["affects"].value() == "child"
    assert form["screen"].value() is None


def test_search_form_shows_screen_term(client):
    """
    Test when the search results are shown the form shows the selected recommendation.
    """
    response = client.get(condition_list_url, {"screen": "no"})
    form = response.context["form"]
    assert form["name"].value() is None
    assert form["affects"].value() is None
    assert form["screen"].value() == "no"
