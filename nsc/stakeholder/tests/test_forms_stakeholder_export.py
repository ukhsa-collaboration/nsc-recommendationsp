import pytest

from ..forms import ExportForm


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, False),  # The name cannot be None
        ("", False),  # The name cannot be blank
        (" ", False),  # The name cannot be empty
        ("conditions", True),
        ("individual", True),
    ],
)
def test_validation(value, expected, make_policy):
    data = {"export_type": value}
    assert ExportForm(data=data).is_valid() == expected
