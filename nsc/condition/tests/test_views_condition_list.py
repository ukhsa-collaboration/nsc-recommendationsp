from django.urls import reverse

import pytest
from model_bakery import baker

from nsc.policy.models import Policy


# All tests require the database
pytestmark = pytest.mark.django_db

condition_list_url = reverse("condition:list")


def test_list_view(django_app):
    """
    Test that the list view returns the list of policies.
    """
    instance = baker.make(Policy)
    response = django_app.get(condition_list_url)
    assert instance in response.context["object_list"]
    assert not response.context["is_paginated"]
    assert response.context["paginator"].num_pages == 1


@pytest.mark.parametrize("num_policies", [1, 9])
def test_list_view_query_count(num_policies, django_app, django_assert_num_queries):
    """
    Test that fetching the list takes a fixed number of queries.
    """
    baker.make(Policy, _quantity=num_policies)
    with django_assert_num_queries(2):
        django_app.get(condition_list_url)


def test_list_view_is_paginated(django_app):
    """
    Test response is paginated.
    """
    baker.make(Policy, _quantity=50)
    response = django_app.get(condition_list_url)
    assert response.context["is_paginated"]
    assert response.context["paginator"].num_pages > 1


def test_search_form_blank(django_app):
    """
    Test that the fields in the search form are initially blank.
    """
    form = django_app.get(condition_list_url).form
    assert form["name"].value == ""
    assert form["affects"].value is None
    assert form["screen"].value is None


def test_search_on_condition_name(django_app_form):
    """
    Test the list of policies can be filtered by the condition name.
    """
    baker.make(Policy, name="name")
    response = django_app_form(condition_list_url, name="other")
    assert not response.context["object_list"]


def test_search_on_age_affected(django_app_form):
    """
    Test the list of policies can be filtered by the age of those affected.
    """
    baker.make(Policy, ages="{adult}")
    response = django_app_form(condition_list_url, affects="child")
    assert not response.context["object_list"]


def test_search_on_recommendation(django_app_form):
    """
    Test the list of policies can be filtered by whether the condition is
    screened for or not.
    """
    baker.make(Policy, is_screened=False)
    response = django_app_form(condition_list_url, screen="yes")
    assert not response.context["object_list"]


def test_search_form_shows_name_term(django_app_form):
    """
    Test when the search results are shown the form shows the entered condition name.
    """
    form = django_app_form(condition_list_url, name="name").form
    assert form["name"].value == "name"
    assert form["affects"].value is None
    assert form["screen"].value is None


def test_search_form_shows_affects_term(django_app_form):
    """
    Test when the search results are shown the form shows the selected age.
    """
    form = django_app_form(condition_list_url, affects="child").form
    assert form["name"].value == ""
    assert form["affects"].value == "child"
    assert form["screen"].value is None


def test_search_form_shows_screen_term(django_app_form):
    """
    Test when the search results are shown the form shows the selected recommendation.
    """
    form = django_app_form(condition_list_url, screen="no").form
    assert form["name"].value == ""
    assert form["affects"].value is None
    assert form["screen"].value == "no"
