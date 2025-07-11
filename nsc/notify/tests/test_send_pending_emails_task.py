import json
import uuid

import pytest

from ..models import Email
from ..tasks import send_pending_emails


# All tests require the database
pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "status",
    [Email.STATUS.sending, Email.STATUS.permanent_failure, Email.STATUS.delivered],
)
def test_no_emails_to_be_sent_no_emails_are_sent(
    status, notify_client_mock, make_email
):
    make_email(status=status)

    send_pending_emails()

    notify_client_mock.send_email_notification.assert_not_called()


@pytest.mark.parametrize(
    "status",
    [
        Email.STATUS.pending,
        Email.STATUS.technical_failure,
        Email.STATUS.temporary_failure,
    ],
)
def test_emails_to_be_sent_exist_emails_are_sent_and_statuses_are_updated(
    status, notify_client_mock, make_email
):
    notify_id = uuid.uuid4().hex
    notify_client_mock.send_email_notification.return_value = {"id": notify_id}

    email = make_email(status=status)

    send_pending_emails()
    email.refresh_from_db()

    notify_client_mock.send_email_notification.assert_called_once_with(
        email_address=email.address,
        template_id=email.template_id,
        personalisation=email.context,
        reference=str(email.id),
    )
    assert email.status == Email.STATUS.sending
    assert email.attempts == 1
    assert email.notify_id == notify_id


@pytest.mark.parametrize(
    "status",
    [
        Email.STATUS.pending,
        Email.STATUS.technical_failure,
        Email.STATUS.temporary_failure,
    ],
)
def test_notify_service_returns_an_error_error_is_logged_and_email_is_not_updated(
    status, notify_client_mock, make_email, logger_mock
):
    with logger_mock("nsc.notify.models") as mock_logger:
        notify_client_mock.send_email_notification.return_value = {
            "errors": [{"error": "Some Error"}]
        }

        email = make_email(status=status)
        orig_notify_id = email.notify_id

        send_pending_emails()
        email.refresh_from_db()

        notify_client_mock.send_email_notification.assert_called_once_with(
            email_address=email.address,
            template_id=email.template_id,
            personalisation=email.context,
            reference=str(email.id),
        )
        assert email.status == status
        assert email.attempts == 1
        assert email.notify_id == orig_notify_id
        mock_logger.error.assert_called_once_with(
            f"Failed to send email {email.id}, response: {json.dumps({'errors': [{'error': 'Some Error'}]})}"
        )


def test_too_many_attempts_status_set():
    email = Email(attempts=101)
    email.send()
    assert email.status == Email.STATUS.too_many_attempts


def test_done_includes_too_many_attempts():
    email = Email(status=Email.STATUS.too_many_attempts)
    email.save()
    queryset = Email.objects.done()
    assert email in queryset
