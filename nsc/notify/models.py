import json
import logging

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from model_utils import Choices

from .client import send_email


logger = logging.getLogger(__name__)


class EmailQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=Email.STATUS.pending)

    def sending(self):
        return self.filter(status=Email.STATUS.sending)

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


class Email(TimeStampedModel):
    """
    Email object that will be picked up the scheduler and sent.

    Every minute the existing email objects in a state to be sent
    (pending, temporary failure or technical failure) will be sent
    to the notify service.
    """

    STATUS = Choices(
        ("pending", _("Pending")),
        ("sending", _("Sending")),
        ("delivered", _("Delivered")),
        ("permanent-failure", "permanent_failure", _("Permanent Failure")),
        ("temporary-failure", "temporary_failure", _("Temporary Failure")),
        ("technical-failure", "technical_failure", _("Technical Failure")),
    )

    notify_id = models.CharField(max_length=50)
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

        resp = send_email(
            self.address, self.template_id, context=self.context, reference=str(self.id)
        )

        if "error" not in resp:
            self.status = self.STATUS.sending
            self.notify_id = resp["id"]
        else:
            logger.error(
                f"Failed to send email {self.id}, response: {json.dumps(resp)}"
            )

        self.save()


def generate_token():
    return get_random_string(50)


class ReceiptUserToken(TimeStampedModel):
    token = models.CharField(max_length=50, default=generate_token)

    def __str__(self):
        return self.token
