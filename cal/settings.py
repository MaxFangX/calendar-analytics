"""
Django settings for the Calendar Journal project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('CJ_DJANGO_SECRET_KEY', None)

ENVIRONMENT = os.getenv('APP_ENVIRONMENT', 'dev')

if ENVIRONMENT == 'prod':
    BASE_URL = '104.131.153.171:8000'
else:
    DEBUG = True
    TEMPLATE_DEBUG = True
    BASE_URL = 'localhost:8000'

# Variables
GOOGLE_CALENDAR_API_CLIENT_ID = os.getenv('CJ_GOOGLE_CALENDAR_API_CLIENT_ID')
GOOGLE_CALENDAR_API_CLIENT_SECRET = os.getenv('CJ_GOOGLE_CALENDAR_API_CLIENT_SECRET')

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGE_SIZE': 10,
}

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # CalendarJournal App(s)
    'cal',

    # Vendor App(s)
    'rest_framework'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Custom middleware
    'cal.middleware.UserBasedExceptionMiddleware',
)

ROOT_URLCONF = 'cal.urls'

WSGI_APPLICATION = 'cal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

# Production settings
if ENVIRONMENT == 'prod':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('CJ_DB_NAME'),
        'USER': os.getenv('CJ_DB_USER'),
        'PASSWORD': os.getenv('CJ_DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',
    }
