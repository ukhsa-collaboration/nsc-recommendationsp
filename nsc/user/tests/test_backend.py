from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.test.client import RequestFactory
from django.utils.timezone import now

import pytest
from model_bakery import baker

from nsc.user.backend import UniqueSessionAdfsBackend


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.fixture
def mock_adfs():
    with patch(
        "django_auth_adfs.backend.AdfsAuthCodeBackend.authenticate"
    ) as mock_adfs_authenticate:
        yield {"authenticate": mock_adfs_authenticate}


def test_no_request_is_given___base_adfs_result_is_returned(user, mock_adfs):
    mock_adfs["authenticate"].return_value = user

    backend = UniqueSessionAdfsBackend()

    assert backend.authenticate(request=None) == user


def test_base_adfs_returns_no_user___base_adfs_result_is_returned(user, mock_adfs):
    mock_adfs["authenticate"].return_value = None
    request = RequestFactory().get("/")

    backend = UniqueSessionAdfsBackend()

    assert backend.authenticate(request=request) is None


def test_base_adfs_returns_anonymous_user___base_adfs_result_is_returned(mock_adfs):
    user = AnonymousUser()
    mock_adfs["authenticate"].return_value = user
    request = RequestFactory().get("/")

    backend = UniqueSessionAdfsBackend()

    assert backend.authenticate(request=request) == user


def test_user_has_no_last_session___base_adfs_result_is_returned(user, mock_adfs):
    mock_adfs["authenticate"].return_value = user
    request = RequestFactory().get("/")

    backend = UniqueSessionAdfsBackend()

    assert backend.authenticate(request=request) == user


def test_last_session_has_expired___base_adfs_result_is_returned(fake_user, mock_adfs):
    session = baker.make(Session, expire_date=now() - timedelta(seconds=1))
    user = fake_user(last_session_id=session.session_key)

    mock_adfs["authenticate"].return_value = user
    request = RequestFactory().get("/")

    backend = UniqueSessionAdfsBackend()

    assert backend.authenticate(request=request) == user


def test_last_session_matches_current_session___base_adfs_result_is_returned(
    fake_user, mock_adfs
):
    session = baker.make(Session, expire_date=now() + timedelta(days=1))
    user = fake_user(last_session_id=session.session_key)

    mock_adfs["authenticate"].return_value = user
    request = RequestFactory().get("/")
    request.session = session

    backend = UniqueSessionAdfsBackend()

    assert backend.authenticate(request=request) == user


def test_current_session_does_not_match_last_session_which_is_not_expired___none_is_returned(
    fake_user, mock_adfs
):
    last_session = baker.make(Session, expire_date=now() + timedelta(days=1))
    user = fake_user(last_session_id=last_session.session_key)

    current_session = baker.make(Session, expire_date=now() + timedelta(days=1))

    mock_adfs["authenticate"].return_value = user
    request = RequestFactory().get("/")
    request.session = current_session

    backend = UniqueSessionAdfsBackend()

    assert backend.authenticate(request=request) is None
