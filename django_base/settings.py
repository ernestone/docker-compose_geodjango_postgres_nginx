"""
Django settings for django_base project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.urls import reverse_lazy

from common_utils.utils_logging import create_file_handler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.getenv('DEBUG', 1)))
print(f"Debug = {DEBUG}")

ALLOWED_HOSTS = []
if ALLOWED_HOSTS_ENV := os.getenv('ALLOWED_HOSTS'):
    ALLOWED_HOSTS.extend({host.strip() for host in ALLOWED_HOSTS_ENV.split(',')})

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.postgres',
    'leaflet',
    'djgeojson',
    'simple_history',
    'rest_framework',
    'rest_framework_gis',
    'rest_framework.authtoken',
    'django_filters',
    'sample_app.apps.SampleAppConfig',
    'sample_admin_app.apps.SampleAdminConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware'
]

CORS_ORIGIN_ALLOW_ALL = DEBUG
if DEBUG:
    INSTALLED_APPS.append('corsheaders')
    MIDDLEWARE.append('corsheaders.middleware.CorsMiddleware')

ROOT_URLCONF = 'django_base.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'django_base.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
schemas = ['public']
add_schema = os.getenv('POSTGRES_SCHEMA')
if add_schema:
    schemas.insert(0, add_schema)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'OPTIONS': {
            'options': f'-c search_path={",".join(schemas)}'  # Schemas en los que aplicará por orden especificado
        },
        'NAME': os.getenv('POSTGRES_DBNAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASS'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': int(os.getenv('POSTGRES_PORT', 5432))
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/static/'
MEDIA_URL = '/static/media/'

STATIC_ROOT = '/vol/web/static'
MEDIA_ROOT = '/vol/web/media'

# Customization plugins
LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (41.33, 2.2),
    'DEFAULT_ZOOM': 9,
    'MAX_ZOOM': 20,
    'MIN_ZOOM': 3,
    'SCALE': 'both'
}

DATA_DIR_SAMPLE = os.getenv('DATA_DIR_SAMPLE', os.path.join(BASE_DIR, 'data', 'load_dir'))

# Params para Django session authentification
LOGIN_REDIRECT_URL = reverse_lazy('map') if DEBUG else reverse_lazy('')
LOGIN_URL = reverse_lazy('jwt_token_login')
LOGOUT_URL = reverse_lazy('logout')

# Extra setting para URL relativa para login externo por JWT Token
JWT_TOKEN_LOGIN_URL = os.getenv('JWT_TOKEN_LOGIN_URL', reverse_lazy('map') if DEBUG else reverse_lazy('admin/login'))

# Custom AUTH_USER (Recomendable siempre aunque no se modifique nada)
AUTH_USER_MODEL = 'sample_admin_app.UserSample'

# Settings mailing
if EMAIL_HOST := os.getenv('EMAIL_HOST'):
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'sample@nexusgeographics.com')
    EMAIL_PORT = os.getenv('EMAIL_PORT')
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'sample@nexusgeographics.com')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_mails')

# Fixture data (data que se cargará cada vez que se ejecute "python manage.py loaddata <fixture_nama>(OPC)"
FIXTURE_DIRS = [os.path.join(BASE_DIR, 'fixture_data')]

# Settings para rest-framework FILTERS
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ]
}

AUTH_ACTIVATED = bool(int(os.getenv('AUTH_ACTIVATED', '0')))
print(f"AUTH_ACTIVATED = {AUTH_ACTIVATED}")
if AUTH_ACTIVATED:
    # Settings para AUTH rest-framework
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
            'rest_framework_simplejwt.authentication.JWTAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ]
    REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
            'rest_framework.permissions.IsAuthenticated',
        ]

    # Settings para JWT_TOKEN
    from datetime import timedelta

    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('ACCESS_TOKEN_LIFETIME', 5))),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
        'ROTATE_REFRESH_TOKENS': False,
        'BLACKLIST_AFTER_ROTATION': True,

        'ALGORITHM': 'HS256',
        'SIGNING_KEY': SECRET_KEY,
        'VERIFYING_KEY': None,
        'AUDIENCE': None,
        'ISSUER': None,

        'AUTH_HEADER_TYPES': ('Token',),
        'USER_ID_FIELD': 'id',
        'USER_ID_CLAIM': 'user_id',

        'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
        'TOKEN_TYPE_CLAIM': 'token_type',

        'JTI_CLAIM': 'jti',

        'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
        'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
        'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    }

# Settings LOGGING
ADMINS = [(*adm.split(':'),)
          for adm in os.getenv('MAILS_ADMINS',
                               'Sample User: sample@mail.com').split(',')]

DEFAULT_EXCEPTION_REPORTER = 'sample_admin_app.log.CustomExceptionReporter'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        },
        'sample_report': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO' if not DEBUG else 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': not DEBUG, # Add attach con html como la pagina de DEBUG
        },
        'sample.logs': {
            '()': create_file_handler,
            'level': 'INFO',
            'filename': os.path.join(
                os.getenv('PYTHON_LOGS_DIR', os.path.join(BASE_DIR, 'data', 'logs')),
                'sample.log'),
            'formatter': 'sample_report',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'sample.errors': {
            'handlers': ['console', 'mail_admins'],
            'level': 'WARNING',
        },
        'sample.logs': {
            'level': 'INFO' if not DEBUG else 'DEBUG',
            'handlers': ['console', 'sample.logs']
        }
    }
}
