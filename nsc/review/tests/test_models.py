from django.urls import reverse

import pytest
from dateutil.relativedelta import relativedelta
from model_bakery import baker

from nsc.document.models import Document, review_document_path
from nsc.utils.datetime import get_today

from ..models import Review


# All tests require the database
pytestmark = pytest.mark.django_db
pytest_plugins = ["nsc.review.tests.fixtures", "nsc.document.tests.fixtures"]


def test_factory_create_policy():
    """
    Test that we can create an instance via our object factory.
    """
    instance = baker.make(Review)
    assert isinstance(instance, Review)


def test_inside_consultation_period():
    """
    Test the queryset in_consultation() method includes reviews that are
    currently open for public comments.
    """
    date = get_today()
    instance = baker.make(
        Review,
        consultation_start=date,
        consultation_end=date + relativedelta(months=+3),
    )
    assert Review.objects.in_consultation().first().pk == instance.pk

    instance.consultation_start = date - relativedelta(months=+3)
    instance.consultation_end = date
    instance.save()
    assert Review.objects.in_consultation().first().pk == instance.pk


def test_outside_consultation_period():
    """
    Test the queryset in_consultation() method excludes reviews that are not
    currently open for public comments.
    """
    date = get_today() + relativedelta(days=1)
    baker.make(Review, consultation_start=date)
    assert not Review.objects.in_consultation().exists()
    date = get_today() - relativedelta(days=1)
    baker.make(Review, consultation_end=date)
    assert not Review.objects.in_consultation().exists()


def test_slug_is_set():
    """
    Test the slug field, if not set, is generated from the name field.
    """
    instance = baker.make(Review, name="The Review", slug="")
    instance.clean()
    assert instance.slug == "the-review"


def test_slug_is_not_overwritten():
    """
    Test that once the slug is set it is not overwritten if the name of the
    policy changes. This ensures that any bookmarked pages still work if the
    name is changed at a later time.
    """
    instance = baker.make(Review, name="The Review", slug="the-review")
    instance.name = "New name"
    instance.clean()
    assert instance.slug == "the-review"


def test_summary_markdown_conversion():
    """
    Test the markdown in the summary attribute is converted to HTML when the model is cleaned.
    """
    instance = baker.make(Review, summary="# Heading", summary_html="")
    instance.clean()
    assert instance.summary_html == '<h1 class="govuk-heading-xl">Heading</h1>'


def test_get_absolute_url():
    """
    Test getting the canonical URL for a review
    """
    instance = baker.make(Review)
    expected = reverse("review:detail", kwargs={"slug": instance.slug})
    assert instance.get_absolute_url() == expected


def test_evidence_review_document(review_published):
    """
    Test that the evidence review document can be obtained from a review.
    """
    expected = Document.objects.get(document_type=Document.TYPE.evidence_review)
    assert review_published.get_evidence_review_document().pk == expected.pk


def test_submission_form(review_published):
    """
    Test that the submission form can be obtained from a review.
    """
    expected = Document.objects.get(document_type=Document.TYPE.submission_form)
    assert review_published.get_submission_form().pk == expected.pk


def test_recommendation_document(review_published):
    """
    Test that the final recommendation document can be obtained from a review.
    """
    expected = Document.objects.get(document_type=Document.TYPE.recommendation)
    assert review_published.get_recommendation_document().pk == expected.pk


def test_coversheet_document(review_published):
    """
    Test that the final coversheet document (submitted comments) can be obtained from a review.
    """
    expected = Document.objects.get(document_type=Document.TYPE.coversheet)
    assert review_published.get_coversheet_document().pk == expected.pk


@pytest.mark.parametrize(
    "status,phase,count",
    [
        ("draft", "pre_consultation", 0),
        ("draft", "consultation", 1),
        ("draft", "post_consultation", 0),
        ("draft", "completed", 0),
        ("published", "completed", 0),
    ],
)
def test_in_consultation(status, phase, count):
    """
    Test the queryset method in_consultation only returns Review objects which are
    currently in review and are in the consultation phase.
    """
    baker.make(Review, status=status, phase=phase)
    actual = Review.objects.in_consultation().count()
    assert count == actual


@pytest.mark.parametrize(
    "status,phase,count",
    [
        ("draft", "pre_consultation", 1),
        ("draft", "consultation", 0),
        ("draft", "post_consultation", 1),
        ("draft", "completed", 1),
        ("published", "completed", 1),
    ],
)
def test_not_in_consultation(status, phase, count):
    """
    Test the queryset method not_in_consultation excludes Reviews objects which are
    currently in review and are in the consultation phase.
    """
    baker.make(Review, status=status, phase=phase)
    actual = Review.objects.not_in_consultation().count()
    assert count == actual


def test_deleting_review_deletes_folder(review_document):
    """
    Test that deleting a Review cascades and associated documents are deleted too.
    This includes the parent folder if it exists.
    """
    review = review_document.review
    review.delete()
    assert not review_document.exists()
    assert not review_document.file_exists()
    folder = review_document_path(review)
    assert not review_document.upload.storage.exists(folder)
