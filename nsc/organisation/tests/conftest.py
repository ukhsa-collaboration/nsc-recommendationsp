import pytest
from model_bakery import baker

from ..models import Organisation


@pytest.fixture
def make_organisation():
    def _make_organisation(**kwargs):
        return baker.make(Organisation, **kwargs)

    return _make_organisation


@pytest.fixture
def organisation(make_organisation):
    return make_organisation()
