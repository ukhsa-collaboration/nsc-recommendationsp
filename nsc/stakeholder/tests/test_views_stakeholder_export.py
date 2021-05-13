import csv
import io

from django.urls import reverse

import pytest
from model_bakery import baker

from nsc.contact.models import Contact
from nsc.policy.models import Policy

from ..models import Stakeholder


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def url():
    return reverse("stakeholder:export")


@pytest.fixture
def response(url, erm_user, django_app):
    return django_app.get(url, user=erm_user)


def test_export_view(response):
    """
    Test that the export view returns form.
    """
    baker.make(Stakeholder, name="name", _quantity=10)
    assert response.status == "200 OK"


def test_export_view__no_user(url, test_access_no_user):
    test_access_no_user(url=url)


def test_export_view__incorrect_permission(url, test_access_forbidden):
    test_access_forbidden(url=url)


@pytest.mark.parametrize("num_stakeholders", [1, 9])
def test_list_view_query_count(
    url, erm_user, num_stakeholders, django_app, django_assert_num_queries
):
    """
    Test that fetching the export takes a fixed number of queries.
    """
    baker.make(Stakeholder, _quantity=num_stakeholders)
    django_app.get("/", user=erm_user)  # login before test
    with django_assert_num_queries(9):  # 5 for view, 4 for login.
        django_app.get(url, user=erm_user)


def test_export_on_no_filter(url, erm_user, django_app):
    """
    Test the export of stakeholders can be filtered by the stakeholder name.
    """
    baker.make(Stakeholder, name="name")
    baker.make(Stakeholder, name="other")
    response = django_app.get(url, user=erm_user)
    assert response.context["total"] == 2
    assert len(response.context["object_list"]) == 2


def test_export_on_stakeholder_name(url, erm_user, django_app):
    """
    Test the export of stakeholders can be filtered by the stakeholder name.
    """
    baker.make(Stakeholder, name="name")
    expected = baker.make(Stakeholder, name="other")
    response = django_app.get(url + "?name=other", user=erm_user)
    assert response.context["total"] == 2
    assert len(response.context["object_list"]) == 1
    assert response.context["object_list"][0].pk == expected.pk


def test_export_on_condition_name(url, erm_user, django_app):
    """
    Test the export of stakeholders can be filtered by the name of the condition
    they are interested in.
    """
    instance = baker.make(Stakeholder)
    instance.policies.add(baker.make(Policy))
    expected = baker.make(Stakeholder)
    expected.policies.add(baker.make(Policy, name="other"))
    response = django_app.get(url + "?condition=other", user=erm_user)
    assert response.context["total"] == 2
    assert len(response.context["object_list"]) == 1
    assert response.context["object_list"][0].pk == expected.pk


def test_export_on_stakeholder_country(url, erm_user, django_app):
    """
    Test the export of stakeholders can be filtered by the stakeholder country.
    """
    expected = baker.make(Stakeholder, countries=[Stakeholder.COUNTRY_ENGLAND])
    baker.make(Stakeholder, countries=[Stakeholder.COUNTRY_NORTHERN_IRELAND])
    response = django_app.get(
        f"{url}?country={Stakeholder.COUNTRY_ENGLAND}", user=erm_user
    )

    assert response.context["total"] == 2
    assert len(response.context["object_list"]) == 1
    assert response.context["object_list"][0].pk == expected.pk


def test_export_mailto(url, erm_user, django_app):
    """
    Test the export of stakeholders shows a mailto link
    """
    instance = baker.make(Stakeholder, name="name")
    baker.make(Contact, email="1@email.com", stakeholder=instance)
    baker.make(Contact, email="2@email.com", stakeholder=instance)

    response = django_app.get(url, user=erm_user)

    assert "mailto:1@email.com,2@email.com" in response.text


def test_export_mailto__exceeds(url, erm_user, django_app):
    """
    Test the export of stakeholders shows a mailto link
    """
    instance = baker.make(Stakeholder, name="name")

    baker.make(
        Contact, email="abcdefghijklm@email.com", stakeholder=instance, _quantity=100
    )

    response = django_app.get(url, user=erm_user)

    assert "mailto:" not in response.text
    assert "Too many emails to provide a mailto link" in response.text


