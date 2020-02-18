import pytest
from model_bakery import baker

from nsc.organisation.models import Organisation

from ..models import Contact


@pytest.fixture
def make_contact(make_organisation):
    organisation = make_organisation()
    phone = 123456000

    def _make_contact():
        return baker.make(Contact, phone=phone + 1, organisation=organisation)

    return _make_contact


@pytest.fixture
def contact(make_contact):
    return make_contact()


@pytest.fixture
def make_organisation():
    def _make_organisation():
        return baker.make(Organisation)

    return _make_organisation


@pytest.fixture
def organisation(make_organisation):
    return make_organisation()
