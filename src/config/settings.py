"""
Django settings pour le projet.
"""

from pathlib import Path
import environ
from src.config import __version__

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
# APPLICATIONS INSTALLÉES
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
    "treebeard",  # Pour la gestion d'arbres hiérarchiques (django-treebeard)
    "parler",     # Pour la gestion des traductions (django-parler)
]

LOCAL_APPS = [
    "src.core.apps.CoreConfig",
    "src.access.apps.AccessConfig",
    "src.scope.apps.ScopeConfig",
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
    "src.core.middleware.RegionalLocaleMiddleware",
    'src.core.middleware.AuditUserMiddleware',
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    "src.scope.middleware.CompanyContextMiddleware",
]

ROOT_URLCONF = "src.config.urls"

# --------------------------------------------------------------------------------
# GABARITS (TEMPLATES)
# --------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "src" / "core" / "templates"],
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

LOGIN_URL           = "users:login"  # L'URL vers laquelle Django redirigera les utilisateurs non connectés
LOGIN_REDIRECT_URL  = "home"  # L'URL où l'utilisateur est envoyé après s'être connecté avec succès
LOGOUT_REDIRECT_URL = "users:login"  # L'URL où l'utilisateur est envoyé après s'être déconnecté

# --------------------------------------------------------------------------------
# INTERNATIONALISATION & CODES RÉGIONAUX (i18n / l10n)
# https://docs.djangoproject.com/en/6.0/topics/i18n/
# --------------------------------------------------------------------------------
LANGUAGE_CODE = env("DEFAULT_LANG")  # Définit la langue par défaut si aucune n'est détectée
USE_I18N = True
USE_TZ = True
TIME_ZONE = env("TIME_ZONE") # Format dans lequel les dates sont stockées brutes en base de données

LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
]

# Variantes régionales supportées par des fichiers .po/.mo
# Lors d'ajout: mettre aussi à jour src/users/choices.py -> PreferredLanguageChoices
LANGUAGES_REGIONAL = [
    'fr-ca',
    'fr-fr',
    'en-ca',
    'en-us'
]

# Variantes activées si on a une variante régionale
LANGUAGES_FALLBACKS = {
    'fr': 'fr-ca',
    'en': 'en-ca',
}

# PARLER_LANGUAGES = {
#     1: (
#         {'code': 'fr'},
#         {'code': 'en'},
#         {'code': 'fr-ca'},
#         {'code': 'fr-fr'},
#         {'code': 'en-ca'},
#         {'code': 'en-us'},
#     ),
#     'default': {
#         # Système de repli en cascade
#         'fallbacks': {
#             'fr-ca': ['fr'],
#             'fr-fr': ['fr'],
#             'en-ca': ['en'],
#             'en-us': ['en'],
#             'default': ['fr'], # Repli ultime si rien n'est trouvé
#         },
#         'hide_untranslated': False, # Évite de retourner une erreur si msg non traduit
#     }
# }

# Une seule langue est active pour les données dynamiques pour le moment
PARLER_LANGUAGES = {
    1: (
        {'code': env("DEFAULT_LANG")},
    ),
    'default': {
        'fallbacks': [env("DEFAULT_LANG")],
        'hide_untranslated': False,
    }
}


# Dossier où seront stockés les fichiers de traduction (.po/.mo)
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# --------------------------------------------------------------------------------
# FICHIERS STATIQUES ET MÉDIAS
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
PROJECT_VERSION = __version__
