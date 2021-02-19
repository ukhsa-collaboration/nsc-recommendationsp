from django.urls import reverse

import pytest
from model_bakery import baker

from nsc.policy.models import Policy

from ..models import Stakeholder


# All tests require the database
pytestmark = pytest.mark.django_db

stakeholder_list_url = reverse("stakeholder:list")


def test_list_view(erm_user, django_app):
    """
    Test that the list view returns the list of policies.
    """
    instance = baker.make(Stakeholder)
    response = django_app.get(stakeholder_list_url, user=erm_user)
    assert response.status == "200 OK"
    assert instance in response.context["object_list"]
    assert not response.context["is_paginated"]
    assert response.context["paginator"].num_pages == 1


def test_list_view__no_user(test_access_no_user):
    test_access_no_user(url=stakeholder_list_url)


def test_list_view__incorrect_permission(test_access_forbidden):
    test_access_forbidden(url=stakeholder_list_url)


@pytest.mark.parametrize("num_stakeholders", [1, 9])
def test_list_view_query_count(
    erm_user, num_stakeholders, django_app, django_assert_num_queries
):
    """
    Test that fetching the list takes a fixed number of queries.
    """
    baker.make(Stakeholder, _quantity=num_stakeholders)
    django_app.get("/", user=erm_user)  # login before test
    with django_assert_num_queries(8):  # 4 for view, 4 for login.
        django_app.get(stakeholder_list_url, user=erm_user)


def test_list_view_is_paginated(erm_user, django_app):
    """
    Test response is paginated.
    """
    baker.make(Stakeholder, _quantity=50)
    response = django_app.get(stakeholder_list_url, user=erm_user)
    assert response.context["is_paginated"]
    assert response.context["paginator"].num_pages > 1


def test_search_form_blank(erm_user, django_app):
    """
    Test that the fields in the search form are initially blank.
    """
    form = django_app.get(stakeholder_list_url, user=erm_user).form
    assert form["name"].value == ""
    assert form["condition"].value == ""


def test_search_on_stakeholder_name(erm_user, django_app_form):
    """
    Test the list of stakeholders can be filtered by the stakeholder name.
    """
    baker.make(Policy, name="name")
    response = django_app_form(stakeholder_list_url, name="other", user=erm_user)
    assert not response.context["object_list"]


def test_search_on_condition_name(erm_user, django_app_form):
    """
    Test the list of stakeholders can be filtered by the name of the condition
    they are interested in.
    """
    instance = baker.make(Stakeholder)
    instance.policies.add(baker.make(Policy))
    response = django_app_form(stakeholder_list_url, condition="Other", user=erm_user)
    assert not response.context["object_list"]


def test_search_on_stakeholder_country(erm_user, django_app_form):
    """
    Test the list of stakeholders can be filtered by the stakeholder country.
    """
    expected = baker.make(Stakeholder, countries=[Stakeholder.COUNTRY_ENGLAND])
    baker.make(Stakeholder, countries=[Stakeholder.COUNTRY_NORTHERN_IRELAND])
    response = django_app_form(
        stakeholder_list_url, country=Stakeholder.COUNTRY_ENGLAND, user=erm_user
    )

    assert len(response.context["object_list"]) == 1
    assert response.context["object_list"][0].pk == expected.pk


def test_search_form_shows_name_term(erm_user, django_app_form):
    """
    Test when the search results are shown the form shows the entered stakeholder name.
    """
    form = django_app_form(stakeholder_list_url, name="name", user=erm_user).form
    assert form["name"].value == "name"
    assert form["condition"].value == ""


def test_search_form_shows_condition_term(erm_user, django_app_form):
    """
    Test when the search results are shown the form shows the selected condition.
    """
    form = django_app_form(stakeholder_list_url, condition="other", user=erm_user).form
    assert form["name"].value == ""
    assert form["condition"].value == "other"
