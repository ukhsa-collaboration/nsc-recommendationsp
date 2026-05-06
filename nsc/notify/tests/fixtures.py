from unittest.mock import patch

from model_bakery import baker
import pytest

from ..models import Email


@pytest.fixture(autouse=True)
def notify_client_mock():
    with patch("nsc.notify.client.client") as mock_client:
        yield mock_client


@pytest.fixture()
def make_email():
    def _make_email(**kwargs):
        return baker.make(Email, **kwargs)

    return _make_email
