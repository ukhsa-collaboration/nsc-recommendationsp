import sys

from django.conf import settings

from notifications_python_client.notifications import NotificationsAPIClient


if settings.NOTIFY_SERVICE_ENABLED:
    client = NotificationsAPIClient(settings.NOTIFY_SERVICE_API_KEY)
else:
    client = None


def send_email(address, template, context=None):
    if client is None:
        sys.stdout.write(f"[Notify] {address} {template} {context}")
        return

    return client.send_email_notification(
        email_address=address, template_id=template, personalisation=context
    )


def submit_public_comment(context):
    address = settings.CONSULTATION_COMMENT_ADDRESS
    template = settings.NOTIFY_TEMPLATE_PUBLIC_COMMENT
    return send_email(address, template, context)


def submit_stakeholder_comment(context):
    address = settings.CONSULTATION_COMMENT_ADDRESS
    template = settings.NOTIFY_TEMPLATE_STAKEHOLDER_COMMENT
    return send_email(address, template, context)
