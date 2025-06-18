from django.urls import reverse

import pytest
from unittest.mock import patch
from nsc.review.models import Review


# All tests require the database
pytestmark = pytest.mark.django_db

# @pytest.fixture(autouse=True)
# def patch_virus_scanner(monkeypatch):
#     monkeypatch.setattr("nsc.utils.virus_scanner.is_file_clean", lambda f: True)

# def test_patch(monkeypatch):
#     from nsc.utils.virus_scanner import is_file_clean
#     assert is_file_clean("dummy") is True

def test_view(erm_user, make_review, django_app):
    """
    Test that the page can be displayed.
    """
    review = make_review()
    response = django_app.get(
        reverse("review:add-review-documents", kwargs={"slug": review.slug}),
        user=erm_user,
    )
    assert response.status == "200 OK"


def test_view__no_user(make_review, test_access_no_user):
    review = make_review()
    test_access_no_user(
        url=reverse("review:add-review-documents", kwargs={"slug": review.slug}),
    )


def test_view__incorrect_permission(make_review, test_access_forbidden):
    review = make_review()
    test_access_forbidden(
        url=reverse("review:add-review-documents", kwargs={"slug": review.slug}),
    )

@patch("nsc.utils.virus_scanner.is_file_clean", return_value=True)
def test_success_url(erm_user, make_review, django_app, minimal_pdf):
    """
    Test success url on submit.
    """
    review = make_review(slug="abc")
    response = django_app.get(
        reverse("review:add-review-documents", kwargs={"slug": review.slug}),
        user=erm_user,
    )
    form = response.forms[1]
    form["cover_sheet"] = (
        "document.pdf",
        minimal_pdf.encode(),
        "application/pdf",
    )
    actual = form.submit().follow()
    assert actual.request.path == reverse("review:detail", kwargs={"slug": review.slug})


def test_success_url__next(erm_user, make_review, django_app, minimal_pdf):
    """
    Test success url is next when provided.
    """
    review = make_review(slug="abc")
    response = django_app.get(
        reverse("review:add-review-documents", kwargs={"slug": review.slug})
        + "?next=/",
        user=erm_user,
    )
    form = response.forms[1]
    form["cover_sheet"] = (
        "document.pdf",
        minimal_pdf.encode(),
        "application/pdf",
    )
    actual = form.submit().follow()
    assert actual.request.path == "/"


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
    erm_user, review_type, expected_field, make_review, django_app
):
    review = make_review(review_type=[review_type])
    response = django_app.get(
        reverse("review:add-review-documents", kwargs={"slug": review.slug}),
        user=erm_user,
    )
    assert "cover_sheet" in response.forms[1]
    assert expected_field in response.forms[1]
