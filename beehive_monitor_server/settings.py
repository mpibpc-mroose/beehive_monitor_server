import os
import json
import logging
import logging.config
import os
from types import SimpleNamespace as Namespace

from django.utils.log import DEFAULT_LOGGING

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

secrets = json.load(
    open(
        os.path.join(
            BASE_DIR,
            "beehive_monitor_server",
            "secrets.json"
        ), "r"
    ),
    object_hook=lambda d: Namespace(**d)
)

logger = logging.getLogger(__name__)

SECRET_KEY = secrets.SECRET_KEY
DEBUG = False

ALLOWED_HOSTS = ["waage.roose-in-berge.de", "localhost", "127.0.0.1"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # packages
    'raven.contrib.django.raven_compat',
    'django_admin_lightweight_date_hierarchy',
    # project
    "DataCollector",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'beehive_monitor_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(
                BASE_DIR, "templates"
            )
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

WSGI_APPLICATION = 'beehive_monitor_server.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': secrets.db_name,
        'USER': secrets.db_user,
        'PASSWORD': secrets.db_password,
        'HOST': secrets.db_host,
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = False
USE_L10N = False
USE_TZ = False

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(
        BASE_DIR,
        "static"
    )
]
STATIC_ROOT = os.path.join(BASE_DIR, 'static_collect')

# EMAIL
EMAIL_HOST = secrets.EMAIL_HOST
EMAIL_HOST_PASSWORD = secrets.EMAIL_HOST_PASSWORD
EMAIL_HOST_USER = secrets.EMAIL_HOST_USER
EMAIL_PORT = secrets.EMAIL_PORT

RAVEN_CONFIG = {
    'dsn': 'https://2dd7f6d0d01b47ff944ad0b3713d978d:9bfa96758856495e859c99a3bb512035@sentry.io/264359',
    'release': "0.0",
}


LOGGING_CONFIG = None
LOGLEVEL = os.environ.get('LOGLEVEL', 'info').upper()

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },
    'loggers': {
        '': {
            'level': 'WARNING',
            'handlers': ['console', 'sentry'],
        },
        'beehive_monitor_server': {
            'level': LOGLEVEL,
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        # Prevent noisy modules from logging to Sentry
        #'noisy_module': {
        #    'level': 'ERROR',
        #    'handlers': ['console'],
        #    'propagate': False,
        #},
        # Default runserver request logging
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
    },
})

LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/admin/login/"

OPEN_WEATHER_MAPS_API_KEY = secrets.OPEN_WEATHER_MAPS_API_KEY

try:
    from beehive_monitor_server.local_settings import *
except ImportError:
    logger.info("No local settings supplied")
