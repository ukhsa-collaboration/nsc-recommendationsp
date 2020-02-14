===========
Development
===========

This project uses Python 3.6, and specifies its node and yarn versions in `.nvmrc` and
`.yvmrc` respectively.

These commands assume you have checked out the project and are in the root of the
repository.


Running locally with docker
===========================

The default ``dev-docker-compose.yml`` will run Django and node in their own
containers::

    cp dev-docker-compose.yml.default dev-docker-compose.yml
    docker-compose -f dev-docker-compose.yml up

Modify ``dev-docker-compose.yml`` to disable services if you'd prefer to run some
manually outside a container during development.

To perform a command in a running container use the ``exec`` command; for example::

    docker-compose -f dev-docker-compose.yml exec django ./manage.py createsuperuser

where ``django`` is the container name. Commands in the documentation will omit this
prefix.


Building frontend only
----------------------

To just use docker to build the frontend resources::

    docker-compose -f dev-docker-compose.yml build frontend
    docker-compose -f dev-docker-compose.yml run -e FRONTEND_MODE=build frontend


Running locally without docker
==============================

We recommend using:

* `pyenv <https://github.com/pyenv/pyenv>`_ to manage python versions
* `nvm <https://github.com/creationix/nvm>`_ to manage node versions
* `yvm <https://yvm.js.org/docs/overview>`_ to manage yarn versions


Django
------

Install the project into a virtual environment::

    python3.6 -m venv ../venv
    source ../venv/bin/activate
    pip install -r requirements-dev.txt

Create a superuser and load the basic fixtures::

    ./manage.py migrate
    ./manage.py createsuperuser


Frontend
--------

Install the project dependencies::

    nvm install
    nvm use
    yvm install
    yvm use
    yarn install

Frontend resources can be built in one of three ways:

* Serve from a local webpack development server (recommended when working on
  the frontend)::

    npm run watch

* Build into a single JavaScript file for use locally (recommended when working
  on the backend)::

    npm run dev

* Build into separate JavaScript and CSS files, minified for deployment::

    npm run build

When the frontend resources are being served from a webpack development server (using
``watch``), the Django development server will automatically detect and switch to use
it, enabling hot module replacement. If you serve it from a different host or port you
can tell Django by setting the environment variables ``WEBPACK_DEV_HOST`` and
``WEBPACK_DEV_PORT``, eg ``WEBPACK_DEV_HOST=192.168.1.72 ./manage.py runserver 0:8000``.

For deployment the resources are built into ``frontend/dist/``, which is then included
in the list of dirs checked by ``collectstatic``.


Initialising the database
=========================

There is a set of django-extensions scripts that can be used to scrape data from the
existing National Screening Committee `legacy website`_.

.. _legacy website: https://legacyscreening.phe.org.uk/screening-recommendations.php

* First generate an index containing the list of pages for each condition screened::

    python manage.py runscript generate_legacy_index

* Then run the script to scrape and load the data::

    python manage.py runscript scrape_policies


(If running Django using docker, replace ``python`` in the above commands with
``docker-compose -f dev-docker-compose.yml exec django``).

Scraping data from the legacy site is just a temporary measure during the initial
phases of development. Once the models and content have been finalised the database
will be dumped to generate a final fixtures file.


Running tests
=============

To run tests and linting checks locally, ensure the containers are running, then run::

    pytest

A summary coverage report will be printed to the console, with an HTML report at
``htmlcov/index.html``.

By default the test database will be reused across test sessions to reduce
initialisation time. If the test database to becomes corrupted (for example, if you
roll back migrations, or start seeing unexpected migration issues) you can force
recreation with::

    pytest --create-db


Development standards
=====================

This project uses black_, flake8_ and isort_ to enforce consistent python styles. These
are checked automatically by ``pytest``. To use them to automatically reformat your
code::

    black nsc
    isort -rc nsc

We recommend using editor plugins to apply these at the point of saving Python files.

.. _black: https://github.com/python/black#the-black-code-style
.. _flake8: https://pypi.org/project/flake8/
.. _isort: https://github.com/timothycrosley/isort


Documentation
=============

The documentation uses sphinx_, with doc8_ for linting. Build with::

    doc8
    sphinx-build docs docs/_build

.. _sphinx: https://www.sphinx-doc.org/
.. _doc8: https://pypi.org/project/doc8/
