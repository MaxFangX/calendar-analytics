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

ENVIRONMENT = os.getenv('APP_ENVIRONMENT', 'dev')
if ENVIRONMENT == 'prod':
    PRODUCTION= True  # Defined for convenience
else:
    PRODUCTION = False  # Defined for convenience

# Configured prod/non-prod settings

if PRODUCTION:
    BASE_URL = 'calendarapptest.herokuapp.com'
    DEBUG = False
    VERBOSE_PRINT = False
    TEMPLATE_DEBUG = False
else:
    BASE_URL = 'calendarapptest.herokuapp.com'
    DEBUG = True
    VERBOSE_PRINT = True
    TEMPLATE_DEBUG = True

# Environment variables
SECRET_KEY = os.environ.get('CJ_DJANGO_SECRET_KEY', "fake_key")
if ENVIRONMENT == 'prod':
    assert SECRET_KEY != "fake_key", "SECRET_KEY environment variable must be set"

GOOGLE_CALENDAR_API_CLIENT_ID = os.getenv('CJ_GOOGLE_CALENDAR_API_CLIENT_ID', None)
GOOGLE_CALENDAR_API_CLIENT_SECRET = os.getenv('CJ_GOOGLE_CALENDAR_API_CLIENT_SECRET', None)
assert GOOGLE_CALENDAR_API_CLIENT_ID, "GOOGLE_CALENDAR_API_CLIENT_ID environment variable must be set"
assert GOOGLE_CALENDAR_API_CLIENT_SECRET, "GOOGLE_CALENDAR_API_CLIENT_SECRET environment variable must be set"

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'ngrok.io', 'calendarapptest.heroku.com']

AUTHENTICATION_BACKENDS = (
    # Python social auth
    'social.backends.google.GoogleOAuth2',
    'social.backends.google.GooglePlusAuth',

    'django.contrib.auth.backends.ModelBackend',
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    # CalendarJournal App(s)
    'cal',
    'api',

    # Vendor App(s)
    'rest_framework',
    'social.apps.django_app.default',
    'loginas',
    'djangobower',
)

BOWER_INSTALLED_APPS = (
    'angular',
    'moment-timezone',
    'angular-nvd3',
    'fullcalendar',
)

# TODO make an actual login page for redirection
LOGIN_URL = "/"

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
    'whitenoise.middleware.WhiteNoiseMiddleware',
)
# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticatedOrReadOnly',),
    'PAGE_SIZE': 200,
}


ROOT_URLCONF = 'cal.urls'

# Python Social Auth
SOCIAL_AUTH_UUID_LENGTH = 3
SOCIAL_AUTH_RAISE_EXCEPTIONS = True

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = GOOGLE_CALENDAR_API_CLIENT_ID
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = GOOGLE_CALENDAR_API_CLIENT_SECRET
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['https://www.googleapis.com/auth/plus.login',
                                   'https://www.googleapis.com/auth/plus.me',
                                   'profile', 'email', 'https://www.googleapis.com/auth/calendar']

SOCIAL_AUTH_GOOGLE_PLUS_KEY = GOOGLE_CALENDAR_API_CLIENT_ID
SOCIAL_AUTH_GOOGLE_PLUS_SECRET = GOOGLE_CALENDAR_API_CLIENT_ID

# TODO disambiguate between these two
SOCIAL_AUTH_GOOGLE_AUTH_EXTRA_ARGUMENTS = {'access_type': 'offline'}
SOCIAL_AUTH_GOOGLE_REQUEST_TOKEN_EXTRA_ARGUMENTS = {'access_type': 'offline'}

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',

    # Custom processors
    'cal.context_processors.calendar_analytics_processor',

    # Vendor processors
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',  # TODO ensure this is used

]

WSGI_APPLICATION = 'cal.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

if 'RDS_DB_NAME' in os.environ:
    # These environment variables are automagically set in prod
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'dfe0rrmd4ldfa1',
            'USER': 'yacnjuojlushro',
            'PASSWORD': 'c18e92383803272e63b9ec80f9ded9f690c4f314dadecdf3ae7ea03fc0863f1b',
            'HOST': 'ec2-54-243-185-99.compute-1.amazonaws.com',
            'PORT': 5432,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'dfe0rrmd4ldfa1',
            'USER': 'yacnjuojlushro',
            'PASSWORD': 'c18e92383803272e63b9ec80f9ded9f690c4f314dadecdf3ae7ea03fc0863f1b',
            'HOST': 'ec2-54-243-185-99.compute-1.amazonaws.com',
            'PORT': 5432,
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

if ENVIRONMENT == 'prod':
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATIC_URL = '/static/'
    BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, "cal", "static/")
    # STATIC_ROOT = os.path.join(BASE_DIR, "static/")
    # STATIC_URL = '/static/'
    # BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, "cal", "static/")
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
    STATIC_URL = '/static/'
    STATICFILES_DIRS = (
        os.path.join(PROJECT_ROOT, 'static'),
    )
    BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, "..", "www", "cal", "static/")
    BOWER_PATH = '/usr/local/bin/bower'
    BOWER_PATH = '/app/node_modules/bower/bin/bower'

STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'djangobower.finders.BowerFinder',
        ]
