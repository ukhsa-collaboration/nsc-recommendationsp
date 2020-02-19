import pytest

from ..forms import OrganisationForm


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, False),  # The name cannot be None
        ("", False),  # The name cannot be blank
        (" ", False),  # The name cannot be empty
        ("Name", True),  # The name is a string
    ],
)
def test_name_validation(value, expected):
    data = {"name": value, "is_public": True}
    assert OrganisationForm(data=data).is_valid() == expected


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
def test_url_validation(value, expected):
    data = {"name": "Name", "url": value, "is_public": True}
    assert OrganisationForm(data=data).is_valid() == expected


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
def test_is_public_validation(value, expected):
    data = {"name": "Name", "url": "www.phe.gov.uk", "is_public": value}
    assert OrganisationForm(data=data).is_valid() == expected
