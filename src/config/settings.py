"""
Django settings for django-stock project.
Optimized for scalability and maintenance.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.0/ref/settings/
"""

from pathlib import Path
from django.utils.translation import gettext_lazy as _

import environ

# --------------------------------------------------------------------------------
# CHEMINS DE BASE (Calculé par rapport à la racine où se trouve manage.py)
# --------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --------------------------------------------------------------------------------
# CONFIGURATION DE L'ENVIRONNEMENT (django-environ)
# --------------------------------------------------------------------------------
env = environ.Env(DEBUG=(bool, False), TIME_ZONE=(str, "UTC"))
environ.Env.read_env(BASE_DIR / ".env")

# --------------------------------------------------------------------------------
# SÉCURITÉ
# --------------------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = ["stock", "127.0.0.1", "localhost", "0.0.0.0"]

# --------------------------------------------------------------------------------
# APPLICATIONS INSTALL?ES
# --------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_browser_reload",
]

LOCAL_APPS = [
    "src.core.apps.CoreConfig",
    "src.users.apps.UsersConfig",
    "src.company.apps.CompanyConfig",
    "src.catalogue.apps.CatalogueConfig",
    "src.inventory.apps.InventoryConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# --------------------------------------------------------------------------------
# MIDDLEWARES
# --------------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "src.config.urls"

# --------------------------------------------------------------------------------
# GABARITS (TEMPLATES)
# --------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / "src" / "core" / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",

                "src.core.context_processors.project_context",
            ],
        },
    },
]

WSGI_APPLICATION = "src.config.wsgi.application"
ASGI_APPLICATION = "src.config.asgi.application"

# --------------------------------------------------------------------------------
# BASE DE DONNÉES
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases
# --------------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

# --------------------------------------------------------------------------------
# AUTHENTIFICATION & UTILISATEURS
# --------------------------------------------------------------------------------
# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "users.User"

LOGIN_URL           = ( "users:login" )   # L'URL vers laquelle Django redirigera les utilisateurs non connectés
LOGIN_REDIRECT_URL  = ( "home" )          # L'URL où l'utilisateur est envoyé après s'être connecté avec succès
LOGOUT_REDIRECT_URL = ( "users:login" )   # L'URL où l'utilisateur est envoyé après s'être déconnecté

# --------------------------------------------------------------------------------
# INTERNATIONALISATION & CODES RÉGIONAUX (i18n / l10n)
# https://docs.djangoproject.com/en/6.0/topics/i18n/
# --------------------------------------------------------------------------------
LANGUAGE_CODE = env("DEFAULT_LANG")  # Apps default language
USE_I18N = True
USE_TZ = True
TIME_ZONE = env("TIME_ZONE")

LANGUAGES = [
    ("en", _("English")),
    ("fr", _("French")),
    ("es", _("Spanish")),
]

# Dossier où seront stockés les fichiers de traduction (.po/.mo)
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# --------------------------------------------------------------------------------
# FICHIERS STATIQUES ET MÉDIAS
# https://docs.djangoproject.com/en/6.0/howto/static-files/
# --------------------------------------------------------------------------------
STATIC_URL = "assets/"

STATICFILES_DIRS = [
    BASE_DIR / "assets",
]

# Fichiers téléversés par l'utilisateur via l'UI (images de produit)
MEDIA_URL = "medias/"
MEDIA_ROOT = BASE_DIR / "medias"

# --------------------------------------------------------------------------------
# CONSTANTES DU PROJET
# --------------------------------------------------------------------------------
PROJECT_AUTHOR = "Caroline Guénette"