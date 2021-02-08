from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import override_settings

import freezegun
import pytest


@pytest.fixture(autouse=True)
def tmp_media():
    with TemporaryDirectory() as d, override_settings(MEDIA_ROOT=d):
        yield d


@pytest.fixture(autouse=True)
def freeze_time():
    with freezegun.freeze_time() as t:
        yield t


@pytest.fixture()
def logger_mock():
    def _logger_mock(name):
        return patch(f"{name}.logger")

    return _logger_mock
