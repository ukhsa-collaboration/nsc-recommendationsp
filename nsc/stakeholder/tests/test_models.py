import pytest
from model_bakery import baker

from nsc.policy.models import Policy

from ..models import Stakeholder


# All tests require the database
pytestmark = pytest.mark.django_db


def test_factory_create_policy():
    """
    Test that we can create an instance via our object factory.
    """
    instance = baker.make(Stakeholder)
    assert isinstance(instance, Stakeholder)


def test_public_stakeholders(make_stakeholder):
    """
    Test the public() method on the manager only returns public stakeholders.
    """
    make_stakeholder(is_public=True)
    make_stakeholder(is_public=False)
    expected = [obj.pk for obj in Stakeholder.objects.filter(is_public=True)]
    actual = [obj.pk for obj in Stakeholder.objects.public()]
    assert expected == actual


def test_public_stakeholders_for_policy(make_stakeholder):
    """
    Test the public() method on the manager returns stakeholders for a given policy.
    """
    policies = baker.prepare(Policy, _quantity=2)
    make_stakeholder(is_public=True, policies=[policies[0]])
    make_stakeholder(is_public=True, policies=[policies[1]])
    expected = [obj.pk for obj in Stakeholder.objects.filter(policies=policies[0])]
    actual = [obj.pk for obj in Stakeholder.objects.public(policies[0])]
    assert expected == actual
