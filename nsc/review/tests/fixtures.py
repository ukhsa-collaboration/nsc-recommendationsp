import pytest
from dateutil.relativedelta import relativedelta
from model_bakery import baker

from nsc.document.models import Document
from nsc.policy.models import Policy
from nsc.utils.datetime import get_today

from ..models import Review, ReviewRecommendation, SummaryDraft


@pytest.fixture
def make_review(make_stakeholder, erm_user):
    def _make_review(add_stakeholders=False, policies=None, user=erm_user, **kwargs):
        policies = policies or [baker.make(Policy, name="condition", ages="{child}")]
        review = baker.make(Review, user=user, **kwargs)
        review.policies.add(*policies)

        if add_stakeholders:
            review.stakeholders.add(make_stakeholder(_make_contact=True))

        return review

    return _make_review


@pytest.fixture
def review_in_pre_consultation(make_review):
    review_start = get_today() - relativedelta(months=2)
    review = make_review(name="Evidence Review", review_start=review_start)
    baker.make(
        Document, name="document", document_type="evidence_review", review=review
    )
    return review


@pytest.fixture
def review_in_consultation(make_review):
    review_start = get_today() - relativedelta(months=2)
    consultation_start = review_start + relativedelta(months=2)
    consultation_end = consultation_start + relativedelta(months=3)
    review = make_review(
        name="review",
        review_start=review_start,
        consultation_start=consultation_start,
        consultation_end=consultation_end,
        dates_confirmed=True,
    )
    baker.make(
        Document,
        name="External Review",
        document_type=Document.TYPE.external_review,
        review=review,
    )
    baker.make(
        Document,
        name="Submission Form",
        document_type=Document.TYPE.submission_form,
        review=review,
    )
    return review


@pytest.fixture
def review_in_post_consultation(make_review):
    review_start = get_today() - relativedelta(months=6)
    consultation_start = review_start + relativedelta(months=2)
    consultation_end = consultation_start + relativedelta(months=3)
    review = make_review(
        name="review",
        review_start=review_start,
        consultation_start=consultation_start,
        consultation_end=consultation_end,
        dates_confirmed=True,
    )
    baker.make(
        Document,
        name="External review",
        document_type=Document.TYPE.external_review,
        review=review,
    )
    baker.make(
        Document,
        name="Submission Form",
        document_type=Document.TYPE.submission_form,
        review=review,
    )
    return review


@pytest.fixture
def review_completed(make_review):
    review_start = get_today() - relativedelta(months=6)
    consultation_start = review_start + relativedelta(months=2)
    consultation_end = consultation_start + relativedelta(months=3)
    review = make_review(
        name="review",
        review_start=review_start,
        consultation_start=consultation_start,
        consultation_end=consultation_end,
        published=True,
    )
    baker.make(
        Document,
        name="External review",
        document_type=Document.TYPE.external_review,
        review=review,
    )
    baker.make(
        Document,
        name="Submission Form",
        document_type=Document.TYPE.submission_form,
        review=review,
    )
    return review


@pytest.fixture
def review_published(make_review, form_pdf):
    review_start = get_today() - relativedelta(months=8)
    consultation_start = review_start + relativedelta(months=2)
    consultation_end = consultation_start + relativedelta(months=3)
    review_end = consultation_start + relativedelta(months=1)
    review = make_review(
        name="review",
        review_start=review_start,
        review_end=review_end,
        consultation_start=consultation_start,
        consultation_end=consultation_end,
        published=True,
    )
    baker.make(
        Document,
        name="External Review",
        document_type=Document.TYPE.external_review,
        review=review,
        upload=form_pdf,
    )
    baker.make(
        Document,
        name="Submission Form",
        document_type=Document.TYPE.submission_form,
        review=review,
        upload=form_pdf,
    )
    baker.make(
        Document,
        name="Cover sheet",
        document_type=Document.TYPE.cover_sheet,
        review=review,
        upload=form_pdf,
    )
    baker.make(
        Document,
        name="Evidence review",
        document_type=Document.TYPE.evidence_review,
        review=review,
        upload=form_pdf,
    )
    return review


@pytest.fixture
def make_review_recommendation():
    def _make(**kwargs):
        return baker.make(ReviewRecommendation, **kwargs)

    return _make


@pytest.fixture
def make_summary_draft():
    def _make(**kwargs):
        return baker.make(SummaryDraft, **kwargs)

    return _make
