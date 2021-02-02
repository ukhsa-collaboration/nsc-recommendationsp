from tempfile import TemporaryDirectory

from django.test import override_settings

import pytest


@pytest.fixture(autouse=True)
def tmp_media():
    with TemporaryDirectory() as d, override_settings(MEDIA_ROOT=d):
        print(d)
        yield d
