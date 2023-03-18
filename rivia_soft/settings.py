"""
Django settings for rivia_soft project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
from companies.url_variables import URL_NAMES_PREFIXED_WITH_APP_NAME
from socket import gethostname, gethostbyname
from json import loads

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# config file for production
CONFIG_FILE_NAME = 'config.json'
CONFIG_FILE_PATH = BASE_DIR / CONFIG_FILE_NAME # Server settings
# load configurations
with open(CONFIG_FILE_PATH, 'r') as CONFIG_FILE:
    CONFIG = loads(CONFIG_FILE.read())


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = CONFIG['DEBUG']

# SECURITY WARNING: keep the secret key used in production secret!
# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
if DEBUG:
    SECRET_KEY = 'wh*lo-yh6geec40s91k0wb!enwn5ov6)3^k53c1hq)pq6png4@'
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', gethostname(), gethostbyname(gethostname())]
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    SECRET_KEY = CONFIG['SECRET_KEY']
    ALLOWED_HOSTS = CONFIG['ALLOWED_HOSTS']
    DATABASES = CONFIG['DATABASES']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
    'rest_framework',

    # Project apps
    'error_handler',
    'users',
    # "user_logs",
    'companies',
    'accounts',
    'invoice',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'user_logs.middleware.UserLastSeenLoggerMiddleware',
    'invoice.middleware.SimpleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rivia_soft.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates'
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

WSGI_APPLICATION = 'rivia_soft.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
# TIME_ZONE = 'Asia/Dhaka'
# TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Expire user session when browser closes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Set session cookie max age to 5 hours
SESSION_COOKIE_AGE = 60*60*5

# Allow iframe to load from same origin
X_FRAME_OPTIONS = "SAMEORIGIN"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
# STATICFILES_DIRS = [
#     BASE_DIR / 'staticfiles'
# ]

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'
LOGIN_URL = 'users_login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'users_login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 1,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}
