from django.urls import reverse

import pytest
from model_bakery import baker

from nsc.policy.models import Policy

from ..models import Organisation


# All tests require the database
pytestmark = pytest.mark.django_db

organisation_list_url = reverse("organisation:list")


def test_list_view(django_app):
    """
    Test that the list view returns the list of policies.
    """
    instance = baker.make(Organisation)
    response = django_app.get(organisation_list_url)
    assert response.status == "200 OK"
    assert instance in response.context["object_list"]
    assert not response.context["is_paginated"]
    assert response.context["paginator"].num_pages == 1


@pytest.mark.parametrize("num_organisations", [1, 9])
def test_list_view_query_count(
    num_organisations, django_app, django_assert_num_queries
):
    """
    Test that fetching the list takes a fixed number of queries.
    """
    baker.make(Organisation, _quantity=num_organisations)
    with django_assert_num_queries(3):
        django_app.get(organisation_list_url)


def test_list_view_is_paginated(django_app):
    """
    Test response is paginated.
    """
    baker.make(Organisation, _quantity=50)
    response = django_app.get(organisation_list_url)
    assert response.context["is_paginated"]
    assert response.context["paginator"].num_pages > 1


def test_search_form_blank(django_app):
    """
    Test that the fields in the search form are initially blank.
    """
    form = django_app.get(organisation_list_url).form
    assert form["name"].value == ""
    assert form["condition"].value == ""


def test_search_on_organisation_name(django_app_form):
    """
    Test the list of policies can be filtered by the organisation name.
    """
    baker.make(Policy, name="name")
    response = django_app_form(organisation_list_url, name="other")
    assert not response.context["object_list"]


def test_search_on_condition_name(django_app_form):
    """
    Test the list of policies can be filtered by the name of the condition
    they are interested in.
    """
    instance = baker.make(Organisation)
    instance.policies.add(baker.make(Policy))
    response = django_app_form(organisation_list_url, condition="Other")
    assert not response.context["object_list"]


def test_search_form_shows_name_term(django_app_form):
    """
    Test when the search results are shown the form shows the entered organisation name.
    """
    form = django_app_form(organisation_list_url, name="name").form
    assert form["name"].value == "name"
    assert form["condition"].value == ""


def test_search_form_shows_condition_term(django_app_form):
    """
    Test when the search results are shown the form shows the selected condition.
    """
    form = django_app_form(organisation_list_url, condition="other").form
    assert form["name"].value == ""
    assert form["condition"].value == "other"
