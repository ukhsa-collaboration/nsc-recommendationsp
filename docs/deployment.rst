==========
Deployment
==========

Overview
=========

This project has two deployed configurations - ``Stage`` and ``Prod``. These are
selected by the ``DJANGO_CONFIGURATION`` environment variable. Both of these
configurations look for their values via environment variable or from secrets stored on
disk.


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

    * - ``SECRETS_DIR``

      - Path to dir which contains configuration secrets.


Secrets
-------

The two deployed configurations will require these variables, and will look for these
values in files under ``SECRETS_DIR``.

These are optional for other configurations (ie ``Dev`` and ``Test``), and should still
be set there using environment variables.


.. list-table::
    :header-rows: 1

    * - Variable
      - Description


    * - ``DJANGO_SECRET_KEY``

      - Secret key.


    * - ``DATABASE_URL``

      - A database URL - see `dj-database-url`__ for syntax. Must be set for deployed
        configurations.

        __ https://pypi.org/project/dj-database-url

        Example::

            DJANGO_DATABASES="postgres://user:pass@localhost:5432/nsc"


    * - ``CACHE_URL``

      - A cache url - see `django-cache-url`__ for syntax.

        __ https://pypi.org/project/django-cache-url/
