import logging

from ..celery import app
from .models import Email


logger = logging.getLogger(__name__)


@app.task
def send_pending_emails():
    # limit to the first 3000 as a max of 3000 messages can be sent in a minute
    for email in Email.objects.to_send()[:3000]:
        try:
            email.send()
        except Exception as e:
            logger.exception(e)


@app.task
def update_stale_email_statuses():
    for email in Email.objects.sending().stale().with_notify_id():
        try:
            email.update_status()
        except Exception as e:
            logger.exception(e)
