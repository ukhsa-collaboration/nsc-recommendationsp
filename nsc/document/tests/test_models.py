from django.urls import reverse

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


@pytest.fixture
def test_get_download_url():
    """
    Test getting the URL for downloading a document
    """
    instance = baker.make(Document)
    expected = reverse("document:download", kwargs={"pk": instance.pk})
    assert instance.get_download_url() == expected


def test_all_document_types(all_document_types):
    """
    Test that the fixture does actually contains all document types.
    """
    expected = [item[0] for item in Document.TYPE]
    actual = [obj.document_type for obj in all_document_types]
    assert sorted(expected) == sorted(actual)


def test_cover_sheets_query(all_document_types):
    """
    Test the queryset cover_sheets() method only returns the cover_sheet
    documents which contain all the comments made by stakeholders and members
    of the public during the consultation stage of a review.
    """
    expected = [
        obj.pk
        for obj in Document.objects.filter(document_type=Document.TYPE.cover_sheet)
    ]
    actual = [obj.pk for obj in Document.objects.cover_sheets()]
    assert expected == actual


def test_external_review_query(all_document_types):
    """
    Test the queryset comments() method only returns documents which contain
    the reviews made by an external reviewer.
    """
    expected = [
        obj.pk
        for obj in Document.objects.filter(document_type=Document.TYPE.external_review)
    ]
    actual = [obj.pk for obj in Document.objects.external_reviews()]
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


def test_evidence_reviews(all_document_types):
    """
    Test the queryset evidence_reviews() method only returns the documents that
    contain the final recommendation by the National Screening Committee on
    whether a condition should be screened for or not.
    """
    expected = [
        obj.pk
        for obj in Document.objects.filter(document_type=Document.TYPE.evidence_review)
    ]
    actual = [obj.pk for obj in Document.objects.evidence_reviews()]
    assert expected == actual


def test_deleting_document_deletes_file(review_document):
    """
    Test that deleting a Document deletes the associated file in storage.
    """
    review_document.delete()
    assert not review_document.file_exists()


def test_queryset_delete_deletes_files(review_document):
    """
    Test that calling delete() on the queryset also deletes the files from storage.
    """
    Document.objects.all().delete()
    assert not review_document.exists()
    assert not review_document.file_exists()


@pytest.skip()
def test_deleting_review_deletes_document(review_document):
    """
    TODO - given model changes re Review or DocumentPolicy this will need to change, will pick up in next PR. JO.

    Test that deleting a Review cascades and associated documents are deleted too.
    This includes the parent folder if it exists.
    """
    review_document.review.delete()
    assert not review_document.exists()
    assert not review_document.file_exists()
