from os import path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from django.urls import reverse

import pytest

# All tests require the database
from nsc.document.models import Document


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("requested_type", Document.TYPE._db_values)
def test_no_files_for_type___response_is_not_found(
    requested_type, make_document, make_review, client
):
    review = make_review()

    for doc_type in Document.TYPE._db_values:
        if doc_type == requested_type:
            continue

        make_document(review=review, document_type=doc_type)

    response = client.get(
        reverse(
            "review:review-document-download",
            kwargs={
                "slug": review.slug,
                "doc_type": requested_type,
            },
        ),
        expect_errors=True,
    )

    assert response.status_code == 404


@pytest.mark.parametrize("requested_type", Document.TYPE._db_values)
def test_single_files_for_type___response_is_single_file(
    requested_type, make_document, make_review, client
):
    review = make_review()

    doc = make_document(review=review, document_type=requested_type)

    response = client.get(
        reverse(
            "review:review-document-download",
            kwargs={
                "slug": review.slug,
                "doc_type": requested_type,
            },
        ),
    )

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert (
        response.headers["Content-Disposition"] == 'attachment; filename="document.pdf"'
    )
    assert response.body == doc.upload.read()


@pytest.mark.parametrize("requested_type", Document.TYPE._db_values)
def test_multiple_files_for_type___response_is_zip_file(
    requested_type, make_document, make_review, client
):
    review = make_review()

    doc1 = make_document(review=review, document_type=requested_type)
    doc2 = make_document(review=review, document_type=requested_type)

    response = client.get(
        reverse(
            "review:review-document-download",
            kwargs={
                "slug": review.slug,
                "doc_type": requested_type,
            },
        ),
    )

    assert response.status_code == 200

    with TemporaryDirectory() as d:
        zip_path = path.join(d, "arch.zip")
        with open(zip_path, "wb") as f:
            f.write(response.body)

        with ZipFile(zip_path) as z:
            with z.open(doc1.name) as first:
                assert first.read() == doc1.upload.read()

            with z.open(doc2.name) as second:
                assert second.read() == doc2.upload.read()