def test_export_conditions(url, erm_user, django_app):
    """
    Test the export of stakeholders returns csv for conditions.
    """
    instance = baker.make(
        Stakeholder,
        name="name",
        countries=[Stakeholder.COUNTRY_ENGLAND],
        url="url.com",
        twitter="@test",
        comments="comments",
    )
    instance.policies.add(baker.make(Policy, name="condition 1"))

    other_instance = baker.make(
        Stakeholder,
        name="other",
        countries=[Stakeholder.COUNTRY_ENGLAND, Stakeholder.COUNTRY_INTERNATIONAL],
        url="url.com",
        twitter="@test2",
        comments="comments",
        is_public=1,
    )
    other_instance.policies.add(baker.make(Policy, name="condition 2"))

    response = django_app.get(url, user=erm_user)
    form = response.forms[1]
    form["export_type"] = "conditions"
    result = form.submit()

    assert result.status == "200 OK"
    assert result.content_type == "text/csv"

    content = result.content.decode("utf-8")
    cvs_reader = csv.reader(io.StringIO(content))
    body = list(cvs_reader)
    headers = body.pop(0)

    assert headers == [
        "Stakeholder name",
        "Stakeholder Type",
        "Country: England",
        "Country: Northern Ireland",
        "Country: Scotland",
        "Country: Wales",
        "Country: UK",
        "Country: International",
        "Website",
        "Twitter",
        "Comments",
        "Show on website",
        "Conditions interested in",
    ]
    assert body == [
        [
            "name",
            instance.get_type_display(),
            "y",
            "",
            "",
            "",
            "",
            "",
            "url.com",
            "@test",
            "comments",
            "",
            "condition 1",
        ],
        [
            "other",
            other_instance.get_type_display(),
            "y",
            "",
            "",
            "",
            "",
            "y",
            "url.com",
            "@test2",
            "comments",
            "y",
            "condition 2",
        ],
    ]


def test_export_individual(url, erm_user, django_app):
    """
    Test the export of stakeholders returns csv for individual.
    """
    instance = baker.make(Stakeholder, name="name")
    baker.make(
        Contact,
        stakeholder=instance,
        name="name contact",
        email="name@email.com",
        role="role",
        phone="123",
    )

    other_instance = baker.make(Stakeholder, name="other")
    baker.make(
        Contact,
        stakeholder=other_instance,
        name="other contact",
        email="other@email.com",
        role="role",
        phone="123",
    )

    response = django_app.get(url, user=erm_user)
    form = response.forms[1]
    form["export_type"] = "individual"
    result = form.submit()

    assert result.status == "200 OK"
    assert result.content_type == "text/csv"

    content = result.content.decode("utf-8")
    cvs_reader = csv.reader(io.StringIO(content))
    body = list(cvs_reader)
    headers = body.pop(0)

    assert headers == [
        "Stakeholder name",
        "Contact Name",
        "Contact Email",
        "Contact Role",
        "Contact Phone",
    ]
    assert body == [
        ["name", "name contact", "name@email.com", "role", "123"],
        ["other", "other contact", "other@email.com", "role", "123"],
    ]


@pytest.mark.parametrize("num_stakeholders", [1, 9])
def test_export_conditions_query_count(
    url, erm_user, num_stakeholders, django_app, django_assert_num_queries
):
    """
    Test that fetching the export takes a fixed number of queries.
    """
    stakeholders = baker.make(Stakeholder, _quantity=num_stakeholders)
    for stakeholder in stakeholders:
        stakeholder.policies.add(baker.make(Policy))

    response = django_app.get(url, user=erm_user)
    with django_assert_num_queries(7):  # 3 for export, 4 for session
        form = response.forms[1]
        form["export_type"] = "conditions"
        form.submit()


@pytest.mark.parametrize("num_stakeholders", [1, 9])
def test_export_individual_query_count(
    url, erm_user, num_stakeholders, django_app, django_assert_num_queries
):
    """
    Test that fetching the export takes a fixed number of queries.
    """
    stakeholders = baker.make(Stakeholder, _quantity=num_stakeholders)
    for stakeholder in stakeholders:
        stakeholder.policies.add(baker.make(Policy))

    response = django_app.get(url, user=erm_user)
    with django_assert_num_queries(7):  # 3 for export, 4 for session
        form = response.forms[1]
        form["export_type"] = "individual"
        form.submit()
