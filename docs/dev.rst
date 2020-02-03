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

To perform a command in a running container:

    docker-compose exec django ./manage.py createsuperuser


Building static only
--------------------

To just use docker to build the static resources::

    docker-compose -f dev-docker-compose.yml build static
    docker-compose -f dev-docker-compose.yml run -e STATIC_MODE=build static


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


Static
------

Install the project dependencies::

    nvm install
    nvm use
    yvm install
    yvm use
    yarn install

Static resources can be built in one of three ways:

* Serve from a local webpack development server (recommended when working on
  the frontend)::

    npm run watch

* Build into a single JavaScript file for use locally (recommended when working
  on the backend)::

    npm run dev

* Build into separate JavaScript and CSS files, minified for deployment::

    npm run build

When the static resources are being served from a webpack development server (using
``watch``), the Django development server will automatically detect and switch to use
it, enabling hot module replacement. If you serve it from a different host or port you
can tell Django by setting the environment variables ``WEBPACK_DEV_HOST`` and
``WEBPACK_DEV_PORT``, eg ``WEBPACK_DEV_HOST=192.168.1.72 ./manage.py runserver 0:8000``.


Running tests
=============

Once you've installed ``requirements-dev.txt`` into a virtual environment, run::

    pytest

This will run all the tests and linting tools, and provide a coverage report on the
console and in the dir ``htmlcov``.


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
