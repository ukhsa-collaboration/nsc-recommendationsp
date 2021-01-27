import pytest
from model_bakery import baker

from nsc.stakeholder.models import Stakeholder

from ..models import Contact


@pytest.fixture
def make_contact(make_stakeholder):
    stakeholder = make_stakeholder()
    phone = 123456000

    def _make_contact():
        return baker.make(Contact, phone=phone + 1, stakeholder=stakeholder)

    return _make_contact


@pytest.fixture
def contact(make_contact):
    return make_contact()


@pytest.fixture
def make_stakeholder():
    def _make_stakeholder():
        return baker.make(Stakeholder)

    return _make_stakeholder


@pytest.fixture
def stakeholder(make_stakeholder):
    return make_stakeholder()
