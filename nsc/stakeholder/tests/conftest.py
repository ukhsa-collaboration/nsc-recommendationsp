import pytest
from model_bakery import baker

from ..models import Stakeholder


@pytest.fixture
def make_stakeholder():
    def _make_stakeholder(**kwargs):
        return baker.make(Stakeholder, **kwargs)

    return _make_stakeholder


@pytest.fixture
def stakeholder(make_stakeholder):
    return make_stakeholder()
