from django.conf import settings

from notifications_python_client.notifications import NotificationsAPIClient


client = NotificationsAPIClient(settings.NOTIFY_SERVICE_API_KEY)


def send_email(address, template, context=None):
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
