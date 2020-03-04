import pytest
from model_bakery import baker

from ..models import Document


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def all_document_types():
    return [baker.make(Document, document_type=item[0]) for item in Document.TYPE]


@pytest.fixture
def test_factory_create_document():
    """
    Test that we can create an instance via our object factory.
    """
    instance = baker.make(Document)
    assert isinstance(instance, Document)


def test_coversheets_query(all_document_types):
    """
    Test the queryset coversheets() method only returns the coversheet
    documents which contain all the comments made by stakeholders and members
    of the public during the consultation stage of a review.
    """
    expected = [
        obj.pk
        for obj in Document.objects.filter(document_type=Document.TYPE.coversheet)
    ]
    actual = [obj.pk for obj in Document.objects.coversheets()]
    assert expected == actual


def test_evidence_review_query(all_document_types):
    """
    Test the queryset comments() method only returns documents which contain
    the evidence reviews made by an external reviewer.
    """
    expected = [
        obj.pk
        for obj in Document.objects.filter(document_type=Document.TYPE.evidence_review)
    ]
    actual = [obj.pk for obj in Document.objects.evidence_reviews()]
    assert expected == actual


def test_submission_form_query(all_document_types):
    """
    Test the queryset submission_forms() method only returns the documents that
    contain the forms that are used by the stakeholders to submit their comments.
    """
    expected = [
        obj.pk
        for obj in Document.objects.filter(document_type=Document.TYPE.submission_form)
    ]
    actual = [obj.pk for obj in Document.objects.submission_forms()]
    assert expected == actual


def test_recommendations(all_document_types):
    """
    Test the queryset recommendation() method only returns the documents that
    contain the final recommendation by the National Screening Committee on
    whether a condition should be screened for or not.
    """
    expected = [
        obj.pk
        for obj in Document.objects.filter(document_type=Document.TYPE.recommendation)
    ]
    actual = [obj.pk for obj in Document.objects.recommendations()]
    assert expected == actual
