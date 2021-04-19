import pytest
from model_bakery import baker

from ..models import Stakeholder


@pytest.fixture
def make_stakeholder(make_contact):
    def _make_stakeholder(_make_contact=False, **kwargs):
        res = baker.make(Stakeholder, **kwargs)
        if _make_contact:
            make_contact(_fill_optional=["email", "name"], stakeholder=res)
        return res

    return _make_stakeholder


@pytest.fixture
def stakeholder(make_stakeholder):
    return make_stakeholder()
