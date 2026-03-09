# Django settings for pythonfiddle project.
import os
from pathlib import Path

PROJECT_DIR = os.path.dirname(__file__)
BASE_DIR = Path(__file__).resolve().parent

DEBUG = True

ADMINS = [
    # ('Your Name', 'your_email@example.com'),
]

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'fiddle.sqlite3',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

LANGUAGES = (
    ('en', 'English'),
    ('zh', 'Chinese'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(os.path.dirname(PROJECT_DIR), "fiddlesalad", "static")

PYTHON_LIB_DIR = os.path.join(PROJECT_DIR, "static", "lib")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = 'http://127.0.0.1:8000/static/'

AWS_ACCESS_KEY_ID = 's3_key'

AWS_SECRET_ACCESS_KEY = 's3_secret'

AWS_STORAGE_BUCKET_NAME = 'bucket_name'

# django-storages S3 configuration (replaces django-mediasync)
STORAGES = {
    'staticfiles': {
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
    },
}
AWS_S3_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
AWS_S3_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME

build_config = False

from pythonfiddle.files import *

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'o#&0=io58r!=dhaf(gx@a5$n#2zy!b$k=yhu&^@uq^7=$v%&k('

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(os.path.dirname(PROJECT_DIR), 'templates'),
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
                'cloud_ide.context_processors.debug',
                'cloud_ide.context_processors.media',
                'pythonfiddle.context_processors.site',
            ],
        },
    },
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'pythonfiddle.urls'

LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, "locale"),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.flatpages',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.redirects',
    'storages',
    'taggit',
    'social_django',
    'cloud_ide.fiddle',
]

AUTHENTICATION_BACKENDS = [
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/done/'

# python-social-auth settings (replaces django-social-auth)
SOCIAL_AUTH_TWITTER_KEY               = '65tXXWpGJ0PfsZzN1xR7Q'
SOCIAL_AUTH_TWITTER_SECRET            = 'KZa2FPOjIByvdFqcHGTQNi01VouoTiqeAaZ8yelTh0'
SOCIAL_AUTH_FACEBOOK_KEY              = '244638052233650'
SOCIAL_AUTH_FACEBOOK_SECRET           = '66c1d60fe6f777dc52c2c3eef5752fbf'
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY         = '823652973862.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET      = 'yQ4l2KebfymlugAnTgS6l2ID'
SOCIAL_AUTH_CREATE_USERS              = True
SOCIAL_AUTH_DEFAULT_USERNAME          = 'socialauth_user'
LOGIN_ERROR_URL                       = '/login/error/'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
