from django.urls import reverse

import pytest

from nsc.document.models import Document
from nsc.utils.datetime import get_today
from nsc.utils.markdown import convert


# All tests require the database


pytestmark = pytest.mark.django_db


supporting_document_types = [
    Document.TYPE.cover_sheet,
    Document.TYPE.evidence_review,
    Document.TYPE.evidence_map,
    Document.TYPE.cost,
    Document.TYPE.systematic,
    Document.TYPE.other,
]


non_supporting_document_types = set(Document.TYPE._db_values) ^ set(
    supporting_document_types
)


def test_view__no_user(make_review, test_access_no_user):
    review = make_review()
    test_access_no_user(url=reverse("review:publish", kwargs={"slug": review.slug}))


def test_view__incorrect_permission(make_review, test_access_forbidden):
    review = make_review()
    test_access_forbidden(url=reverse("review:publish", kwargs={"slug": review.slug}))


def test_response_is_no_recommendations_are_not_updated(
    erm_user, make_review, make_policy, make_review_recommendation, django_app
):
    first_policy = make_policy(name="first", recommendation=False)
    second_policy = make_policy(name="second", recommendation=True)
    review = make_review(policies=[first_policy, second_policy])

    make_review_recommendation(policy=first_policy, review=review, recommendation=True)
    make_review_recommendation(
        policy=second_policy, review=review, recommendation=False
    )

    response = django_app.get(
        reverse("review:publish", kwargs={"slug": review.slug}), user=erm_user
    )

    form = response.form
    form["published"] = False
    form.submit()

    first_policy.refresh_from_db()
    second_policy.refresh_from_db()
    assert first_policy.recommendation is False
    assert second_policy.recommendation is True


def test_response_is_no_summaries_are_not_updated(
    erm_user, make_review, make_policy, make_summary_draft, django_app
):
    first_policy = make_policy(
        name="first", summary="first summary", summary_html=convert("first summary")
    )
    second_policy = make_policy(
        name="second", summary="second summary", summary_html=convert("second summary")
    )
    review = make_review(policies=[first_policy, second_policy])

    make_summary_draft(
        policy=first_policy, review=review, text="**new** ~first~ `summary`"
    )
    make_summary_draft(
        policy=second_policy, review=review, text="**new** ~second~ `summary`"
    )

    response = django_app.get(
        reverse("review:publish", kwargs={"slug": review.slug}), user=erm_user
    )

    form = response.form
    form["published"] = False
    form.submit()

    first_policy.refresh_from_db()
    second_policy.refresh_from_db()
    assert first_policy.summary == "first summary"
    assert first_policy.summary_html == convert("first summary")
    assert second_policy.summary == "second summary"
    assert second_policy.summary_html == convert("second summary")


@pytest.mark.parametrize("doc_type", Document.TYPE._db_values)
def test_response_is_no_documents_arent_updated(
    erm_user, doc_type, make_review, make_policy, make_document, django_app
):
    first_policy = make_policy(name="first")
    second_policy = make_policy(name="second")
    review = make_review(policies=[first_policy, second_policy])

    doc = make_document(review=review, document_type=doc_type)

    response = django_app.get(
        reverse("review:publish", kwargs={"slug": review.slug}), user=erm_user
    )

    form = response.form
    form["published"] = False
    form.submit()

    doc.refresh_from_db()
    assert not doc.policies.exists()


def test_response_is_yes_recommendations_are_updated(
    erm_user, make_review, make_policy, make_review_recommendation, django_app
):
    first_policy = make_policy(name="first", recommendation=False)
    second_policy = make_policy(name="second", recommendation=True)
    review = make_review(policies=[first_policy, second_policy])

    make_review_recommendation(policy=first_policy, review=review, recommendation=True)
    make_review_recommendation(
        policy=second_policy, review=review, recommendation=False
    )

    response = django_app.get(
        reverse("review:publish", kwargs={"slug": review.slug}), user=erm_user
    )

    form = response.form
    form["published"] = True
    form.submit()

    first_policy.refresh_from_db()
    second_policy.refresh_from_db()
    assert first_policy.recommendation is True
    assert second_policy.recommendation is False


def test_response_is_yes_no_review_end_set(
    erm_user, make_review, make_policy, make_review_recommendation, django_app
):
    first_policy = make_policy(name="first", recommendation=False)
    second_policy = make_policy(name="second", recommendation=True)
    review = make_review(policies=[first_policy, second_policy], review_end=None)

    make_review_recommendation(policy=first_policy, review=review, recommendation=True)
    make_review_recommendation(
        policy=second_policy, review=review, recommendation=False
    )

    response = django_app.get(
        reverse("review:publish", kwargs={"slug": review.slug}), user=erm_user
    )

    form = response.form
    form["published"] = True
    form.submit()

    review.refresh_from_db()
    assert review.review_end == get_today()


def test_response_is_yes_summaries_not_updated(
    erm_user, make_review, make_policy, make_summary_draft, django_app
):
    first_policy = make_policy(
        name="first", summary="first summary", summary_html=convert("first summary")
    )
    second_policy = make_policy(
        name="second", summary="second summary", summary_html=convert("second summary")
    )
    review = make_review(policies=[first_policy, second_policy])

    make_summary_draft(
        policy=first_policy, review=review, text="**new** ~first~ `summary`"
    )
    make_summary_draft(
        policy=second_policy, review=review, text="**new** ~second~ `summary`"
    )

    response = django_app.get(
        reverse("review:publish", kwargs={"slug": review.slug}), user=erm_user
    )

    form = response.form
    form["published"] = True
    form.submit()

    first_policy.refresh_from_db()
    second_policy.refresh_from_db()
    assert first_policy.summary == "**new** ~first~ `summary`"
    assert first_policy.summary_html == convert("**new** ~first~ `summary`")
    assert second_policy.summary == "**new** ~second~ `summary`"
    assert second_policy.summary_html == convert("**new** ~second~ `summary`")


@pytest.mark.parametrize("doc_type", supporting_document_types)
def test_response_is_yes_supporting_documents_are_updated(
    erm_user, doc_type, make_review, make_policy, make_document, django_app
):
    first_policy = make_policy(name="first")
    second_policy = make_policy(name="second")
    review = make_review(policies=[first_policy, second_policy])

    doc = make_document(review=review, document_type=doc_type)

    response = django_app.get(
        reverse("review:publish", kwargs={"slug": review.slug}), user=erm_user
    )

    form = response.form
    form["published"] = True
    form.submit()

    doc.refresh_from_db()
    assert set(doc.policies.values_list("id", flat=True)) == {
        first_policy.id,
        second_policy.id,
    }


@pytest.mark.parametrize("doc_type", non_supporting_document_types)
def test_response_is_yes_non_supporting_documents_arent_updated(
    erm_user, doc_type, make_review, make_policy, make_document, django_app
):
    first_policy = make_policy(name="first")
    second_policy = make_policy(name="second")
    review = make_review(policies=[first_policy, second_policy])

    doc = make_document(review=review, document_type=doc_type)

    response = django_app.get(
        reverse("review:publish", kwargs={"slug": review.slug}), user=erm_user
    )

    form = response.form
    form["published"] = True
    form.submit()

    doc.refresh_from_db()
    assert not doc.policies.exists()
