===========
Development
===========

This project uses Python 3.6, and specifies its node and yarn versions in `.nvmrc` and
`.yvmrc` respectively.

These commands assume you have checked out the project and are in the root of the
repository.


Running with docker
===================

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


Running manually
================

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

Initialising the database
-------------------------
There is a set of django-extensions scripts that can be used to scrape data from the
existing National Screening Committee (legacy) `web site <https://legacyscreening.phe.org.uk/screening-recommendations.php>`_.

* First generate an index containing the list of pages for each condition screened::

    python manage.py runscript generate_legacy_index

* Then run the various scripts to scrape and load the data::

    python manage.py runscript scrape_conditions
    python manage.py runscript scrape_policies

The order is important since there are foreign keys to keep in order.

Scraping data from the legacy site is just a temporary measure duing the initial
phases of development. Once the models and content have been finalised the database
will be dumped to generate a final fixtures file.
