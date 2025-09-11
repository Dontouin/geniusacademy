"""
Django settings for config project.

Optimisé pour Genius Academy : 100% Jazzmin + multilingue + PWA.
"""

import os
from decouple import config
import dj_database_url
from django.utils.translation import gettext_lazy as _

# -------------------------
# Build paths
# -------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -------------------------
# Security
# -------------------------
SECRET_KEY = config("SECRET_KEY", default="django-insecure-default-key-for-dev")
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = [
    "*",
    "127.0.0.1",
    "localhost",
]

# -------------------------
# Custom user model
# -------------------------
AUTH_USER_MODEL = "accounts.User"

# -------------------------
# Installed apps
# -------------------------
DJANGO_APPS = [
    "modeltranslation",  # multilingue
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "jazzmin",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_filters",
    "widget_tweaks",
    "pwa",  # <- Ajout pour PWA
]

PROJECT_APPS = [
    "core.apps.CoreConfig",
    "accounts.apps.AccountsConfig",
    "search.apps.SearchConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

# -------------------------
# Middleware
# -------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # multilingue
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -------------------------
# URL & WSGI
# -------------------------
ROOT_URLCONF = "config.urls"

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

# -------------------------
# Database
# -------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
# Alternative PostgreSQL (Render par ex.)
# DATABASES = {
#     "default": dj_database_url.parse(config("DATABASE_URL"))
# }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------
# Password validators
# -------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------
# Internationalization & Languages
# -------------------------
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Douala"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("fr", _("Français")),
    ("en", _("English")),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

# -------------------------
# Static & Media
# -------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# WhiteNoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------
# Email
# -------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# Pour production, configure SMTP via env (ex: Gmail, SendGrid, Mailgun...)

# -------------------------
# Crispy Forms
# -------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# -------------------------
# Auth Redirects
# -------------------------
LOGIN_URL = "/accounts/login/"
LOGOUT_REDIRECT_URL = "/"

# -------------------------
# Jazzmin Customisation
# -------------------------
JAZZMIN_SETTINGS = {
    "site_title": "GENIUS ACADEMY ADMIN",
    "site_header": "Genius Academy",
    "site_brand": "Genius Academy",
    "welcome_sign": "Bienvenue dans l'administration de Genius Academy",
    "show_sidebar": True,
    "navigation_expanded": True,
    "copyright": "The Genius Academy © 2025",
    "search_model": "accounts.user",
    "user_avatar": "accounts.User.picture",
    "topmenu_links": [
        {"name": "Accueil", "url": "/", "permissions": ["auth.view_user"]},
        {"name": "Site", "url": "/admin/", "new_window": True},
        {"model": "accounts.user"},
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "accounts.user": "fas fa-user-graduate",
        "accounts.student": "fas fa-user",
        "accounts.teacher": "fas fa-chalkboard-teacher",
        "core.newsandevents": "fas fa-newspaper",
        "core.testimonial": "fas fa-comment-dots",
    },
    "related_modal_active": True,
    "show_ui_builder": True,
}

# -------------------------
# Jazzmin Theme (couleurs)
# -------------------------
JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "dark_mode_theme": "darkly",
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "purple",
    "accent": "purple",
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success",
    },
}

# -------------------------
# Progressive Web App (PWA)
# -------------------------
PWA_APP_NAME = "Genius Academy"
PWA_APP_DESCRIPTION = "Application web progressive de Genius Academy"
PWA_APP_THEME_COLOR = "#0a0a14"
PWA_APP_BACKGROUND_COLOR = "#ffffff"
PWA_APP_DISPLAY = "standalone"
PWA_APP_SCOPE = "/"
PWA_APP_ORIENTATION = "any"
PWA_APP_START_URL = "/"
PWA_APP_ICONS = [
    {
        "src": "/static/images/icons/icon-512x512.png",
        "sizes": "512x512"
    }
]
PWA_APP_ICONS_APPLE = [
    {
        "src": "/static/images/icons/icon-512x512.png",
        "sizes": "512x512"
    }
]
PWA_APP_SPLASH_SCREEN = [
    {
        "src": "/static/images/icons/splash-640x1136.png",
        "media": "(device-width: 320px) and (device-height: 568px)"
    }
]
PWA_APP_DIR = "ltr"
PWA_APP_LANG = "fr-FR"

# -------------------------
# Logging
# -------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"level": "DEBUG", "class": "logging.StreamHandler"},
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}
