from os import environ, getenv
from os.path import abspath, dirname, join
from sys import argv
from configurations import Configuration

from django.utils.translation import gettext_lazy as _

BASE_DIR = dirname(dirname(abspath(__file__)))
PROJECT_NAME = 'nsc'
PROJECT_ENVIRONMENT_SLUG = '{}_{}'.format(PROJECT_NAME, environ.get('DJANGO_CONFIGURATION').lower())

# Detect if we are running tests.  Is this really the best way?
IN_TESTS = 'test' in argv


class RedisCache(object):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://{}:{}/1'.format(getenv('REDIS_SERVICE_HOST', '127.0.0.1'), getenv('REDIS_SERVICE_PORT', 6379)),
            'KEY_PREFIX': '{}_'.format(PROJECT_ENVIRONMENT_SLUG),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'PARSER_CLASS': 'redis.connection.HiredisParser',
                # You may want this. See https://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
                # 'IGNORE_EXCEPTIONS': True, # see
            }
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'


class Common(Configuration):
    ADMINS = (
        ('Django Admin', 'richard@wildfish.com'),
    )

    MANAGERS = ADMINS

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = 'hqv8JcfTG6dkTTALY8MhaHTnKqSdhCG1CX8R4c8cc4nc0mUeCfnTiHobzlmGbcr5'

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    ALLOWED_HOSTS = []

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'whitenoise.runserver_nostatic',
        'django.contrib.staticfiles',
        'raven.contrib.django.raven_compat',
        'debug_toolbar',
        'bootstrap3',
        'django_extensions',
        'clear_cache',
        'simple_history',
        'django_filters',
        'nsc.condition',
        'nsc.policy',
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'simple_history.middleware.HistoryRequestMiddleware',
    ]

    ROOT_URLCONF = 'nsc.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                join(BASE_DIR, 'templates')
            ],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'nsc.wsgi.application'

    # Database
    # https://docs.djangoproject.com/en/1.11/ref/settings/#databases
    # http://django-configurations.readthedocs.org/en/latest/values/#configurations.values.DatabaseURLValue
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': join(BASE_DIR, 'db.sqlite3'),
        }
    }

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': getenv('DATABASE_NAME', PROJECT_NAME),
            'USER': getenv('DATABASE_USER', PROJECT_NAME),
            'PASSWORD': getenv('DATABASE_PASSWORD', PROJECT_NAME),
            'HOST': getenv('DATABASE_HOST', 'localhost'),
            'PORT': getenv('DATABASE_PORT', 5432),
        }
    }

    # Password validation
    # https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
    ]

    # Internationalization
    # https://docs.djangoproject.com/en/1.11/topics/i18n/
    LANGUAGE_CODE = 'en'

    LANGUAGES = [
        ('en', _('English'))
    ]

    TIME_ZONE = 'Europe/London'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.11/howto/static-files/
    STATIC_URL = '/static/'
    STATIC_ROOT = join(BASE_DIR, 'static_root')

    MEDIA_URL = '/media/'
    MEDIA_ROOT = join(BASE_DIR, 'media')

    # Additional locations of static files
    STATICFILES_DIRS = [
        join(BASE_DIR, 'static'),
        join(BASE_DIR, 'node_modules'),
    ]

    # STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    FIXTURE_DIRS = [
        join(BASE_DIR, 'fixtures')
    ]

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'django.server': {
                '()': 'django.utils.log.ServerFormatter',
                'format': '[%(server_time)s] %(message)s',
            }
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
            'django.server': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'django.server',
            },
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'django.server': {
                'handlers': ['django.server'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }

    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERYD_WORKER_HIJACK_ROOT_LOGGER = False


class Webpack:
    """
    Use as mixin for Dev configuration
    """
    # If static content is being served through the webpack dev server.
    # Needs template context processor for template support.
    WEBPACK_DEV_HOST = getenv('WEBPACK_DEV_HOST', 'localhost')
    WEBPACK_DEV_PORT = int(getenv('WEBPACK_DEV_PORT', '8080'))
    WEBPACK_DEV_URL = f'http://{WEBPACK_DEV_HOST}:{WEBPACK_DEV_PORT}/'

    @property
    def LOGGING(self):
        LOGGING = super().LOGGING
        LOGGING['loggers']['nsc.context_processors'] = {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        }
        return LOGGING

    @property
    def TEMPLATES(self):
        """
        Add a context processor to enable webpack dev server
        """
        TEMPLATES = super().TEMPLATES
        TEMPLATES[0]['OPTIONS']['context_processors'].append(
            'nsc.context_processors.webpack_dev_url',
        )
        return TEMPLATES


class Dev(Webpack, Common):
    DEBUG = True
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = '/tmp/app-emails'
    INTERNAL_IPS = ['127.0.0.1', ]
    ALLOWED_HOSTS = ['*']


class Deployed(RedisCache, Common):
    """
    Settings which are for a non local deployment, served behind nginx.
    """
    # django-debug-toolbar will throw an ImproperlyConfigured exception if DEBUG is
    # ever turned on when run with a WSGI server
    DEBUG_TOOLBAR_PATCH_SETTINGS = False

    PUBLIC_ROOT = join(BASE_DIR, '../public/')
    STATIC_ROOT = join(PUBLIC_ROOT, 'static')
    MEDIA_ROOT = join(PUBLIC_ROOT, 'media')
    COMPRESS_OUTPUT_DIR = ''

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    DEFAULT_FROM_EMAIL = ''
    SERVER_EMAIL = ''


class Stage(Deployed):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': getenv('POSTGRES_USER', ''),
            'USER': getenv('POSTGRES_USER', ''),
            'PASSWORD': getenv('POSTGRES_PASSWORD', 'password'),
            'HOST': getenv('POSTGRES_SERVICE_HOST', 'localhost'),
        }
    }


class Prod(Deployed):
    DEBUG = False

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': getenv('POSTGRES_USER', ''),
            'USER': getenv('POSTGRES_USER', ''),
            'PASSWORD': getenv('POSTGRES_PASSWORD', 'password'),
            'HOST': getenv('POSTGRES_SERVICE_HOST', 'localhost'),
        }
    }

    ALLOWED_HOSTS = ['.example.com', ]  # add deployment domain here

    RAVEN_CONFIG = {
        'dsn': ''
    }
