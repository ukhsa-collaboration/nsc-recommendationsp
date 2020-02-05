import pytest
from model_bakery import baker

from nsc.utils.models import is_fetched

from ..models import Policy


# All tests require the database
pytestmark = pytest.mark.django_db


def test_factory_create():
    """
    Test that we can create an instance via our object factory.
    """
    instance = baker.make(Policy)
    assert isinstance(instance, Policy)


def test_active():
    """
    Test the active() method on the manager only returns active policies.
    """
    baker.make(Policy, is_active=True)
    baker.make(Policy, is_active=False)
    expected = [obj.pk for obj in Policy.objects.filter(is_active=True)]
    actual = [obj.pk for obj in Policy.objects.active()]
    assert expected == actual


def test_active_selected_related():
    """
    Test that Policy object fetches also include Conditions.
    """
    baker.make(Policy, is_active=True)
    policy = Policy.objects.active().first()
    assert is_fetched(policy, "condition")
