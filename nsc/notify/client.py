import logging

from django.conf import settings

from notifications_python_client.errors import APIError
from notifications_python_client.notifications import NotificationsAPIClient


logger = logging.getLogger(__name__)


def get_client():
    if settings.NOTIFY_SERVICE_ENABLED and settings.NOTIFY_SERVICE_API_KEY:
        return NotificationsAPIClient(settings.NOTIFY_SERVICE_API_KEY)
    return None


def send_email(address, template, context=None, reference=None):
    client = get_client()
    if client is None:
        logger.info(f"[Notify - Send] {address} {template} {context}")
        return

    try:
        return client.send_email_notification(
            email_address=address,
            template_id=template,
            personalisation=context,
            reference=reference,
        )
    except APIError as e:
        return e.response.json()


def get_email_status(notify_id):
    client = get_client()
    if client is None:
        logger.info(f"[Notify - Get Status] {notify_id}")
        return

    try:
        return client.get_notification_by_id(notify_id)
    except APIError as e:
        return e.response.json()
