import pytest

from ..forms import StakeholderCommentForm


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "name, expected",
    [
        (None, False),  # The name cannot be None
        ("", False),  # The name cannot be blank
        (" ", False),  # The name cannot be empty
        ("name", True),
    ],
)
def test_comment_name_validation(name, expected):
    data = {
        "name": name,
        "email": "email@email.com",
        "organisation": "organisation",
        "role": "role",
        "publish": True,
        "behalf": True,
        "comment": "comment",
    }
    assert StakeholderCommentForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "email, expected",
    [
        (None, False),  # The email cannot be None
        ("", False),  # The email cannot be blank
        (" ", False),  # The email cannot be empty
        ("email", False),
        ("email@email.com", True),
    ],
)
def test_comment_email_validation(email, expected):
    data = {
        "name": "name",
        "email": email,
        "organisation": "organisation",
        "role": "role",
        "publish": True,
        "behalf": True,
        "comment": "comment",
    }
    assert StakeholderCommentForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "publish, expected",
    [
        (None, False),  # The publish cannot be None
        ("", False),  # The publish cannot be blank
        (" ", False),  # The publish cannot be empty
        (True, True),
        (False, True),
    ],
)
def test_comment_publish_validation(publish, expected):
    data = {
        "name": "name",
        "email": "email@email.com",
        "organisation": "organisation",
        "role": "role",
        "publish": publish,
        "behalf": True,
        "comment": "comment",
    }
    assert StakeholderCommentForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "behalf, expected",
    [
        (None, False),  # The publish cannot be None
        ("", False),  # The publish cannot be blank
        (" ", False),  # The publish cannot be empty
        (True, True),
        (False, True),
    ],
)
def test_comment_behalf_validation(behalf, expected):
    data = {
        "name": "name",
        "email": "email@email.com",
        "organisation": "organisation",
        "role": "role",
        "publish": True,
        "behalf": behalf,
        "comment": "comment",
    }
    assert StakeholderCommentForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "comment, expected",
    [
        (None, False),  # The publish cannot be None
        ("", False),  # The publish cannot be blank
        (" ", False),  # The publish cannot be empty
        ("comment", True),
    ],
)
def test_comment_comment_validation(comment, expected):
    data = {
        "name": "name",
        "email": "email@email.com",
        "organisation": "organisation",
        "role": "role",
        "publish": True,
        "behalf": True,
        "comment": comment,
    }
    assert StakeholderCommentForm(data=data).is_valid() == expected
