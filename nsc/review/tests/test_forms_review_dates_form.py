import random

import pytest
from dateutil.relativedelta import relativedelta
from model_bakery import baker

from nsc.utils.datetime import get_today

from ..forms import ReviewDatesForm
from ..models import Review


# All tests require the database
pytestmark = pytest.mark.django_db


def form_for_review(review):
    data = {
        "consultation_open": None,
        "consultation_start": review.consultation_start,
        "consultation_end": review.consultation_end,
        "nsc_meeting_date": review.nsc_meeting_date,
    }

    date = review.consultation_start
    data.update(
        {
            "consultation_start_day": date.day if date else "",
            "consultation_start_month": date.month if date else "",
            "consultation_start_year": date.year if date else "",
        }
    )

    date = review.consultation_end
    data.update(
        {
            "consultation_end_day": date.day if date else "",
            "consultation_end_month": date.month if date else "",
            "consultation_end_year": date.year if date else "",
        }
    )

    date = review.nsc_meeting_date
    data.update(
        {
            "nsc_meeting_date_day": date.day if date else "",
            "nsc_meeting_date_month": date.month if date else "",
            "nsc_meeting_date_year": date.year if date else "",
        }
    )

    return data


def test_form_configuration():
    assert Review == ReviewDatesForm.Meta.model
    assert "consultation_start" in ReviewDatesForm.Meta.fields
    assert "consultation_end" in ReviewDatesForm.Meta.fields
    assert "nsc_meeting_date" in ReviewDatesForm.Meta.fields


def test_consultation_start_can_be_blank():
    review = baker.make(Review, consultation_start=None, consultation_end=None)
    data = form_for_review(review)
    assert ReviewDatesForm(data=data).is_valid()


def test_consultation_end_can_be_blank():
    review = baker.make(Review, consultation_start=None, consultation_end=None)
    data = form_for_review(review)
    assert ReviewDatesForm(data=data).is_valid()


def test_both_start_and_end_dates_must_be_blank_together():
    review = baker.make(Review, consultation_start=None, consultation_end=get_today())
    data = form_for_review(review)
    assert not ReviewDatesForm(data=data).is_valid()


def test_nsc_meeting_date_can_be_blank():
    review = baker.make(Review, nsc_meeting_date=None)
    data = form_for_review(review)
    assert ReviewDatesForm(data=data).is_valid()


def test_consultation_start_set_from_fields():
    start = get_today()
    tomorrow = get_today() + relativedelta(days=+1)

    data = form_for_review(
        baker.make(Review, consultation_start=start, consultation_end=tomorrow)
    )

    data["consultation_start_day"] = tomorrow.day

    form = ReviewDatesForm(data=data)

    assert form.is_valid()
    assert form.cleaned_data["consultation_start"] == tomorrow


def test_consultation_start_must_be_valid():
    today = get_today()
    soon = get_today() + relativedelta(months=+3)
    data = form_for_review(
        baker.make(Review, consultation_start=today, consultation_end=soon)
    )
    key = random.choice(
        [
            "consultation_start_day",
            "consultation_start_month",
            "consultation_start_year",
        ]
    )
    data[key] = "0"
    assert not ReviewDatesForm(data=data).is_valid()


def test_consultation_end_set_from_fields():
    yesterday = get_today() + relativedelta(days=-1)
    tomorrow = get_today() + relativedelta(days=+1)

    data = form_for_review(
        baker.make(Review, consultation_start=yesterday, consultation_end=tomorrow)
    )

    today = get_today()

    data["consultation_end_day"] = today.day
    data["consultation_end_month"] = today.month
    data["consultation_end_year"] = today.year

    form = ReviewDatesForm(data=data)

    assert form.is_valid()
    assert form.cleaned_data["consultation_end"] == today


def test_consultation_end_date_must_be_valid():
    today = get_today()
    soon = get_today() + relativedelta(months=+3)
    data = form_for_review(
        baker.make(Review, consultation_start=today, consultation_end=soon)
    )
    key = random.choice(
        ["consultation_end_day", "consultation_end_month", "consultation_end_year"]
    )
    data[key] = "0"
    assert not ReviewDatesForm(data=data).is_valid()


def test_nsc_meeting_date_set_from_fields():
    today = get_today()
    tomorrow = get_today() + relativedelta(days=+1)

    data = form_for_review(baker.make(Review, nsc_meeting_date=today))

    data["nsc_meeting_date_day"] = tomorrow.day

    form = ReviewDatesForm(data=data)

    assert form.is_valid()
    assert form.cleaned_data["nsc_meeting_date"] == tomorrow


def test_nsc_meeting_date_must_be_valid():
    today = get_today()
    soon = get_today() + relativedelta(months=+3)
    data = form_for_review(
        baker.make(Review, consultation_start=today, consultation_end=soon)
    )
    key = random.choice(
        ["nsc_meeting_date_day", "nsc_meeting_date_month", "nsc_meeting_date_year"]
    )
    data[key] = "0"
    assert not ReviewDatesForm(data=data).is_valid()


def test_opening_consultation_initializes_dates_starting_today():
    data = form_for_review(
        baker.make(Review, consultation_start=None, consultation_end=None)
    )
    data["consultation_open"] = "True"

    start = get_today()
    end = get_today() + relativedelta(months=+3)
    form = ReviewDatesForm(data=data)

    assert form.is_valid()
    assert form.cleaned_data["consultation_start"] == start
    assert form.cleaned_data["consultation_end"] == end


def test_consultation_end_must_come_after_consultation_start():
    today = get_today()
    tomorrow = get_today() + relativedelta(days=+1)

    data = form_for_review(
        baker.make(Review, consultation_start=tomorrow, consultation_end=today)
    )
    assert not ReviewDatesForm(data=data).is_valid()


def test_nsc_meeting_must_come_after_consultation_end():
    today = get_today()
    tomorrow = get_today() + relativedelta(days=+1)

    data = form_for_review(
        baker.make(
            Review,
            consultation_start=today,
            consultation_end=tomorrow,
            nsc_meeting_date=today,
        )
    )
    assert not ReviewDatesForm(data=data).is_valid()
