import pytest
from freezegun import freeze_time
from model_bakery import baker

from nsc.utils.datetime import get_today

from ..forms import ReviewDateConfirmationForm
from ..models import Review


# All tests require the database
pytestmark = pytest.mark.django_db


def test_consultation_start_is_not_set_error_is_raised():
    with freeze_time():
        today = get_today()
        review = baker.make(
            Review,
            consultation_start=None,
            consultation_end=today,
            nsc_meeting_date=today,
        )
        form = ReviewDateConfirmationForm(
            instance=review, data={"dates_confirmed": True}
        )

        assert not form.is_valid()
        assert [
            "The review consultation start date has not been set."
        ] == form.non_field_errors()


def test_consultation_end_is_not_set_error_is_raised():
    with freeze_time():
        today = get_today()
        review = baker.make(
            Review,
            consultation_start=today,
            consultation_end=None,
            nsc_meeting_date=today,
        )
        form = ReviewDateConfirmationForm(
            instance=review, data={"dates_confirmed": True}
        )

        assert not form.is_valid()
        assert [
            "The review consultation end date has not been set."
        ] == form.non_field_errors()


def test_nsc_meeting_date_is_not_set_error_is_raised():
    with freeze_time():
        today = get_today()
        review = baker.make(
            Review,
            consultation_start=today,
            consultation_end=today,
            nsc_meeting_date=None,
        )
        form = ReviewDateConfirmationForm(
            instance=review, data={"dates_confirmed": True}
        )

        assert not form.is_valid()
        assert (
            "The review UK NSC meeting date has not been set."
            in form.non_field_errors()
        )


def test_dates_are_already_confirmed_error_is_not_raised():
    with freeze_time():
        today = get_today()
        review = baker.make(
            Review,
            consultation_start=today,
            consultation_end=today,
            nsc_meeting_date=today,
            dates_confirmed=True,
        )
        form = ReviewDateConfirmationForm(
            instance=review, data={"dates_confirmed": True}
        )

        assert form.is_valid()


@pytest.mark.parametrize("value", (True, False))
def test_all_fields_are_valid_review_is_updated(value):
    with freeze_time():
        today = get_today()
        review = baker.make(
            Review,
            consultation_start=today,
            consultation_end=today,
            nsc_meeting_date=today,
            dates_confirmed=False,
        )
        form = ReviewDateConfirmationForm(
            instance=review, data={"dates_confirmed": value}
        )

        form.is_valid()

        assert form.is_valid(), form.errors

        form.save()
        review.refresh_from_db()

        assert review.dates_confirmed == value
