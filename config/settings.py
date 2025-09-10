import os
from decouple import config
import dj_database_url
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy

# ================================
# Base
# ================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = config("SECRET_KEY", default="django-insecure-default-key-for-dev")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = ['geniusacademy5.onrender.com', '127.0.0.1']

# ================================
# Applications
# ================================
DJANGO_APPS = [
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "jazzmin",
    "jet",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_filters",
    "widget_tweaks",
]

PROJECT_APPS = [
    "core.apps.CoreConfig",
    "accounts.apps.AccountsConfig",
    "search.apps.SearchConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

# ================================
# Middleware
# ================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# ================================
# Templates
# ================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ================================
# Database
# ================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# Alternative PostgreSQL (décommente si besoin)
# DATABASES = {
#     'default': dj_database_url.parse(config('DATABASE_URL', default='postgresql://localhost/mydatabase'))
# }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ================================
# Auth
# ================================
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = reverse_lazy('login')
LOGOUT_REDIRECT_URL = reverse_lazy('home')

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

# ================================
# Internationalization
# ================================
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Douala"
USE_I18N = True
USE_TZ = True

# ================================
# Static & Media
# ================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ================================
# Email
# ================================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ================================
# Crispy Forms
# ================================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ================================
# Jazzmin
# ================================
JAZZMIN_SETTINGS = {
    "site_title": "GENIUS ACADEMY ADMIN",
    "site_header": "Genius Academy",
    "site_brand": "Genius Academy",
    "welcome_sign": "Bienvenue dans l'administration de Genius Academy",
    "show_sidebar": True,
    "navigation_expanded": True,
}

# ================================
# Logging
# ================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"level": "DEBUG", "class": "logging.StreamHandler",}},
    "root": {"level": "INFO", "handlers": ["console"]},
}
