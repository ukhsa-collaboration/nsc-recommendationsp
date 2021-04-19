===============
Scheduled Tasks
===============

The system has several scheduled tasks ran using celery (although they can be
called from the command line without celery).

A worker is required which can be started using::

    celery -A nsc worker

To start the scheduler use::

    celery -A nsc beat

Tasks
=====

send-open-review-notifications
------------------------------

**Path:** `nsc.review.tasks.send_open_review_notifications`

**Schedule:** Every minute

Creates the notification objects to alert stakeholders that a review has been opened
for a policy.

To run without celery use::

    python manage.py send_open_review_notifications

send-published-notifications
----------------------------

**Path:** `nsc.review.tasks.send_published_notifications`

**Schedule:** Every minute

Creates the notification objects to alert stakeholders that a decision has been
published for a review.

To run without celery use::

    python manage.py send_published_notifications

send-pending-emails
-------------------

**Path:** `nsc.notify.tasks.send_pending_emails`

**Schedule:** Every minute

Sends all pending email notifications using the govuk notify service.

To run without celery use::

    python manage.py send_pending_emails
