from django.urls import reverse

import pytest

from nsc.review.models import Review


# All tests require the database
pytestmark = pytest.mark.django_db


def test_view(make_review, django_app):
    """
    Test that the page can be displayed.
    """
    review = make_review()
    response = django_app.get(
        reverse("review:add-review-documents", kwargs={"slug": review.slug})
    )
    assert response.status == "200 OK"


@pytest.mark.parametrize(
    "review_type,expected_field",
    (
        (Review.TYPE.evidence, "evidence_review"),
        (Review.TYPE.map, "evidence_map"),
        (Review.TYPE.cost, "cost_effective_model"),
        (Review.TYPE.systematic, "systematic_review"),
    ),
)
def review_has_types_set_only_correct_fields_are_shown(
    review_type, expected_field, make_review, django_app
):
    review = make_review(review_type=[review_type])
    response = django_app.get(
        reverse("review:add-review-documents", kwargs={"slug": review.slug})
    )
    assert "cover_sheet" in response.form
    assert expected_field in response.form
