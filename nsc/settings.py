import os
from os import environ
from pathlib import Path

from django.utils.translation import gettext_lazy as _

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

import envdir
from celery.schedules import crontab
from configurations import Configuration


# Common settings
BASE_DIR = Path(__file__).absolute().parent.parent
PROJECT_NAME = "nsc"
CONFIGURATION = environ["DJANGO_CONFIGURATION"]
CONFIG_DIR = environ.get("DJANGO_CONFIG_DIR")
SECRET_DIR = environ.get("DJANGO_SECRET_DIR")


if CONFIG_DIR:
    envdir.Env(CONFIG_DIR)


class NotSetClass:
    def __bool__(self):
        return False


NotSet = NotSetClass()


def get_env(name, default=NotSet, required=False, cast=str):
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

        if value is None and default is not NotSet:
            return default

        if value is None and required:
            raise ValueError(f"{name} not found in env")

        return cast(value)

    return property(_lookup)


def get_secret(*name, default=NotSet, required=True, cast=str):
    """
    Get a secret from disk

    Secrets should be available as the content of `<SECRET_DIR>/<name>`

    All secrets are required

    Arguments:

        name (str[]): Path to the secret variable
        default (any): The value to use if not set
        required (bool): Should an error be raised if the value is missing
        cast (Callable): function to call on extracted string value
    """

    # We don't want this to be called unless we're in a configuration which uses it
    def _lookup(self):
        if not SECRET_DIR:
            if required:
                raise ValueError(
                    f"Secret {name} not found: DJANGO_SECRET_DIR not set in env"
                )
            else:
                return default

        file = Path(SECRET_DIR, *name)
        if not file.exists():
            if required:
                raise ValueError(f"Secret {file} not found")
            else:
                return default

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
        "django_auth_adfs",
        "whitenoise.runserver_nostatic",
        "django.contrib.staticfiles",
        "django_extensions",
        "clear_cache",
        "simple_history",
        "storages",
        "django_filters",
        "nsc.user",
        "nsc.condition",
        "nsc.contact",
        "nsc.document",
        "nsc.stakeholder",
        "nsc.policy",
        "nsc.review",
        "nsc.notify",
        "nsc.utils",
        "nsc.subscription",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.cache.UpdateCacheMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.cache.FetchFromCacheMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "simple_history.middleware.HistoryRequestMiddleware",
        "nsc.middleware.redirect_url_fragment",
        "nsc.user.middleware.record_user_session",
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

    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

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
        "disable_existing_loggers": False,
        "root": {"level": "WARNING", "handlers": ["console"]},
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

    # dont use the get_env function here as the property isn't read into the celery config correctly
    REDIS_HOST = environ.get("DJANGO_REDIS_HOST", "127.0.0.1")
    REDIS_PORT = int(environ.get("DJANGO_REDIS_PORT", 6379))

    # Settings for the GDS Notify service for sending emails.
    PHE_COMMUNICATIONS_EMAIL = get_env("PHE_COMMUNICATIONS_EMAIL", default=None)
    PHE_COMMUNICATIONS_NAME = get_env("PHE_COMMUNICATIONS_NAME", default=None)
    PHE_HELP_DESK_EMAIL = get_env("PHE_HELP_DESK_EMAIL", default=None)
    CONSULTATION_COMMENT_ADDRESS = get_env("CONSULTATION_COMMENT_ADDRESS", default=None)
    NOTIFY_SERVICE_ENABLED = bool(get_env("NOTIFY_SERVICE_ENABLE", default=0, cast=int))
    NOTIFY_SERVICE_API_KEY = get_secret(
        "notify", "api-key", required=False, default=None
    )
    NOTIFY_TEMPLATE_CONSULTATION_OPEN = get_env(
        "NOTIFY_TEMPLATE_CONSULTATION_OPEN", default=None
    )
    NOTIFY_TEMPLATE_CONSULTATION_OPEN_COMMS = get_env(
        "NOTIFY_TEMPLATE_CONSULTATION_OPEN_COMMS", default=None
    )
    NOTIFY_TEMPLATE_SUBSCRIBER_CONSULTATION_OPEN = get_env(
        "NOTIFY_TEMPLATE_SUBSCRIBER_CONSULTATION_OPEN", default=None
    )
    NOTIFY_TEMPLATE_DECISION_PUBLISHED = get_env("NOTIFY_TEMPLATE_DECISION_PUBLISHED")
    NOTIFY_TEMPLATE_SUBSCRIBER_DECISION_PUBLISHED = get_env(
        "NOTIFY_TEMPLATE_SUBSCRIBER_DECISION_PUBLISHED", default=None
    )
    NOTIFY_TEMPLATE_PUBLIC_COMMENT = get_env(
        "NOTIFY_TEMPLATE_PUBLIC_COMMENT", default=None
    )
    NOTIFY_TEMPLATE_STAKEHOLDER_COMMENT = get_env(
        "NOTIFY_TEMPLATE_STAKEHOLDER_COMMENT", default=None
    )
    NOTIFY_TEMPLATE_SUBSCRIBED = get_env("NOTIFY_TEMPLATE_SUBSCRIBED", default=None)
    NOTIFY_TEMPLATE_UPDATED_SUBSCRIPTION = get_env(
        "NOTIFY_TEMPLATE_UPDATED_SUBSCRIPTION", default=None
    )
    NOTIFY_TEMPLATE_UNSUBSCRIBE = get_env("NOTIFY_TEMPLATE_UNSUBSCRIBE", default=None)
    NOTIFY_TEMPLATE_HELP_DESK = get_env("NOTIFY_TEMPLATE_HELP_DESK", default=None)
    NOTIFY_TEMPLATE_HELP_DESK_CONFIRMATION = get_env(
        "NOTIFY_TEMPLATE_HELP_DESK_CONFIRMATION", default=None
    )
    NOTIFY_STALE_MINUTES = 5

    # Settings for celery
    CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERYD_WORKER_HIJACK_ROOT_LOGGER = False

    CELERY_BEAT_SCHEDULE = {
        "send-pending-emails": {
            "task": "nsc.notify.tasks.send_pending_emails",
            "schedule": crontab(minute="*"),
        },
        "update-stale-email-statuses": {
            "task": "nsc.notify.tasks.update_stale_email_statuses",
            "schedule": crontab(minute=f"*/{NOTIFY_STALE_MINUTES}"),
        },
        "send-open-review-notifications": {
            "task": "nsc.review.tasks.send_open_review_notifications",
            "schedule": crontab(minute="*"),
        },
        "send-published-notifications": {
            "task": "nsc.review.tasks.send_published_notifications",
            "schedule": crontab(minute="*"),
        },
    }

    # This is the URL for the National Screening Committee where members of
    # the public can leave feedback about the web site.
    PROJECT_FEEDBACK_URL = ""

    #
    # Authentication
    #
    AUTH_USE_ACTIVE_DIRECTORY = bool(int(environ.get("AUTH_USE_ACTIVE_DIRECTORY", 0)))
    ACTIVE_DIRECTORY_CLIENT_ID = get_secret(
        "azure-ad", "application-id", required=bool(AUTH_USE_ACTIVE_DIRECTORY)
    )
    ACTIVE_DIRECTORY_CLIENT_SECRET = get_secret(
        "azure-ad", "secret", required=bool(AUTH_USE_ACTIVE_DIRECTORY)
    )
    ACTIVE_DIRECTORY_TENANT_ID = get_secret(
        "azure-ad", "tenant-id", required=bool(AUTH_USE_ACTIVE_DIRECTORY)
    )
    LOGIN_REDIRECT_URL = "/"

    @property
    def AUTHENTICATION_BACKENDS(self):
        AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

        if self.AUTH_USE_ACTIVE_DIRECTORY:
            return AUTHENTICATION_BACKENDS + (
                "nsc.user.backend.UniqueSessionAdfsBackend",
            )

        return AUTHENTICATION_BACKENDS

    @property
    def LOGIN_URL(self):
        if self.AUTH_USE_ACTIVE_DIRECTORY:
            return "django_auth_adfs:login"
        else:
            return "/accounts/login/"

    @property
    def AUTH_ADFS(self):
        if not self.AUTH_USE_ACTIVE_DIRECTORY:
            return {
                "TENANT_ID": "fake-tenant",
                "CLIENT_ID": "fake-client",
                "RELYING_PARTY_ID": "fake-relying-party",
                "AUDIENCE": "fake-audience",
            }

        return {
            "AUDIENCE": self.ACTIVE_DIRECTORY_CLIENT_ID,
            "CLIENT_ID": self.ACTIVE_DIRECTORY_CLIENT_ID,
            "CLIENT_SECRET": self.ACTIVE_DIRECTORY_CLIENT_SECRET,
            "CLAIM_MAPPING": {"email": "email"},
            "USERNAME_CLAIM": "name",
            "GROUPS_CLAIM": "roles",
            "GROUP_TO_FLAG_MAPPING": {"is_staff": "admin", "is_superuser": "admin"},
            "MIRROR_GROUPS": False,
            "TENANT_ID": self.ACTIVE_DIRECTORY_TENANT_ID,
            "RELYING_PARTY_ID": self.ACTIVE_DIRECTORY_CLIENT_ID,
        }

    AUTH_USER_MODEL = "user.User"


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
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = get_env("DJANGO_SECRET_KEY", default=PROJECT_NAME)

    DEBUG = True
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = "/tmp/app-emails"
    INTERNAL_IPS = ["127.0.0.1"]

    MAIN_DOMAIN = "localhost:8000"

    @property
    def EMAIL_ROOT_DOMAIN(self):
        return f"http://{self.MAIN_DOMAIN}"

    # Settings for the GDS Notify service for sending emails.
    PHE_COMMUNICATIONS_EMAIL = "phecomms@example.com"
    PHE_COMMUNICATIONS_NAME = "PHE Comms"
    PHE_HELP_DESK_EMAIL = "phehelpdesk@example.com"
    CONSULTATION_COMMENT_ADDRESS = "phecomments@example.com"
    NOTIFY_SERVICE_ENABLED = False
    NOTIFY_SERVICE_API_KEY = None
    NOTIFY_TEMPLATE_CONSULTATION_OPEN = "consultation-open-templates"
    NOTIFY_TEMPLATE_CONSULTATION_OPEN_COMMS = "comms-consultation-open-templates"
    NOTIFY_TEMPLATE_SUBSCRIBER_CONSULTATION_OPEN = (
        "subscriber-consultation-open-template"
    )
    NOTIFY_TEMPLATE_DECISION_PUBLISHED = "decision-published-template"
    NOTIFY_TEMPLATE_SUBSCRIBER_DECISION_PUBLISHED = (
        "subscriber-decision-published-template"
    )
    NOTIFY_TEMPLATE_PUBLIC_COMMENT = "public-comment-template"
    NOTIFY_TEMPLATE_STAKEHOLDER_COMMENT = "stakeholder-comment-template"
    NOTIFY_TEMPLATE_SUBSCRIBED = "subscribed-template"
    NOTIFY_TEMPLATE_UPDATED_SUBSCRIPTION = "updated-subscription-template"
    NOTIFY_TEMPLATE_UNSUBSCRIBE = "unsubscribed-template"
    NOTIFY_TEMPLATE_HELP_DESK = "help-desk-template"
    NOTIFY_TEMPLATE_HELP_DESK_CONFIRMATION = "help-desk-confirmation-template"

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


