from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab
from configurations import importer


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nsc.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")

importer.install()

app = Celery("nsc")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "send-emails": {
        "task": "nsc.notify.tasks.send_pending_emails",
        "schedule": crontab(minute="*"),
    },
    "send-open-review-notifications": {
        "task": "nsc.review.tasks.send_open_review_notifications",
        "schedule": crontab(minute="*"),
    },
    "send-decided-notifications": {
        "task": "nsc.review.tasks.send_published_notifications",
        "schedule": crontab(minute="*"),
    },
}
