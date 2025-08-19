import logging

from django.conf import settings

from notifications_python_client.errors import APIError
from notifications_python_client.notifications import NotificationsAPIClient


logger = logging.getLogger(__name__)

if settings.NOTIFY_SERVICE_ENABLED and settings.NOTIFY_SERVICE_API_KEY:
    client = NotificationsAPIClient(settings.NOTIFY_SERVICE_API_KEY)
else:
    client = None


def send_email(address, template, context=None, reference=None):
    logger.info(f"Sending email with reference: {reference}")
    if client is None:
        logger.warning(f"Email service not enabled - email {reference} not sent")
        return

    try:
        params = {
            "email_address": address,
            "template_id": template,
            "personalisation": context,
            "reference": reference,
        }
        response = client.send_email_notification(**params)
        logger.info(f"Successfully received response from send email")
        return response
    except APIError as e:
        logger.error(f"Email API error: {e.response.json()}")
        return e.response.json()


def get_email_status(notify_id):
    logger.info(f"Getting email status with notify id: {notify_id}")
    if client is None:
        return
    try:
        response = client.get_notification_by_id(notify_id)
        logger.info(f"Successfully received response from get notification by id")
        return response
    except APIError as e:
        logger.error(f"Get email status from notify error: {e}")
        return e.response.json()
