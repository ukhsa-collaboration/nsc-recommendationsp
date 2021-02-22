import pytest

from ..forms import PublicCommentForm


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
        "email": "test@test.com",
        "notify": True,
        "comment_affected": "comment_affected",
        "comment_evidence": "comment_evidence",
        "comment_discussion": "comment_evidence",
        "comment_recommendation": "comment_recommendation",
        "comment_alternatives": "comment_alternatives",
        "comment_other": "comment_other",
    }
    assert PublicCommentForm(data=data).is_valid() == expected


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
        "notify": True,
        "comment_affected": "comment_affected",
        "comment_evidence": "comment_evidence",
        "comment_discussion": "comment_evidence",
        "comment_recommendation": "comment_recommendation",
        "comment_alternatives": "comment_alternatives",
        "comment_other": "comment_other",
    }
    assert PublicCommentForm(data=data).is_valid() == expected


@pytest.mark.parametrize(
    "notify, expected",
    [
        (None, False),  # The notify cannot be None
        ("", False),  # The notify cannot be blank
        (" ", False),  # The notify cannot be empty
        (True, True),
        (False, True),
    ],
)
def test_comment_notify_validation(notify, expected):
    data = {
        "name": "name",
        "email": "email@email.com",
        "notify": notify,
        "comment_affected": "comment_affected",
        "comment_evidence": "comment_evidence",
        "comment_discussion": "comment_evidence",
        "comment_recommendation": "comment_recommendation",
        "comment_alternatives": "comment_alternatives",
        "comment_other": "comment_other",
    }
    assert PublicCommentForm(data=data).is_valid() == expected


def test_comment_at_least_one_comment_field():
    data = {
        "name": "name",
        "email": "email@email.com",
        "notify": True,
        "comment_affected": "",
        "comment_evidence": "",
        "comment_discussion": "",
        "comment_recommendation": "",
        "comment_alternatives": "",
        "comment_other": "",
    }

    form = PublicCommentForm(data=data)
    assert not form.is_valid()
    assert "Please submit at least one comment." in str(form.errors)
