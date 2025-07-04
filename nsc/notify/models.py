import json
import logging
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import JSONField
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from model_utils import Choices

from .client import get_email_status, send_email


logger = logging.getLogger(__name__)


class EmailQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=Email.STATUS.pending)

    def sending(self):
        return self.filter(status__in=[Email.STATUS.sending, Email.STATUS.created])

    def delivered(self):
        return self.filter(status=Email.STATUS.delivered)

    def permanent_failure(self):
        return self.filter(status=Email.STATUS.permanent_failure)

    def temporary_failure(self):
        return self.filter(status=Email.STATUS.temporary_failure)

    def technical_failure(self):
        return self.filter(status=Email.STATUS.technical_failure)

    def to_send(self):
        return self.filter(
            status__in=[
                Email.STATUS.pending,
                Email.STATUS.technical_failure,
                Email.STATUS.temporary_failure,
            ]
        )

    def done(self):
        return self.filter(
            status__in=[Email.STATUS.delivered, Email.STATUS.permanent_failure]
        )

    def stale(self):
        """
        Fetches all email objects that have not changed in 5 minutes
        """
        return self.filter(
            modified__lte=now() - timedelta(minutes=settings.NOTIFY_STALE_MINUTES)
        )

    def with_notify_id(self):
        return self.exclude(notify_id="")


class Email(TimeStampedModel):
    """
    Email object that will be picked up the scheduler and sent.

    Every minute the existing email objects in a state to be sent
    (pending, temporary failure or technical failure) will be sent
    to the notify service.
    """

    STATUS = Choices(
        ("pending", _("Pending")),
        ("created", _("Created")),
        ("sending", _("Sending")),
        ("delivered", _("Delivered")),
        ("permanent-failure", "permanent_failure", _("Permanent Failure")),
        ("temporary-failure", "temporary_failure", _("Temporary Failure")),
        ("technical-failure", "technical_failure", _("Technical Failure")),
    )

    notify_id = models.CharField(max_length=50, default="", blank=True, editable=False)
    address = models.EmailField()
    template_id = models.CharField(max_length=50)
    context = JSONField(default=dict)
    status = models.CharField(
        choices=STATUS,
        max_length=max(len(v) for v in STATUS._db_values),
        default=STATUS.pending,
    )
    attempts = models.PositiveSmallIntegerField(default=0)

    objects = EmailQuerySet.as_manager()

    def send(self):
        self.attempts += 1

        logger.info(f"sending email: {self.id}")
        resp = send_email(
            self.address, self.template_id, context=self.context, reference=str(self.id)
        )

        if resp and isinstance(resp, dict):
            errors = resp.get("errors", [])
            if errors and isinstance(errors, list):
                first_error = errors[0]
                if isinstance(first_error, dict) and first_error.get("error") == "ValidationError":
                    self.status = self.STATUS.permanent_failure
            else:
                logger.error(
                    f"Failed to send email {self.id}, response: {json.dumps(resp)}"
                )
        else:
            logger.error(f"Response is None or not a valid dict: {resp}")

        self.save()

    def update_status(self):
        resp = get_email_status(self.notify_id)

        if resp and "status" in resp:
            self.status = resp["status"]
            self.save()
        else:
            logger.error(
                f"Failed to get email status {self.id}, response: {json.dumps(resp)}"
            )


def generate_token():
    return get_random_string(50)


class ReceiptUserToken(TimeStampedModel):
    token = models.CharField(max_length=50, default=generate_token)

    def __str__(self):
        return self.token
