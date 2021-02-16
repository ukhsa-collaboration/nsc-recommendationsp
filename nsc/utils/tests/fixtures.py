from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import override_settings

import freezegun
import pytest
from model_bakery import baker


@pytest.fixture()
def erm_user():
    user = baker.make(get_user_model())
    erm_permission = Permission.objects.get(
        codename="evidence_review_manager",
        content_type__model="review",
        content_type__app_label="review",
    )
    user.user_permissions.add(erm_permission)
    return user


@pytest.fixture()
def non_user():
    return baker.make(get_user_model())


@pytest.fixture()
def test_access_forbidden(non_user, django_app):
    def _test_access_forbidden(url):
        response = django_app.get(url, user=non_user, expect_errors=True)
        assert response.status == "403 Forbidden"
    return _test_access_forbidden


@pytest.fixture()
def test_access_no_user(django_app):
    def _test_access_forbidden(url):
        response = django_app.get(url)
        assert response.status == "302 Found"
        assert response.url == f"/accounts/login/?next={url}"
    return _test_access_forbidden


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
