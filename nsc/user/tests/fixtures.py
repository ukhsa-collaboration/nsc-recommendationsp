from django.contrib.auth import get_user_model

import pytest
from model_bakery import baker


@pytest.fixture
def fake_user():
    def factory(*args, **kwargs):
        return baker.make(get_user_model(), *args, **kwargs)

    return factory


@pytest.fixture
def user(fake_user):
    return fake_user()
