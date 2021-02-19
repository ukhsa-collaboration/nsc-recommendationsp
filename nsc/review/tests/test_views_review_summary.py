from django.urls import reverse

import pytest

# All tests require the database
from nsc.review.models import SummaryDraft


pytestmark = pytest.mark.django_db


def test_view(erm_user, make_review, django_app):
    """
    Test that the page can be displayed.
    """
    review = make_review()
    response = django_app.get(
        reverse("review:summary", kwargs={"slug": review.slug}), user=erm_user
    )
    assert response.status == "200 OK"


def test_view__no_user(make_review, test_access_no_user):
    review = make_review()
    test_access_no_user(url=reverse("review:summary", kwargs={"slug": review.slug}))


def test_view__incorrect_permission(make_review, test_access_forbidden):
    review = make_review()
    test_access_forbidden(url=reverse("review:summary", kwargs={"slug": review.slug}))


def test_view__not_user(make_review, test_access_not_user):
    review = make_review()
    test_access_not_user(url=reverse("review:summary", kwargs={"slug": review.slug}))


def test_not_all_summaries_are_updated_errors_are_raised(
    erm_user, make_review, make_policy, django_app
):
    first_policy = make_policy(name="first", summary="")
    second_policy = make_policy(name="second", summary="")
    review = make_review(policies=[first_policy, second_policy])

    response = django_app.get(
        reverse("review:summary", kwargs={"slug": review.slug}), user=erm_user
    )

    form = response.form
    form["summary-0-text"] = "first content"
    form.submit()

    assert (
        SummaryDraft.objects.filter(review=review, policy=first_policy).first().text
        == ""
    )
    assert (
        not SummaryDraft.objects.filter(review=review, policy=first_policy)
        .first()
        .updated
    )
    assert (
        SummaryDraft.objects.filter(review=review, policy=second_policy).first().text
        == ""
    )
    assert (
        not SummaryDraft.objects.filter(review=review, policy=second_policy)
        .first()
        .updated
    )


def test_default_value_is_the_original_policy_summary(
    erm_user, make_review, make_policy, django_app
):
    first_policy = make_policy(name="first", summary="orig first content")
    second_policy = make_policy(name="second", summary="orig second content")
    review = make_review(policies=[first_policy, second_policy])

    response = django_app.get(
        reverse("review:summary", kwargs={"slug": review.slug}), user=erm_user
    )

    form = response.form
    form["summary-0-text"] = "first content"
    form.submit()

    first_draft = SummaryDraft.objects.filter(
        review=review, policy=first_policy
    ).first()
    second_draft = SummaryDraft.objects.filter(
        review=review, policy=second_policy
    ).first()
    assert first_draft.text == "first content"
    assert first_draft.updated
    assert second_draft.text == "orig second content"
    assert second_draft.updated
