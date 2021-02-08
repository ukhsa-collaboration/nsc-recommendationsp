========
Settings
========

Overview
=========

This project uses `django-configurations`_ to manage configurations for different
environments; define the environment variable ``DJANGO_CONFIGURATION`` to select a
development configuration. The primary configurations are

* ``Dev`` - local development
* ``Test`` - used when running tests
* ``Stage`` - staging deployment
* ``Prod`` - production deployment

Each of these look to override their defaults via environment variables, and the
deployed configurations look for some as secrets on disk.

.. _django-configurations: https://django-configurations.readthedocs.io/


Settings
========

Environment variables
---------------------

.. envvar:: DJANGO_CONFIGURATION

    Select the configuration to use; one of ``Dev``, ``Test``, ``Stage`` or ``Prod``

    Equivalent to ``manage.py <cmd> --configuration=<config>``


.. envvar:: DJANGO_ALLOWED_HOSTS

    A comma separated list of allowed hosts. Must be set for deployed
    configurations.

    Example::

        DJANGO_ALLOWED_HOSTS="example.com,example.net"


.. envvar:: DATABASE_HOST, DATABASE_PORT, DATABASE_NAME

    Details of the PostgreSQL database. User and password are set as secrets


.. envvar:: DJANGO_SECRETS_DIR

    Path to dir which contains configuration secrets for deployed configurations.


.. envvar:: OBJECT_STORAGE_BUCKET_NAME, OBJECT_STORAGE_DOMAIN_NAME

    The name of the bucket used for uploaded files and the fully qualified
    domain name from where the files are served.


.. envvar:: NOTIFY_TEMPLATE_CONSULTATION_INVITATION, NOTIFY_TEMPLATE_PUBLIC_COMMENT, NOTIFY_TEMPLATE_STAKEHOLDER_COMMENT, NOTIFY_TEMPLATE_CONSULTATION_OPEN

    The unique identifiers for each of the templates used to send notifications
    using the UK GOV Notify Service.

.. envvar:: PHE_COMMUNICATIONS_EMAIL

    The email address to send notifications for the PHE communications team to.

.. envvar:: CONSULTATION_COMMENT_ADDRESS

    The email address where comments during the consultation period are sent


Secrets
-------

The deployed configurations will require these variables, and will look for these values
in files under ``SECRETS_DIR``.

These are optional for other configurations (ie ``Dev`` and ``Test``), and should still
be set there using environment variables.


.. envvar:: DJANGO_SECRET_KEY

    Secret key.


.. envvar:: DATABASE_USER, DATABASE_PASSWORD

    PostgreSQL login credentials


.. envvar:: OBJECT_STORAGE_KEY_ID, OBJECT_STORAGE_SECRET_KEY

    The S3-compatible storage server credentials


.. envvar:: NOTIFY_SERVICE_API_KEY

    The key for the UK GOV Notify service. There are also a set of unique identifiers
    for each of the email message templates.


Adding a setting
================

For non-secrets:

#. Add a default to the ``Common`` configuration, using the appropriate `value class`_.

#. If it is optional for development but required for deployment, redefine it in the
   ``Deployed`` configuration with the argument ``environ_required=True``.

#. Add an entry to the ``ConfigMap`` in ``openshift-template.yaml``, with a default
   value from the ``parameters`` if appropriate.


For secrets:

#. Add a default to the ``Common`` configuration, using the appropriate `value class`_.

#. Add the secret to the ``Deployed`` configuration using ``get_secret(...)``.

#. Add an entry to the ``Secret`` in ``openshift-template.yaml``, with a default
   value from the ``parameters`` if appropriate.

.. _value class: https://django-configurations.readthedocs.io/en/stable/values/
