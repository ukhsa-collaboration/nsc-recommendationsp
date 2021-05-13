from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now

import pytest
from freezegun import freeze_time

from nsc.notify.models import Email
from nsc.notify.tasks import update_stale_email_statuses


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "status",
    [
        Email.STATUS.pending,
        Email.STATUS.delivered,
        Email.STATUS.permanent_failure,
        Email.STATUS.temporary_failure,
        Email.STATUS.technical_failure,
    ],
)
def test_emails_are_not_in_sending_status___statuses_arent_updated(
    status, notify_client_mock, make_email
):
    email = make_email(status=status, notify_id="notify_id")
    orig_modified_time = email.modified

    with freeze_time(now() + timedelta(minutes=settings.NOTIFY_STALE_MINUTES)):
        update_stale_email_statuses()

        email.refresh_from_db()

        assert email.modified == orig_modified_time
        assert email.status == status
        notify_client_mock.get_notification_by_id.assert_not_called()


@pytest.mark.parametrize(
    "status",
    [
        Email.STATUS.sending,
        Email.STATUS.created,
    ],
)
def test_emails_are_not_stale___statuses_arent_updated(
    status, notify_client_mock, make_email
):
    email = make_email(status=status, notify_id="notify_id")
    orig_modified_time = email.modified

    with freeze_time(now() + timedelta(minutes=settings.NOTIFY_STALE_MINUTES - 1)):
        update_stale_email_statuses()

        email.refresh_from_db()

        assert email.modified == orig_modified_time
        assert email.status == status
        notify_client_mock.get_notification_by_id.assert_not_called()


@pytest.mark.parametrize(
    "status",
    [
        Email.STATUS.sending,
        Email.STATUS.created,
    ],
)
def test_emails_do_not_have_notify_id___statuses_arent_updated(
    status, notify_client_mock, make_email
):
    email = make_email(status=status, notify_id="")
    orig_modified_time = email.modified

    with freeze_time(now() + timedelta(minutes=settings.NOTIFY_STALE_MINUTES)):
        update_stale_email_statuses()

        email.refresh_from_db()

        assert email.modified == orig_modified_time
        assert email.status == status
        notify_client_mock.get_notification_by_id.assert_not_called()


@pytest.mark.parametrize(
    "status",
    [
        Email.STATUS.sending,
        Email.STATUS.created,
    ],
)
@pytest.mark.parametrize(
    "new_status",
    [
        Email.STATUS.sending,
        Email.STATUS.created,
        Email.STATUS.delivered,
        Email.STATUS.permanent_failure,
        Email.STATUS.temporary_failure,
        Email.STATUS.technical_failure,
    ],
)
def test_emails_are_stale___statuses_are_updated(
    status, new_status, notify_client_mock, make_email
):
    email = make_email(status=status, notify_id="notify_id")

    with freeze_time(now() + timedelta(minutes=settings.NOTIFY_STALE_MINUTES)):
        notify_client_mock.get_notification_by_id.return_value = {"status": new_status}

        update_stale_email_statuses()

        email.refresh_from_db()

        assert email.modified == now()
        assert email.status == new_status
        notify_client_mock.get_notification_by_id.assert_called_once_with(
            email.notify_id
        )
