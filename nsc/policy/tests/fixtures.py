import pytest
from model_bakery import baker

from nsc.policy.models import Policy


@pytest.fixture
def make_policy():
    def _make_policy(**kwargs):
        return baker.make(Policy, **kwargs)

    return _make_policy
