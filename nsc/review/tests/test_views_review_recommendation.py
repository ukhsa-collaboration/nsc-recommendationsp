from django.urls import reverse

import pytest

# All tests require the database
from nsc.review.models import ReviewRecommendation


pytestmark = pytest.mark.django_db


def test_view(erm_user, make_review, django_app):
    """
    Test that the page can be displayed.
    """
    review = make_review()
    response = django_app.get(
        reverse("review:recommendation", kwargs={"slug": review.slug}), user=erm_user
    )
    assert response.status == "200 OK"


def test_view__no_user(make_review, test_access_no_user):
    review = make_review()
    test_access_no_user(
        url=reverse("review:recommendation", kwargs={"slug": review.slug})
    )


def test_view__incorrect_permission(make_review, test_access_forbidden):
    review = make_review()
    test_access_forbidden(
        url=reverse("review:recommendation", kwargs={"slug": review.slug})
    )


def test_view__not_user(make_review, test_access_not_user):
    review = make_review()
    test_access_not_user(
        url=reverse("review:recommendation", kwargs={"slug": review.slug})
    )


def test_not_all_recommendations_are_updated_errors_are_raised(
    erm_user, make_review, make_policy, django_app
):
    first_policy = make_policy(name="first", summary="")
    second_policy = make_policy(name="second", summary="")
    review = make_review(policies=[first_policy, second_policy])

    response = django_app.get(
        reverse("review:recommendation", kwargs={"slug": review.slug}), user=erm_user
    )

    form = response.form
    form["recommendation-0-recommendation"] = True
    form.submit()

    assert (
        ReviewRecommendation.objects.filter(review=review, policy=first_policy)
        .first()
        .recommendation
        is None
    )
    assert (
        ReviewRecommendation.objects.filter(review=review, policy=second_policy)
        .first()
        .recommendation
        is None
    )


def test_all_recommendations_are_set_values_are_updated(
    erm_user, make_review, make_policy, django_app
):
    first_policy = make_policy(name="first")
    second_policy = make_policy(name="second")
    review = make_review(policies=[first_policy, second_policy])

    response = django_app.get(
        reverse("review:recommendation", kwargs={"slug": review.slug}), user=erm_user
    )

    form = response.form
    form["recommendation-0-recommendation"] = True
    form["recommendation-1-recommendation"] = False
    form.submit()

    first_rec = ReviewRecommendation.objects.filter(
        review=review, policy=first_policy
    ).first()
    second_rec = ReviewRecommendation.objects.filter(
        review=review, policy=second_policy
    ).first()
    assert first_rec.recommendation is True
    assert second_rec.recommendation is False