class Build(Common):
    """
    Settings for use when building containers for deployment
    """

    # Fake secret key so that collect static can be ran
    SECRET_KEY = "not a real secret key"

    # New paths
    PUBLIC_ROOT = BASE_DIR.parent / "public"
    STATIC_ROOT = PUBLIC_ROOT / "static"
    MEDIA_ROOT = PUBLIC_ROOT / "media"


class Deployed(Build):
    """
    Settings which are for a non-local deployment
    """

    DEBUG = False

    #  X-Content-Type-Options: nosniff
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # X-XSS-Protection: 1; mode=block
    SECURE_BROWSER_XSS_FILTER = True

    # Secure session cookie
    SESSION_COOKIE_SECURE = True

    # Prevent client-side JS from accessing the session cookie.
    SESSION_COOKIE_HTTPONLY = True

    # Sets the maximum age of a session (4 hours in seconds)
    SESSION_COOKIE_AGE = 4 * 60 * 60

    # Add preload directive to the Strict-Transport-Security header
    SECURE_HSTS_PRELOAD = True

    # Secure CSRF cookie
    CSRF_COOKIE_SECURE = True

    # Disallow iframes from any origin.
    X_FRAME_OPTIONS = "DENY"

    # Set Referrer Policy header on all responses.
    # Django 3.0 only.
    SECURE_REFERRER_POLICY = "same-origin"

    # Sets HTTP Strict Transport Security header on all responses.
    SECURE_HSTS_SECONDS = 3600  # Seconds

    # Sets up treating connections from the load balancer as secure
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Some deployed settings are no longer env vars - collect from the secret store
    SECRET_KEY = get_secret("django", "secret-key")
    DATABASE_USER = get_secret("postgresql", "database-user")
    DATABASE_PASSWORD = get_secret("postgresql", "database-password")
    DATABASE_NAME = get_secret("postgresql", "database-name")

    # Change default cache
    REDIS_HOST = get_env("REDIS_SERVICE_HOST", required=True)

    # Settings for the S3 object store
    AWS_QUERYSTRING_AUTH = False
    AWS_BUCKET_DOMAIN = get_secret("s3", "endpoint")
    AWS_ACCESS_KEY_ID = get_secret("s3", "access-key")
    AWS_SECRET_ACCESS_KEY = get_secret("s3", "secret-key")
    AWS_STORAGE_BUCKET_NAME = get_secret("s3", "bucket-name")
    MEDIA_HOST_DOMAIN = get_env("MEDIA_HOST_DOMAIN")

    @property
    def AWS_S3_ENDPOINT_URL(self):
        return f"http://{self.AWS_BUCKET_DOMAIN}"

    @property
    def MEDIA_URL(self):
        return f"https://{self.MEDIA_HOST_DOMAIN}/"

    @property
    def AWS_S3_CUSTOM_DOMAIN(self):
        return self.MEDIA_HOST_DOMAIN

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
                },
            },
            "session": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/2",
                "KEY_PREFIX": "{}_".format(self.PROJECT_ENVIRONMENT_SLUG),
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "PARSER_CLASS": "redis.connection.HiredisParser",
                },
            },
        }

    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "session"

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

    # host settings
    MAIN_DOMAIN = get_env("MAIN_DOMAIN", required=True)
    EXTRA_ALLOWED_HOSTS = get_env("EXTRA_ALLOWED_HOSTS", default=[], cast=csv_to_list)

    @property
    def ALLOWED_HOSTS(self):
        return [self.MAIN_DOMAIN, *self.EXTRA_ALLOWED_HOSTS]

    @property
    def EMAIL_ROOT_DOMAIN(self):
        return f"https://{self.MAIN_DOMAIN}"

    # sentry settings
    SENTRY_DSN = get_secret("sentry", "dsn")

    @classmethod
    def pre_setup(cls):
        SENTRY_DSN = os.environ.get("SENTRY_DSN", None)
        if SENTRY_DSN:
            sentry_sdk.init(
                dsn=SENTRY_DSN,
                integrations=[
                    DjangoIntegration(),
                    CeleryIntegration(),
                    RedisIntegration(),
                ],
                environment=cls.__name__,
                send_default_pii=False,
            )


class Stage(Deployed):
    pass


class Prod(Deployed):
    pass


class Demo(Build):
    """
    Demo configuration for simplified OpenShift deployment

    Mirrors the Deployed configuration but without services external to OpenShift

    This should be removed once external services are available
    """

    DEBUG = False

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

    COMPRESS_OUTPUT_DIR = ""
