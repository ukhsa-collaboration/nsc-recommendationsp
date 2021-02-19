import pytest

from ..forms import StakeholderForm
from ..models import Stakeholder


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, False),  # The name cannot be None
        ("", False),  # The name cannot be blank
        (" ", False),  # The name cannot be empty
        ("Name", True),  # The name is a string
    ],
)
def test_name_validation(value, expected, make_policy):
    data = {
        "name": value,
        "is_public": True,
        "type": Stakeholder.TYPE_INDIVIDUAL,
        "countries": [Stakeholder.COUNTRY_ENGLAND],
        "policies-TOTAL_FORMS": 1,
        "policies-INITIAL_FORMS": 1,
        "policies-MIN_NUM_FORMS": 1,
        "policies-MAX_NUM_FORMS": 1000,
        "policies-0-policy": make_policy().id,
        "contacts-TOTAL_FORMS": 1,
        "contacts-INITIAL_FORMS": 0,
        "contacts-MIN_NUM_FORMS": 1,
        "contacts-MAX_NUM_FORMS": 5,
        "contacts-0-id": "",
        "contacts-0-name": "contact",
    }
    assert StakeholderForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, True),  # None is allowed (will be saved as an empty string)
        ("", True),  # An empty string is allowed
        (" ", True),  # Only spaces is allowed (will be saved as an empty string)
        ("www.phe.gov.uk", True),  # A simple string is allowed
        ("http://www.phe.gov.uk", True),  # A full URL is allowed
    ],
)
def test_url_validation(value, expected, make_policy):
    data = {
        "name": "Name",
        "url": value,
        "is_public": True,
        "type": Stakeholder.TYPE_INDIVIDUAL,
        "countries": [Stakeholder.COUNTRY_ENGLAND],
        "policies-TOTAL_FORMS": 1,
        "policies-INITIAL_FORMS": 1,
        "policies-MIN_NUM_FORMS": 1,
        "policies-MAX_NUM_FORMS": 1000,
        "policies-0-policy": make_policy().id,
        "contacts-TOTAL_FORMS": 1,
        "contacts-INITIAL_FORMS": 0,
        "contacts-MIN_NUM_FORMS": 1,
        "contacts-MAX_NUM_FORMS": 5,
        "contacts-0-name": "contact",
    }
    assert StakeholderForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, True),  # None is allowed (will be saved as an empty string)
        ("", True),  # An empty string is allowed
        (" ", False),  # Only spaces is allowed (will be saved as an empty string)
        ([Stakeholder.COUNTRY_ENGLAND], True),  # England
        ([Stakeholder.COUNTRY_SCOTLAND], True),  # Scotland
        ([Stakeholder.COUNTRY_WALES], True),  # Wales
        ([Stakeholder.COUNTRY_NORTHERN_IRELAND], True),  # Northern ireland
        ([Stakeholder.COUNTRY_UK], True),  # UK
        ([Stakeholder.COUNTRY_INTERNATIONAL], True),  # International
        ([Stakeholder.COUNTRY_UK, Stakeholder.COUNTRY_INTERNATIONAL], True),  # Multi
    ],
)
def test_country_validation(value, expected, make_policy):
    data = {
        "name": "Name",
        "url": "",
        "is_public": True,
        "type": Stakeholder.TYPE_INDIVIDUAL,
        "countries": value,
        "policies-TOTAL_FORMS": 1,
        "policies-INITIAL_FORMS": 1,
        "policies-MIN_NUM_FORMS": 1,
        "policies-MAX_NUM_FORMS": 1000,
        "policies-0-policy": make_policy().id,
        "contacts-TOTAL_FORMS": 1,
        "contacts-INITIAL_FORMS": 0,
        "contacts-MIN_NUM_FORMS": 1,
        "contacts-MAX_NUM_FORMS": 5,
        "contacts-0-name": "contact",
    }
    assert StakeholderForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, False),  # None is allowed (will be saved as an empty string)
        ("", False),  # An empty string is allowed
        (" ", False),  # Only spaces is allowed (will be saved as an empty string)
        (Stakeholder.TYPE_INDIVIDUAL, True),  # Individual
        (Stakeholder.TYPE_COMMERCIAL, True),  # Commercial
        (Stakeholder.TYPE_PROFESSIONAL, True),  # Professional
        (Stakeholder.TYPE_PATIENT_GROUP, True),  # Patient group
        (Stakeholder.TYPE_ACADEMIC, True),  # Academic
        (Stakeholder.TYPE_OTHER, True),  # Other
    ],
)
def test_type_validation(value, expected, make_policy):
    data = {
        "name": "Name",
        "url": "",
        "is_public": True,
        "type": value,
        "countries": [Stakeholder.COUNTRY_UK],
        "policies-TOTAL_FORMS": 1,
        "policies-INITIAL_FORMS": 1,
        "policies-MIN_NUM_FORMS": 1,
        "policies-MAX_NUM_FORMS": 1000,
        "policies-0-policy": make_policy().id,
        "contacts-TOTAL_FORMS": 1,
        "contacts-INITIAL_FORMS": 0,
        "contacts-MIN_NUM_FORMS": 1,
        "contacts-MAX_NUM_FORMS": 5,
        "contacts-0-name": "contact",
    }
    assert StakeholderForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, False),  # None is not allowed
        ("", False),  # An empty string is not allowed
        (" ", False),  # Only spaces is not allowed
        ("yes", False),  # 'yes' is not allowed
        ("y", False),  # 'y' is not allowed
        ("t", False),  # 't' is not allowed
        (1, False),  # 1 is not allowed
        (True, True),  # True is allowed
        ("no", False),  # 'no' is not allowed
        ("n", False),  # 'n' is not allowed
        ("f", False),  # 'f' is not allowed
        (0, False),  # 0 is not allowed
        (False, True),  # False is allowed
    ],
)
def test_is_public_validation(value, expected, make_policy):
    data = {
        "name": "Name",
        "url": "www.phe.gov.uk",
        "is_public": value,
        "type": Stakeholder.TYPE_INDIVIDUAL,
        "countries": [Stakeholder.COUNTRY_UK],
        "policies-TOTAL_FORMS": 1,
        "policies-INITIAL_FORMS": 1,
        "policies-MIN_NUM_FORMS": 1,
        "policies-MAX_NUM_FORMS": 1000,
        "policies-0-policy": make_policy().id,
        "contacts-TOTAL_FORMS": 1,
        "contacts-INITIAL_FORMS": 0,
        "contacts-MIN_NUM_FORMS": 1,
        "contacts-MAX_NUM_FORMS": 5,
        "contacts-0-name": "contact",
    }
    assert StakeholderForm(data=data).is_valid() == expected
