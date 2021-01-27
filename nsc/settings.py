from os import environ
from pathlib import Path

from django.utils.translation import gettext_lazy as _

import envdir
from configurations import Configuration


# Common settings
BASE_DIR = Path(__file__).absolute().parent.parent
PROJECT_NAME = "nsc"
CONFIGURATION = environ["DJANGO_CONFIGURATION"]
CONFIG_DIR = environ.get("DJANGO_CONFIG_DIR")
SECRET_DIR = environ.get("DJANGO_SECRET_DIR")


def get_env(name, default=None, required=False, cast=str):
    """
    Get an environment variable

    Arguments:

        name (str): Name of environment variable
        default (Any): default value
        required (bool): If True, raises an ImproperlyConfigured error if not defined
        cast (Callable): function to call with extracted string value.
            Not applied to defaults.
    """

    def _lookup(self):
        value = environ.get(name)

        if value is None and default is not None:
            return default

        if value is None and required:
            raise ValueError(f"{name} not found in env")

        return cast(value)

    return property(_lookup)


def get_secret(name, cast=str):
    """
    Get a secret from disk

    Secrets should be available as the content of `<SECRET_DIR>/<name>`

    All secrets are required

    Arguments:

        name (str): Name of environment variable
        cast (Callable): function to call on extracted string value
    """

    # We don't want this to be called unless we're in a configuration which uses it
    def _lookup(self):
        if not SECRET_DIR:
            raise ValueError(
                f"Secret {name} not found: DJANGO_SECRET_DIR not set in env"
            )

        file = Path(SECRET_DIR) / name
        if not file.exists():
            raise ValueError(f"Secret {file} not found")

        value = file.read_text().strip()
        return cast(value)

    return property(_lookup)


def csv_to_list(value):
    """
    Convert a comma separated list of values into a list.

    Convenience function for use with get_env() and get_secret() ``cast`` argument.
    """
    if value is None:
        return []
    return value.split(",")


