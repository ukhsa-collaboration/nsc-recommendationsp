from unittest.mock import patch

import pytest
from model_bakery import baker

from ..models import Email


@pytest.fixture(autouse=True)
def notify_client_mock():
    with patch("nsc.notify.client.get_client") as mock_get_client:
        mock_client = mock_get_client.return_value
        yield mock_client


@pytest.fixture()
def make_email():
    def _make_email(**kwargs):
        return baker.make(Email, **kwargs)

    return _make_email
