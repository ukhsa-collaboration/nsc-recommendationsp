from django.core.cache import cache
from django.urls import reverse

import pytest
from dateutil.relativedelta import relativedelta
from model_bakery import baker

from nsc.document.models import Document, document_path
from nsc.utils.datetime import from_today, get_today

from ..models import Review


# All tests require the database
pytestmark = pytest.mark.django_db


def test_factory_create_policy():
    """
    Test that we can create an instance via our object factory.
    """
    instance = baker.make(Review)
    assert isinstance(instance, Review)


def test_slug_is_set():
    """
    Test the slug field, if not set, is set when a Review is created.
    """
    instance = baker.make(Review, name="The Review", slug="")
    assert instance.slug == "the-review"


def test_slug_is_not_overwritten():
    """
    Test that once the slug is set it is not overwritten if the name of the
    policy changes. This ensures that any bookmarked pages still work if the
    name is changed at a later time.
    """
    instance = baker.make(Review, name="The Review", slug="the-review")
    instance.name = "New name"
    instance.save()
    assert instance.slug == "the-review"


def test_default_review_start():
    """
    Test the review_start field defaults to today when a Review is created.
    """
    instance = baker.make(Review)
    assert instance.review_start == get_today()


def test_review_start_is_updated():
    """
    Test the review_start field can be set when a Review is created.
    """
    tomorrow = get_today() + relativedelta(days=+1)
    instance = baker.make(Review, review_start=tomorrow)
    assert instance.review_start == tomorrow


def test_review_start_is_not_updated_later():
    """
    Test the review_start field is not changed if set already.
    """
    tomorrow = get_today() + relativedelta(days=+1)
    instance = baker.make(Review, review_start=tomorrow)
    instance.save()
    assert instance.review_start == tomorrow


def test_summary_markdown_conversion():
    """
    Test the markdown in the summary attribute is converted to HTML when the model is saved.
    """
    instance = baker.make(Review, summary="# Heading", summary_html="")
    assert instance.summary_html == '<h1 class="govuk-heading-xl">Heading</h1>'


def test_get_absolute_url():
    """
    Test getting the canonical URL for a review
    """
    instance = baker.make(Review)
    expected = reverse("review:detail", kwargs={"slug": instance.slug})
    assert instance.get_absolute_url() == expected


def test_external_review_document(review_published):
    """
    Test that the external review document can be obtained from a review.
    """
    expected = Document.objects.get(document_type=Document.TYPE.external_review)
    assert review_published.get_external_reviews().first().pk == expected.pk


def test_submission_form(review_published):
    """
    Test that the submission form can be obtained from a review.
    """
    expected = Document.objects.get(document_type=Document.TYPE.submission_form)
    assert review_published.submission_form.pk == expected.pk


def test_evidence_review_document(review_published):
    """
    Test that the evidence review can be obtained from a review.
    """
    expected = Document.objects.get(document_type=Document.TYPE.evidence_review)
    assert review_published.evidence_review.pk == expected.pk


def test_cover_sheet_document(review_published):
    """
    Test that the final coversheet document (submitted comments) can be obtained from a review.
    """
    expected = Document.objects.get(document_type=Document.TYPE.cover_sheet)
    assert review_published.cover_sheet.pk == expected.pk


@pytest.mark.parametrize(
    "published,count",
    [(False, 1), (True, 0)],  # valid: review started  # valid: review completed
)
def test_in_progress(published, count):
    """
    Test the queryset method in_progress only returns Review objects which are
    currently in review.
    """
    baker.make(Review, published=published)
    actual = Review.objects.in_progress().count()
    assert count == actual


@pytest.mark.parametrize(
    "start,end,published,count",
    [
        (None, None, False, 0),  # valid: review in pre-consultation
        (from_today(+1), from_today(+30), False, 0),  # valid: consultation dates set
        (
            get_today(),
            from_today(+7),
            False,
            1,
        ),  # valid: consultation period opens today
        (
            from_today(-30),
            get_today(),
            False,
            1,
        ),  # valid: consultation period closes today
        (
            from_today(-30),
            from_today(-1),
            False,
            0,
        ),  # valid: review in post-consultation
        (
            from_today(+1),
            None,
            False,
            0,
        ),  # error: pre-consultation but only start date set
        (
            get_today(),
            None,
            False,
            0,
        ),  # error: consultation opens but only start date set
        (
            None,
            from_today(-1),
            False,
            0,
        ),  # error: post-consultation but only end date set
        (None, None, True, 0),  # error: already published
        (from_today(+1), from_today(+30), True, 0),  # error: already published
        (get_today(), from_today(+7), True, 0),  # error: already published
        (from_today(-30), get_today(), True, 0),  # error: already published
        (from_today(-30), from_today(-1), True, 0),  # error: already published
    ],
)
def test_open_for_comments(start, end, published, count):
    """
    Test the queryset method open_for_comments only returns Review objects which are
    currently accepting comments from the public.

    Must also not yet be published.
    """
    baker.make(
        Review, consultation_start=start, consultation_end=end, published=published
    )
    actual = Review.objects.open_for_comments().count()
    assert count == actual


@pytest.mark.parametrize(
    "start,end,count",
    [
        (None, None, 1),  # valid: review in pre-consultation
        (from_today(+1), from_today(+30), 1),  # valid: consultation dates set
        (get_today(), from_today(+7), 0),  # valid: consultation period opens today
        (from_today(-30), get_today(), 0),  # valid: consultation period closes today
        (from_today(-30), from_today(-1), 1),  # valid: review in post-consultation
        (from_today(+1), None, 1),  # error: pre-consultation but only start date set
        (get_today(), None, 1),  # error: consultation opens but only start date set
        (None, from_today(-1), 1),  # error: post-consultation but only end date set
    ],
)
def test_closed_for_comments(start, end, count):
    """
    Test the queryset method closed_for_comments only returns Review objects which are
    not accepting comments from the public.
    """
    baker.make(Review, consultation_start=start, consultation_end=end, published=False)
    actual = Review.objects.closed_for_comments().count()
    assert count == actual


@pytest.mark.skip(reason="needs reworking re DocumentPolicy")
def test_deleting_review_deletes_folder(review_document):
    """
    TODO - given model changes re Review or DocumentPolicy this will need to change, will pick up in next PR. JO.

    Test that deleting a Review cascades and associated documents are deleted too.
    This includes the parent folder if it exists.
    """
    review = review_document.review
    review.delete()
    assert not review_document.exists()
    assert not review_document.file_exists()
    folder = document_path(review)
    assert not review_document.upload.storage.exists(folder)


def test_review_is_saved___cache_is_cleared(make_review):
    cache.set("foo", "bar")

    make_review()

    assert cache.get("foo") is None


def test_review_is_deleted___cache_is_cleared(make_review):
    review = make_review()

    cache.set("foo", "bar")

    review.delete()

    assert cache.get("foo") is None


def test_review_recommendation_is_saved___cache_is_cleared(make_review_recommendation):
    cache.set("foo", "bar")

    make_review_recommendation()

    assert cache.get("foo") is None


def test_review_recommendation_is_deleted___cache_is_cleared(
    make_review_recommendation,
):
    review_recommendation = make_review_recommendation()

    cache.set("foo", "bar")

    review_recommendation.delete()

    assert cache.get("foo") is None
