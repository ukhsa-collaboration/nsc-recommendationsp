from django.urls import reverse

import pytest
from model_bakery import baker

from ..models import Policy


# All tests require the database
pytestmark = pytest.mark.django_db

policy_list_url = reverse("policy:list")


@pytest.fixture
def django_search(db, django_app):
    def search(url, **form_args):
        """
        Search the given URL with the specified form arguments
        """
        form = django_app.get(url).form
        for field, value in form_args.items():
            form[field] = value
        return form.submit()

    return search


@pytest.fixture
def policy_search(django_search):
    return lambda **form_args: django_search(policy_list_url, **form_args)


def test_list_view(django_app):
    """
    Test that the list view returns the list of policies.
    """
    instance = baker.make(Policy)
    response = django_app.get(policy_list_url)
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
        django_app.get(policy_list_url)


def test_list_view_is_paginated(django_app):
    """
    Test response is paginated.
    """
    baker.make(Policy, _quantity=50)
    response = django_app.get(policy_list_url)
    assert response.context["is_paginated"]
    assert response.context["paginator"].num_pages > 1


def test_search_form_blank(django_app):
    """
    Test that the fields in the search form are initially blank.
    """
    form = django_app.get(policy_list_url).form
    assert form["condition"].value == ""
    assert form["affects"].value is None
    assert form["screen"].value is None


def test_search_on_condition_name(policy_search):
    """
    Test the list of policies can be filtered by the condition name.
    """
    baker.make(Policy, name="condition")
    response = policy_search(condition="other")
    assert not response.context["object_list"]


def test_search_on_age_affected(policy_search):
    """
    Test the list of policies can be filtered by the age of those affected.
    """
    baker.make(Policy, condition__ages="{adult}")
    response = policy_search(affects="child")
    assert not response.context["object_list"]


def test_search_on_recommendation(policy_search):
    """
    Test the list of policies can be filtered by whether the condition is
    screened for or not.
    """
    baker.make(Policy, is_screened=False)
    response = policy_search(screen="yes")
    assert not response.context["object_list"]


def test_search_form_shows_condition_term(policy_search):
    """
    Test when the search results are shown the form shows the entered condition name.
    """
    form = policy_search(condition="name").form
    assert form["condition"].value == "name"
    assert form["affects"].value is None
    assert form["screen"].value is None


def test_search_form_shows_affects_term(policy_search):
    """
    Test when the search results are shown the form shows the selected age.
    """
    form = policy_search(affects="child").form
    assert form["condition"].value == ""
    assert form["affects"].value == "child"
    assert form["screen"].value is None


def test_search_form_shows_screen_term(policy_search):
    """
    Test when the search results are shown the form shows the selected recommendation.
    """
    form = policy_search(screen="no").form
    assert form["condition"].value == ""
    assert form["affects"].value is None
    assert form["screen"].value == "no"
