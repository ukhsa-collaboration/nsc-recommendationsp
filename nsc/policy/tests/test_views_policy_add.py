import datetime

from django.urls import reverse

import pytest
from model_bakery import baker

from nsc.policy.models import Policy
from nsc.utils.datetime import get_today
from nsc.utils.markdown import convert


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture()
def policy():
    return baker.make(Policy, is_active=False)


def test_add_start_view(erm_user, django_app):
    response = django_app.get(reverse("policy:add:start"), user=erm_user)
    assert response.status == "200 OK"


def test_add_start_view__no_user(test_access_no_user):
    test_access_no_user(url=reverse("policy:add:start"))


def test_add_start_view__incorrect_permission(test_access_forbidden):
    test_access_forbidden(url=reverse("policy:add:start"))


def test_add_start_view__created(erm_user, django_app):
    start = django_app.get(reverse("policy:add:start"), user=erm_user)
    start_form = start.form

    start_form["name"] = "name"
    start_form["condition_type"] = Policy.CONDITION_TYPES.general
    start_form["condition"] = "condition"
    start_form["ages"] = [Policy.AGE_GROUPS.antenatal]
    start_form["keywords"] = "keywords"

    result = start_form.submit()

    assert result.status == "302 Found"
    assert result.url == reverse("policy:add:summary", args=("name",))

    policy = Policy.objects.get(name="name")

    assert policy.condition_type == Policy.CONDITION_TYPES.general
    assert policy.condition == "condition"
    assert policy.condition_html == convert("condition")
    assert policy.ages == [Policy.AGE_GROUPS.antenatal]
    assert policy.keywords == "keywords"
    assert not policy.is_active


def test_add_summary_view(policy, erm_user, django_app):
    response = django_app.get(
        reverse("policy:add:summary", args=(policy.slug,)), user=erm_user
    )
    assert response.status == "200 OK"


def test_add_summary_view__no_user(policy, test_access_no_user):
    test_access_no_user(url=reverse("policy:add:summary", args=(policy.slug,)))


def test_add_summary_view__incorrect_permission(policy, test_access_forbidden):
    test_access_forbidden(url=reverse("policy:add:summary", args=(policy.slug,)))


def test_add_summary_view__updated(policy, erm_user, django_app):
    summary = django_app.get(
        reverse("policy:add:summary", args=(policy.slug,)), user=erm_user
    )
    summary_form = summary.form

    summary_form["summary"] = "summary"
    summary_form["background"] = "background"

    result = summary_form.submit()

    assert result.status == "302 Found"
    assert result.url == reverse("policy:add:recommendation", args=(policy.slug,))

    policy.refresh_from_db()

    assert policy.summary == "summary"
    assert policy.summary_html == convert("summary")
    assert policy.background == "background"
    assert policy.background_html == convert("background")
    assert not policy.is_active


def test_add_recommendation_view(policy, erm_user, django_app):
    response = django_app.get(
        reverse("policy:add:recommendation", args=(policy.slug,)), user=erm_user
    )
    assert response.status == "200 OK"


def test_add_recommendation_view__no_user(policy, test_access_no_user):
    test_access_no_user(url=reverse("policy:add:recommendation", args=(policy.slug,)))


def test_add_recommendation_view__incorrect_permission(policy, test_access_forbidden):
    test_access_forbidden(url=reverse("policy:add:recommendation", args=(policy.slug,)))


def test_add_recommendation_view__updated(policy, erm_user, django_app):
    summary = django_app.get(
        reverse("policy:add:recommendation", args=(policy.slug,)), user=erm_user
    )
    summary_form = summary.form

    summary_form["recommendation"] = True
    summary_form["next_review"] = get_today().year

    result = summary_form.submit()

    assert result.status == "302 Found"
    assert result.url == reverse("review:add") + f"?policy={policy.slug}"

    policy.refresh_from_db()

    assert policy.recommendation
    assert policy.next_review == datetime.date(get_today().year, 1, 1)
    assert policy.is_active