class Common(Configuration):
    @classmethod
    def pre_setup(cls):
        """
        If specified, add config dir to environment
        """
        if CONFIG_DIR:
            envdir.Env(CONFIG_DIR)
        super().pre_setup()

    # Name of the configuration class in use
    PROJECT_ENVIRONMENT_SLUG = "{}_{}".format(PROJECT_NAME, CONFIGURATION.lower())

    @property
    def ADMINS(self):
        """
        Look up DJANGO_ADMINS and split into list of (name, email) tuples

        Separate name and email with commas, name+email pairs with semicolons, eg::

            DJANGO_ADMINS="User One,user1@example.com;User Two,user2@example.com"
        """
        value = environ.get("DJANGO_ADMINS")
        if not value:
            return []

        pairs = value.split(";")
        return [pair.rsplit(",", 1) for pair in pairs]

    MANAGERS = ADMINS

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = get_env("DJANGO_SECRET_KEY", default=PROJECT_NAME)

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    # Comma separated list of hosts; for exmaple:
    #   DJANGO_ALLOWED_HOSTS=host1.example.com,host2.example.com
    ALLOWED_HOSTS = get_env("DJANGO_ALLOWED_HOSTS", cast=csv_to_list, default=["*"])

    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "whitenoise.runserver_nostatic",
        "django.contrib.staticfiles",
        "raven.contrib.django.raven_compat",
        "django_extensions",
        "clear_cache",
        "simple_history",
        "storages",
        "django_filters",
        "nsc.condition",
        "nsc.contact",
        "nsc.document",
        "nsc.stakeholder",
        "nsc.policy",
        "nsc.review",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "simple_history.middleware.HistoryRequestMiddleware",
    ]

    ROOT_URLCONF = "nsc.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [BASE_DIR / "templates"],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ]
            },
        }
    ]

    WSGI_APPLICATION = "nsc.wsgi.application"

    # Database
    # https://docs.djangoproject.com/en/1.11/ref/settings/#databases
    DATABASE_HOST = get_env("DATABASE_HOST", default="localhost")
    DATABASE_PORT = get_env("DATABASE_PORT", default=5432, cast=int)
    DATABASE_NAME = get_env("DATABASE_NAME", default=PROJECT_NAME)
    DATABASE_USER = get_env("DATABASE_USER", default=PROJECT_NAME)
    DATABASE_PASSWORD = get_env("DATABASE_PASSWORD", default=PROJECT_NAME)

    @property
    def DATABASES(self):
        """
        Build the databases object here to allow subclasses to override specific values
        """
        return {
            "default": {
                "ENGINE": "django.db.backends.postgresql_psycopg2",
                "HOST": self.DATABASE_HOST,
                "PORT": self.DATABASE_PORT,
                "NAME": self.DATABASE_NAME,
                "USER": self.DATABASE_USER,
                "PASSWORD": self.DATABASE_PASSWORD,
            }
        }

    # Password validation
    # https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
    AUTH_PASSWORD_VALIDATORS = [
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"}
    ]

    # Internationalization
    # https://docs.djangoproject.com/en/1.11/topics/i18n/
    LANGUAGE_CODE = "en"

    LANGUAGES = [("en", _("English"))]

    TIME_ZONE = "Europe/London"

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.11/howto/static-files/
    STATIC_URL = "/static/"
    STATIC_ROOT = BASE_DIR / "static"

    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

    # Additional locations of static files
    STATICFILES_DIRS = [BASE_DIR / "frontend" / "dist"]

    # STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    WHITENOISE_ROOT = BASE_DIR / "public"

    FIXTURE_DIRS = [BASE_DIR / "fixtures"]

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "root": {"level": "WARNING", "handlers": ["sentry"]},
        "formatters": {
            "verbose": {
                "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
            },
            "django.server": {
                "()": "django.utils.log.ServerFormatter",
                "format": "[%(server_time)s] %(message)s",
            },
        },
        "handlers": {
            "sentry": {
                "level": "ERROR",
                "class": "raven.contrib.django.raven_compat.handlers.SentryHandler",
            },
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "django.server": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "django.server",
            },
        },
        "loggers": {
            "django.db.backends": {
                "level": "ERROR",
                "handlers": ["console"],
                "propagate": False,
            },
            "raven": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
            "sentry.errors": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": False,
            },
            "django.server": {
                "handlers": ["django.server"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERYD_WORKER_HIJACK_ROOT_LOGGER = False

    # Settings for the GDS Notify service for sending emails.
    NOTIFY_SERVICE_ENABLED = False
    NOTIFY_SERVICE_API_KEY = get_env("NOTIFY_SERVICE_API_KEY")
    CONSULTATION_COMMENT_ADDRESS = get_env("CONSULTATION_COMMENT_ADDRESS")
    NOTIFY_TEMPLATE_CONSULTATION_INVITATION = get_env(
        "NOTIFY_TEMPLATE_CONSULTATION_INVITATION"
    )
    NOTIFY_TEMPLATE_PUBLIC_COMMENT = get_env("NOTIFY_TEMPLATE_PUBLIC_COMMENT")
    NOTIFY_TEMPLATE_STAKEHOLDER_COMMENT = get_env("NOTIFY_TEMPLATE_STAKEHOLDER_COMMENT")

    # This is the URL for the National Screening Committee where members of
    # the public can leave feedback about the web site.
    PROJECT_FEEDBACK_URL = ""


class Webpack:
    """
    Use as mixin for Dev configuration
    """

    # If static content is being served through the webpack dev server.
    # Needs template context processor for template support.
    WEBPACK_DEV_HOST = get_env("WEBPACK_DEV_HOST", default="{host}")
    WEBPACK_DEV_PORT = get_env("WEBPACK_DEV_PORT", default=8080, cast=int)

    @property
    def WEBPACK_DEV_URL(self):
        value = environ.get("WEBPACK_DEV_URL")
        if value:
            return value
        return f"//{self.WEBPACK_DEV_HOST}:{self.WEBPACK_DEV_PORT}/static/"

    @property
    def LOGGING(self):
        LOGGING = super().LOGGING
        LOGGING["loggers"]["nsc.context_processors"] = {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        }
        return LOGGING

    @property
    def TEMPLATES(self):
        """
        Add a context processor to enable webpack dev server
        """
        TEMPLATES = super().TEMPLATES
        TEMPLATES[0]["OPTIONS"]["context_processors"].append(
            "nsc.context_processors.webpack_dev_url"
        )
        return TEMPLATES


class Dev(Webpack, Common):
    DEBUG = True
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = "/tmp/app-emails"
    INTERNAL_IPS = ["127.0.0.1"]

    @property
    def INSTALLED_APPS(self):
        INSTALLED_APPS = super().INSTALLED_APPS
        INSTALLED_APPS.append("debug_toolbar")
        return INSTALLED_APPS

    @property
    def MIDDLEWARE(self):
        MIDDLEWARE = super().MIDDLEWARE
        MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
        return MIDDLEWARE


class Test(Dev):
    """
    Default test settings
    """

    pass


class TravisCI(Dev):
    """
    Default CI settings for Travis
    """

    DATABASE_NAME = "test_db"
    DATABASE_USER = "postgres"
    DATABASE_PASSWORD = ""


class Build(Common):
    """
    Settings for use when building containers for deployment
    """

    # New paths
    PUBLIC_ROOT = BASE_DIR.parent / "public"
    STATIC_ROOT = PUBLIC_ROOT / "static"
    MEDIA_ROOT = PUBLIC_ROOT / "media"


class Deployed(Build):
    """
    Settings which are for a non-local deployment
    """

    # Redefine values which are not optional in a deployed environment
    ALLOWED_HOSTS = get_env("DJANGO_ALLOWED_HOSTS", cast=csv_to_list, required=True)

    # Some deployed settings are no longer env vars - collect from the secret store
    SECRET_KEY = get_secret("DJANGO_SECRET_KEY")
    DATABASE_USER = get_secret("DATABASE_USER")
    DATABASE_PASSWORD = get_secret("DATABASE_PASSWORD")
    NOTIFY_SERVICE_ENABLED = True
    NOTIFY_SERVICE_API_KEY = get_secret("NOTIFY_SERVICE_API_KEY")

    # Change default cache
    REDIS_HOST = get_env("DJANGO_REDIS_HOST", required=True)
    REDIS_PORT = get_env("DJANGO_REDIS_PORT", default=6379, cast=int)

    # Settings for the S3 object store
    AWS_ACCESS_KEY_ID = get_secret("OBJECT_STORAGE_KEY_ID")
    AWS_SECRET_ACCESS_KEY = get_secret("OBJECT_STORAGE_SECRET_KEY")
    AWS_STORAGE_BUCKET_NAME = get_env("OBJECT_STORAGE_BUCKET_NAME", required=True)
    AWS_S3_CUSTOM_DOMAIN = get_env("OBJECT_STORAGE_DOMAIN_NAME", required=True)

    # ToDo: it's not clear whether any files uploaded to the server should be
    #       cached since it's likely that an admin would want the ability to
    #       make changes at any time and have users see them immediately.
    # AWS_S3_OBJECT_PARAMETERS = {
    #     "CacheControl": "max-age=%d" % values.IntegerValue(26*60*60),
    # }

    DEFAULT_FILE_STORAGE = "nsc.storage.MediaStorage"

    @property
    def CACHES(self):
        return {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1",
                "KEY_PREFIX": "{}_".format(self.PROJECT_ENVIRONMENT_SLUG),
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "PARSER_CLASS": "redis.connection.HiredisParser",
                    # See https://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
                    # 'IGNORE_EXCEPTIONS': True,
                },
            }
        }

    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

    # django-debug-toolbar will throw an ImproperlyConfigured exception if DEBUG is
    # ever turned on when run with a WSGI server
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    COMPRESS_OUTPUT_DIR = ""

    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.sendgrid.net"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = ""
    EMAIL_HOST_PASSWORD = ""
    DEFAULT_FROM_EMAIL = ""
    SERVER_EMAIL = ""


