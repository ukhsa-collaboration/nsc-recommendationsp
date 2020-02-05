import pytest
from model_bakery import baker

from nsc.condition.models import Condition


# All tests require the database
pytestmark = pytest.mark.django_db


def test_factory_create():
    """
    Test that we can create an instance via our object factory.
    """
    instance = baker.make(Condition)
    assert isinstance(instance, Condition)
