import pytest

from ..forms import ContactForm


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, False),  # None (null) is not allowed
        ("", False),  # An empty string is not allowed
        (" ", False),  # Only spaces is not allowed
        ("Name", True),  # A string is allowed
    ],
)
def test_name_validation(value, expected, organisation):
    data = {
        "name": value,
        "email": "name@example.com",
        "phone": "01 234 456789",
        "organisation": organisation.pk,
    }
    assert ContactForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, False),  # None (null) is not allowed
        ("", False),  # An empty string is not allowed
        (" ", False),  # Only spaces is not allowed
        ("example.com", False),  # An invalid email address is not allowed
        ("user@example.com", True),  # A valid email address is allowed
    ],
)
def test_email_validation(value, expected, organisation):
    data = {
        "name": "Name",
        "email": value,
        "phone": "01 234 456789",
        "organisation": organisation.pk,
    }
    assert ContactForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, True),  # None is allowed (will be saved as an empty string)
        ("", True),  # An empty string is allowed
        (" ", True),  # Only spaces is allowed (will be saved as an empty string)
        ("01234456789", True),  # A simple string is allowed
        ("01 234 456789", True),  # A formatted string is allowed
        ("(01) 234 567890", True),  # Numbers with optional area code is allowed
        ("+44 1 234 567890", True),  # International format numbers are allowed
        ("01 234 456789 x1234", True),  # Numbers with an extension are allowed
    ],
)
def test_phone_validation(value, expected, organisation):
    data = {
        "name": "Name",
        "email": "name@example.com",
        "phone": value,
        "organisation": organisation.pk,
    }
    assert ContactForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, False),  # Organisation cannot be None (null)
        (-1, False),  # Organisation must exist
    ],
)
def test_organisation_validation(value, expected):
    data = {
        "name": "Name",
        "email": "name@example.com",
        "phone": "01234567890",
        "organisation": value,
    }
    assert ContactForm(data=data).is_valid() == expected


def test_object_created(organisation):
    data = {
        "name": "Name",
        "email": "name@example.com",
        "phone": "01234567890",
        "organisation": organisation.pk,
    }
    form = ContactForm(data=data)
    assert form.is_valid()
    assert organisation.contacts.count() == 0
    form.save()
    assert organisation.contacts.count() == 1
