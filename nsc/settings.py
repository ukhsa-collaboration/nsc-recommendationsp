from pathlib import Path

from django.utils.translation import gettext_lazy as _

from configurations import Configuration, values

from .utils.configurations import PathConfiguration, PathValue


# Common settings
BASE_DIR = Path(__file__).absolute().parent.parent
PROJECT_NAME = "nsc"
CONFIGURATION = values.Value(environ_name="CONFIGURATION", environ_required=True)


class Common(Configuration):
    # Name of the configuration class in use
    PROJECT_ENVIRONMENT_SLUG = "{}_{}".format(PROJECT_NAME, CONFIGURATION.lower())

    # DJANGO_ADMINS="User One,user1@example.com;User Two,user2@example.com"
    ADMINS = values.SingleNestedTupleValue()

    MANAGERS = ADMINS

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = values.Value(PROJECT_NAME)

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    ALLOWED_HOSTS = values.ListValue(["*"])

    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "whitenoise.runserver_nostatic",
        "django.contrib.staticfiles",
        "raven.contrib.django.raven_compat",
        "debug_toolbar",
        "django_extensions",
        "clear_cache",
        "simple_history",
        "django_filters",
        "nsc.condition",
        "nsc.contact",
        "nsc.document",
        "nsc.organisation",
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
        "debug_toolbar.middleware.DebugToolbarMiddleware",
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
    # http://django-configurations.readthedocs.org/en/latest/values/#configurations.values.DatabaseURLValue
    DATABASES = values.DatabaseURLValue(
        f"postgres://{PROJECT_NAME}:{PROJECT_NAME}@localhost:5432/{PROJECT_NAME}"
    )

    # Cache
    # https://pypi.org/project/django-cache-url/
    CACHES = values.CacheURLValue(f"locmem://{PROJECT_NAME}")

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


class Webpack:
    """
    Use as mixin for Dev configuration
    """

    # If static content is being served through the webpack dev server.
    # Needs template context processor for template support.
    WEBPACK_DEV_HOST = values.Value("{host}")
    WEBPACK_DEV_PORT = values.IntegerValue(8080)
    WEBPACK_DEV_URL = values.Value(f"//{WEBPACK_DEV_HOST}:{WEBPACK_DEV_PORT}/static/")

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


class Test(Dev):
    """
    Default test settings
    """

    pass


class Deployed(PathConfiguration):
    """
    Settings which are for a non local deployment, served behind nginx.
    """

    SECRETS_DIR = values.Value(
        "/run/secrets", environ_name="SECRETS_DIR", environ_prefix=None
    )

    # Some values are not optional in a deployed environment
    ALLOWED_HOSTS = values.Value(environ_required=True)
    SECRET_KEY = PathValue(SECRETS_DIR, values.Value)
    DATABASES = PathValue(SECRETS_DIR, values.DatabaseURLValue)

    # Change default cache
    CACHES = PathValue(SECRETS_DIR, values.CacheURLValue)
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

    # django-debug-toolbar will throw an ImproperlyConfigured exception if DEBUG is
    # ever turned on when run with a WSGI server
    DEBUG_TOOLBAR_PATCH_SETTINGS = False

    # New paths
    PUBLIC_ROOT = BASE_DIR.parent / "public"
    STATIC_ROOT = PUBLIC_ROOT / "static"
    MEDIA_ROOT = PUBLIC_ROOT / "media"
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
