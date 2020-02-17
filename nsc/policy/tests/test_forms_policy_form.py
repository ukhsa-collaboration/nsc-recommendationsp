from datetime import date

import pytest

from ..forms import PolicyForm


@pytest.mark.parametrize(
    "condition,expected",
    [
        (None, False),  # The condition cannot be None
        ("", False),  # The condition cannot be blank
        (" ", False),  # The condition cannot be empty
        ("# Heading", True),  # The condition can be markdown
        ("<h1>Heading</h1>", True),  # The condition can be HTML
    ],
)
def test_condition_validation(condition, expected):
    data = {"condition": condition, "next_review": ""}
    assert PolicyForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "next_review,expected",
    [
        (None, True),  # The next review can be None
        ("", True),  # The next review can be blank
        (" ", True),  # The next review can be empty
        ("20", False),  # The next review must be 4 digits
        ("2O2O", False),  # The next review must only contain digits
        (date.today().year - 1, False),  # The next review cannot be in the past
        (date.today().year, True),  # The next review can be this year
        (date.today().year + 1, True),  # The next review can be in the future
    ],
)
def test_next_review_validation(next_review, expected):
    data = {"condition": "# Heading", "next_review": next_review}
    assert PolicyForm(data=data).is_valid() == expected


@pytest.mark.parametrize("next_review", ["", " "])
def test_next_review_is_cleaned(next_review):
    """
    Test empty strings and only spaces for the next_review field need
    to be cleaned to None.
    """
    data = {"condition": "# Heading", "next_review": next_review}
    form = PolicyForm(data=data)
    assert form.is_valid() is True
    assert form.cleaned_data["next_review"] is None
