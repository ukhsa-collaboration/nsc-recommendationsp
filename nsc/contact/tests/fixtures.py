import pytest
from model_bakery import baker

from ..models import Contact


@pytest.fixture
def make_contact():
    def _make_contact(_fill_optional=True, **kwargs):
        return baker.make(Contact, _fill_optional=_fill_optional, **kwargs)

    return _make_contact


@pytest.fixture
def contact(make_contact):
    return make_contact(_fill_optional=False)
