from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.test import override_settings

import freezegun
import pytest
from model_bakery import baker


@pytest.fixture()
def erm_permission():
    return Permission.objects.get(
        codename="evidence_review_manager",
        content_type__model="review",
        content_type__app_label="review",
    )


@pytest.fixture()
def erm_user(erm_permission):
    user = baker.make(get_user_model())
    user.user_permissions.add(erm_permission)
    return user


@pytest.fixture()
def non_user():
    return baker.make(get_user_model())


@pytest.fixture()
def test_access_forbidden(non_user, client):
    def _test_access_forbidden(url):
        response = client.get(url, user=non_user, expect_errors=True)
        assert response.status == "403 Forbidden"

    return _test_access_forbidden


@pytest.fixture()
def test_access_no_user(client):
    def _test_access_forbidden(url):
        response = client.get(url)
        assert response.status == "302 Found"
        assert response.url == f"/accounts/login/?next={url}"

    return _test_access_forbidden


@pytest.fixture()
def test_access_not_user_can_access(erm_permission, client):
    def _test_access_not_user_can_access(url):
        user = baker.make(get_user_model())
        user.user_permissions.add(erm_permission)
        response = client.get(url, user=user, expect_errors=True)
        assert response.status == "200 OK"

    return _test_access_not_user_can_access


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


@pytest.fixture(autouse=True)
def email_settings():
    with override_settings(
        PHE_COMMUNICATIONS_EMAIL="comms@example.com",
        PHE_COMMUNICATIONS_NAME="PHE Comms",
        PHE_HELP_DESK_EMAIL="hepdesk@example.com",
        CONSULTATION_COMMENT_ADDRESS="comments@example.com",
        NOTIFY_SERVICE_API_KEY="NOTIFY_SERVICE_API_KEY",
        NOTIFY_TEMPLATE_CONSULTATION_OPEN="NOTIFY_TEMPLATE_CONSULTATION_OPEN",
        NOTIFY_TEMPLATE_CONSULTATION_OPEN_COMMS="NOTIFY_TEMPLATE_CONSULTATION_OPEN_COMMS",
        NOTIFY_TEMPLATE_SUBSCRIBER_CONSULTATION_OPEN="NOTIFY_TEMPLATE_SUBSCRIBER_CONSULTATION_OPEN",
        NOTIFY_TEMPLATE_DECISION_PUBLISHED="NOTIFY_TEMPLATE_DECISION_PUBLISHED",
        NOTIFY_TEMPLATE_SUBSCRIBER_DECISION_PUBLISHED="NOTIFY_TEMPLATE_SUBSCRIBER_DECISION_PUBLISHED",
        NOTIFY_TEMPLATE_PUBLIC_COMMENT="NOTIFY_TEMPLATE_PUBLIC_COMMENT",
        NOTIFY_TEMPLATE_STAKEHOLDER_COMMENT="NOTIFY_TEMPLATE_STAKEHOLDER_COMMENT",
        NOTIFY_TEMPLATE_SUBSCRIBED="NOTIFY_TEMPLATE_SUBSCRIBED",
        NOTIFY_TEMPLATE_UPDATED_SUBSCRIPTION="NOTIFY_TEMPLATE_UPDATED_SUBSCRIPTION",
        NOTIFY_TEMPLATE_UNSUBSCRIBE="NOTIFY_TEMPLATE_UNSUBSCRIBE",
        NOTIFY_TEMPLATE_HELP_DESK="NOTIFY_TEMPLATE_HELP_DESK",
        NOTIFY_TEMPLATE_HELP_DESK_CONFIRMATION="NOTIFY_TEMPLATE_HELP_DESK_CONFIRMATION",
    ):
        yield


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
