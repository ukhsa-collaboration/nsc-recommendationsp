import logging

from django.conf import settings

from notifications_python_client.errors import APIError
from notifications_python_client.notifications import NotificationsAPIClient


logger = logging.getLogger(__name__)

logger.info("Notify client called")

if settings.NOTIFY_SERVICE_ENABLED and settings.NOTIFY_SERVICE_API_KEY:
    client = NotificationsAPIClient(settings.NOTIFY_SERVICE_API_KEY)
    logger.info("Notify service initialized successfully")
else:
    client = None
    logger.warning(
        "Notify service not initialized - check NOTIFY_SERVICE_ENABLED and API key"
    )
    # Print the values to see what went wrong
    logger.info(f"NOTIFY_SERVICE_ENABLED: {settings.NOTIFY_SERVICE_ENABLED}")


def send_email(address, template, context=None, reference=None):
    logger.info(f"Sending email to {address} using template {template}")
    if client is None:
        logger.info(
            f"Email service not enabled - email not sent to {address} {template} {context}"
        )
        return

    try:
        params = {
            "email_address": address,
            "template_id": template,
            "personalisation": context,
            "reference": reference,
        }
        logger.info(f"Sending email with params: {params}")

        response = client.send_email_notification(**params)
        logger.info(f"Email sent successfully with response: {response}")
        return response
    except APIError as e:
        logger.error(f"Email API error: {e.response.json()}")
        return e.response.json()


def get_email_status(notify_id):
    if client is None:
        logger.info(f"Email service not enabled - cannot check status for {notify_id}")
        return

    try:
        response = client.get_notification_by_id(notify_id)
        logger.info(f"Email status response: {response}")
        return response
    except APIError as e:
        logger.error(f"Email API error: {e.response.json()}")
        return e.response.json()