class Stage(Deployed):
    pass


class Prod(Deployed):
    DEBUG = False

    RAVEN_CONFIG = {"dsn": ""}


class Demo(Build):
    """
    Demo configuration for simplified OpenShift deployment

    Mirrors the Deployed configuration but without services external to OpenShift

    This should be removed once external services are available
    """

    # Redefine values which are not optional in a deployed environment
    ALLOWED_HOSTS = get_env("DJANGO_ALLOWED_HOSTS", cast=csv_to_list, required=True)

    # Some deployed settings are no longer env vars - collect from the secret store
    SECRET_KEY = get_secret("DJANGO_SECRET_KEY")
    DATABASE_USER = get_secret("DATABASE_USER")
    DATABASE_PASSWORD = get_secret("DATABASE_PASSWORD")
    NOTIFY_SERVICE_ENABLED = True
    NOTIFY_SERVICE_API_KEY = get_secret("NOTIFY_SERVICE_API_KEY")

    # Change default cache
    REDIS_HOST = get_env("DJANGO_REDIS_HOST", required=True)
    REDIS_PORT = get_env("DJANGO_REDIS_PORT", default=6379, cast=int)

    @property
    def CACHES(self):
        return {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1",
                "KEY_PREFIX": "{}_".format(self.PROJECT_ENVIRONMENT_SLUG),
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "PARSER_CLASS": "redis.connection.HiredisParser",
                    # See https://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
                    # 'IGNORE_EXCEPTIONS': True,
                },
            }
        }

    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

    # django-debug-toolbar will throw an ImproperlyConfigured exception if DEBUG is
    # ever turned on when run with a WSGI server
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    COMPRESS_OUTPUT_DIR = ""
