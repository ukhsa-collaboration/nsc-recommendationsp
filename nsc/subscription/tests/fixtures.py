import pytest
from model_bakery import baker

from ..models import Subscription


@pytest.fixture
def make_subscription():
    def _make(**kwargs):
        return baker.make(Subscription, **kwargs)

    return _make
