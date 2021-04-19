===================
Email Notifications
===================

Email notifications are handled by the GovUK Notify system. To schedule an
email for sending create an ``Email`` object in the database. Every minute all,
the first 3000 emails in a "to be sent" state (``Email.STATUS.pending``,
``Email.STATUS.temporary_failure`` and ``Email.STATUS.technical_failure``) will
be sent to the notify service. These emails will be sent and updated to the
``Email.STATUS.sending`` status.

To schedule the email use::

    from nsc.notify.models import Email
    Email.objects.create(
        address=<email_address>,
        template_id=<notify_template_id>,
        context=<context_dict>,
    )

Only the ``address`` and ``template_id`` are required, if supplied the ``context``
should be a dictionary of string keys and values, this is used to personalise the
email content.
