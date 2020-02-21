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

.. list-table::
    :header-rows: 1

    * - Variable
      - Description


    * - ``DJANGO_CONFIGURATION``
      - Select the configuration to use; one of ``Dev``, ``Test``, ``Stage`` or ``Prod``

        Equivalent to ``manage.py <cmd> --configuration=<config>``


    * - ``DJANGO_ALLOWED_HOSTS``

      - A comma separated list of allowed hosts. Must be set for deployed
        configurations.

        Example::

            DJANGO_ALLOWED_HOSTS="example.com,example.net"

    * - ``DATABASE_HOST``, ``DATABASE_PORT``, ``DATABASE_NAME``

      - Details of the PostgreSQL database. User and password are set as secrets

    * - ``DJANGO_SECRETS_DIR``

      - Path to dir which contains configuration secrets for deployed configurations.


Secrets
-------

The deployed configurations will require these variables, and will look for these values
in files under ``SECRETS_DIR``.

These are optional for other configurations (ie ``Dev`` and ``Test``), and should still
be set there using environment variables.


.. list-table::
    :header-rows: 1

    * - Variable
      - Description


    * - ``DJANGO_SECRET_KEY``

      - Secret key.


    * - ``DATABASE_USER``, ``DATABASE_PASSWORD``

      - PostgreSQL login credentials


Adding a setting
================

For non-secrets:

#. Add a default to the ``Common`` configuration, using the appropriate `value class`_

#. If it required for deployments, redefine it in the ``Deployed`` configuration.

#. Add an entry to the ``ConfigMap`` in ``openshift-template.yaml``, with a default
   value from the ``parameters`` if appropriate.


For secrets:

#. Add a default to the ``Common`` configuration, using the appropriate `value class`_

#. Add the secret to the ``Deployed`` in the ``Deployed`` configuration using
   ``self.get_secret()``.

#. Add an entry to the ``Secret`` in ``openshift-template.yaml``, with a default
   value from the ``parameters`` if appropriate.

.. _value class: https://django-configurations.readthedocs.io/en/stable/values/
