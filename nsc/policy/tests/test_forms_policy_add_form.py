import pytest
from model_bakery import baker

from nsc.utils.datetime import get_today

from ..forms import PolicyAddForm, PolicyAddRecommendationForm, PolicyAddSummaryForm
from ..models import Policy


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "name, expected",
    [
        (None, False),  # The name cannot be None
        ("", False),  # The name cannot be blank
        (" ", False),  # The name cannot be empty
        ("Heading", True),
    ],
)
def test_add_name_validation(name, expected):
    data = {
        "name": name,
        "condition_type": Policy.CONDITION_TYPES.general,
        "condition": "condition",
        "ages": [Policy.AGE_GROUPS.antenatal],
        "keywords": "keywords",
    }
    assert PolicyAddForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "condition_type, expected",
    [
        (None, False),  # The name cannot be None
        ("", False),  # The name cannot be blank
        (" ", False),  # The name cannot be empty
        (Policy.CONDITION_TYPES.general, True),
        (Policy.CONDITION_TYPES.targeted, True),
    ],
)
def test_add_type_validation(condition_type, expected):
    data = {
        "name": "name",
        "condition_type": condition_type,
        "condition": "condition",
        "ages": [Policy.AGE_GROUPS.antenatal],
        "keywords": "keywords",
    }
    assert PolicyAddForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "condition, expected",
    [
        (None, False),  # The condition cannot be None
        ("", False),  # The condition cannot be blank
        (" ", False),  # The condition cannot be empty
        ("# Heading", True),  # The condition can be markdown
        ("<h1>Heading</h1>", True),  # The condition can be HTML
    ],
)
def test_add_condition_validation(condition, expected):
    data = {
        "name": "name",
        "condition_type": Policy.CONDITION_TYPES.general,
        "condition": condition,
        "ages": [Policy.AGE_GROUPS.antenatal],
        "keywords": "keywords",
    }
    assert PolicyAddForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "ages, expected",
    [
        (None, False),  # The name cannot be None
        ("", False),  # The name cannot be blank
        (" ", False),  # The name cannot be empty
        ([Policy.AGE_GROUPS.antenatal], True),
        ([Policy.AGE_GROUPS.antenatal, Policy.AGE_GROUPS.newborn], True),
    ],
)
def test_add_ages_validation(ages, expected):
    data = {
        "name": "name",
        "condition_type": Policy.CONDITION_TYPES.general,
        "condition": "condition",
        "ages": ages,
        "keywords": "keywords",
    }
    assert PolicyAddForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "keywords, expected",
    [
        (None, True),  # The keywords can be None
        ("", True),  # The keywords can be blank
        (" ", True),  # The keywords can be empty
        ("keywords", True),
    ],
)
def test_add_keywords_validation(keywords, expected):
    data = {
        "name": "name",
        "condition_type": Policy.CONDITION_TYPES.general,
        "condition": "condition",
        "ages": [Policy.AGE_GROUPS.antenatal],
        "keywords": keywords,
    }
    assert PolicyAddForm(data=data).is_valid() == expected


def test_add_name_already_used():
    baker.make(Policy, name="Test")
    form_data = {
        "name": "Test",
        "condition_type": Policy.CONDITION_TYPES.general,
        "condition": "condition",
        "ages": [Policy.AGE_GROUPS.antenatal],
        "keywords": "keywords",
    }
    form = PolicyAddForm(data=form_data)
    assert not form.is_valid()
    assert "name" in form.errors


@pytest.mark.parametrize(
    "summary, expected",
    [
        (None, False),  # The summary cannot be None
        ("", False),  # The summary cannot be blank
        (" ", False),  # The summary cannot be empty
        ("# Heading", True),  # The summary can be markdown
        ("<h1>Heading</h1>", True),  # The summarycosummaryndition can be HTML
    ],
)
def test_add_summary_summary_validation(summary, expected):
    data = {
        "summary": summary,
        "background": "background",
    }
    assert PolicyAddSummaryForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "background, expected",
    [
        (None, True),  # The background can be None
        ("", True),  # The background can be blank
        (" ", True),  # The background can be empty
        ("# Heading", True),  # The background can be markdown
        ("<h1>Heading</h1>", True),  # The background can be HTML
    ],
)
def test_add_summary_background_validation(background, expected):
    data = {
        "summary": "summary",
        "background": background,
    }
    assert PolicyAddSummaryForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "recommendation,expected",
    [
        (None, True),  # The recommendation can be None
        ("", True),  # The recommendation can be blank
        (" ", False),  # The recommendation cannot be empty
        (True, True),  # The recommendation can be True
        (False, True),  # The recommendation can be False
    ],
)
def test_add_recommendation_recommendation_validation(recommendation, expected):
    data = {
        "recommendation": recommendation,
        "next_review": get_today().year,
    }
    assert PolicyAddRecommendationForm(data=data).is_valid() == expected


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
def test_add_recommendation_next_review_validation(next_review, expected):
    data = {
        "recommendation": True,
        "next_review": next_review,
    }
    assert PolicyAddRecommendationForm(data=data).is_valid() == expected
