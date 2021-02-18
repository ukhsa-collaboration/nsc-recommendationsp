import pytest

from nsc.utils.datetime import get_today

from ..forms import PolicyEditForm
from ..models import Policy


def test_form_configuration():
    assert Policy == PolicyEditForm.Meta.model
    assert "next_review" in PolicyEditForm.Meta.fields
    assert "condition_type" in PolicyEditForm.Meta.fields
    assert "ages" in PolicyEditForm.Meta.fields
    assert "condition" in PolicyEditForm.Meta.fields
    assert "keywords" in PolicyEditForm.Meta.fields
    assert "summary" in PolicyEditForm.Meta.fields
    assert "background" in PolicyEditForm.Meta.fields


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
    data = {
        "condition": condition,
        "next_review": "",
        "condition_type": Policy.CONDITION_TYPES.general,
        "ages": [Policy.AGE_GROUPS.antenatal],
        "summary": "A summary",
        "background": "Some background",
    }
    assert PolicyEditForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "condition_type,expected",
    [
        (None, False),  # The condition_type cannot be None
        ("", False),  # The condition_type cannot be blank
        (" ", False),  # The condition_type cannot be empty
        (Policy.CONDITION_TYPES.general, True),
        (Policy.CONDITION_TYPES.targeted, True),
    ],
)
def test_condition_type_validation(condition_type, expected):
    data = {
        "condition": "condition",
        "next_review": "",
        "condition_type": condition_type,
        "ages": [Policy.AGE_GROUPS.antenatal],
        "summary": "A summary",
        "background": "Some background",
    }
    assert PolicyEditForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "ages,expected",
    [
        (None, False),  # The ages cannot be None
        ("", False),  # The ages cannot be blank
        (" ", False),  # The ages cannot be empty
        ([Policy.AGE_GROUPS.antenatal], True),
        ([Policy.AGE_GROUPS.antenatal, Policy.AGE_GROUPS.newborn], True),
    ],
)
def test_ages_validation(ages, expected):
    data = {
        "condition": "condition",
        "next_review": "",
        "condition_type": Policy.CONDITION_TYPES.general,
        "ages": ages,
        "summary": "A summary",
        "background": "Some background",
    }
    assert PolicyEditForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "next_review,expected",
    [
        (None, True),  # The next review can be None
        ("", True),  # The next review can be blank
        (" ", True),  # The next review can be empty
        ("20", False),  # The next review must be 4 digits
        ("2O2O", False),  # The next review must only contain digits
        (get_today().year - 1, False),  # The next review cannot be in the past
        (get_today().year, True),  # The next review can be this year
        (get_today().year + 1, True),  # The next review can be in the future
    ],
)
def test_next_review_validation(next_review, expected):
    data = {
        "condition": "# Heading",
        "next_review": next_review,
        "condition_type": Policy.CONDITION_TYPES.general,
        "ages": [Policy.AGE_GROUPS.antenatal],
        "summary": "A summary",
        "background": "Some background",
    }
    assert PolicyEditForm(data=data).is_valid() == expected


@pytest.mark.parametrize("next_review", ["", " "])
def test_next_review_is_cleaned(next_review):
    """
    Test empty strings and only spaces for the next_review field need
    to be cleaned to None.
    """
    data = {
        "condition": "# Heading",
        "next_review": next_review,
        "condition_type": Policy.CONDITION_TYPES.general,
        "ages": [Policy.AGE_GROUPS.antenatal],
        "summary": "A summary",
        "background": "Some background",
    }
    form = PolicyEditForm(data=data)
    assert form.is_valid() is True
    assert form.cleaned_data["next_review"] is None
