from datetime import date

import pytest

from nsc.utils.datetime import get_date_display, get_day_display


@pytest.mark.parametrize(
    "day,expected",
    [
        (1, "1st"),
        (2, "2nd"),
        (3, "3rd"),
        (4, "4th"),
        (5, "5th"),
        (6, "6th"),
        (7, "7th"),
        (8, "8th"),
        (9, "9th"),
        (10, "10th"),
        (11, "11th"),
        (12, "12th"),
        (13, "13th"),
        (14, "14th"),
        (15, "15th"),
        (16, "16th"),
        (17, "17th"),
        (18, "18th"),
        (19, "19th"),
        (20, "20th"),
        (21, "21st"),
        (22, "22nd"),
        (23, "23rd"),
        (24, "24th"),
        (25, "25th"),
        (26, "26th"),
        (27, "27th"),
        (28, "28th"),
        (29, "29th"),
        (30, "30th"),
        (31, "31st"),
    ],
)
def test_get_day_display__suffix_added(day, expected):
    """
    Test the correct suffix is displayed for each day in a month.
    """
    assert expected == get_day_display(day)


def test_get_day_display__value_cannot_be_none():
    """
    Test a ValueError is raise if the day is None.
    """
    pytest.raises(ValueError, get_day_display, None)


def test_get_day_display__value_cannot_be_outside_range():
    """
    Test a ValueError is raise if the day is not in the range 1..31.
    """
    pytest.raises(ValueError, get_day_display, 0)
    pytest.raises(ValueError, get_day_display, 32)


def test_get_date_display__date_is_formatted():
    """
    Test a suffix is added to the day in a month.
    """
    assert "2nd January 2020" == get_date_display(date(2020, 1, 2))
    pytest.raises(ValueError, get_date_display, None)


def test_get_date_display__date_cannot_be_none():
    """
    Test a ValueError is raised if the date is None.
    """
    assert "2nd January 2020" == get_date_display(date(2020, 1, 2))
    pytest.raises(ValueError, get_date_display, None)
