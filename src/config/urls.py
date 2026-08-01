"""
URL configuration for django-stock project.
Centralized router linking language prefixes and local applications.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from src.core.views import HomeView  # Import propre depuis le package de vues de core

# -----------------------------------------------------------
# URLs globales et techniques (Sans préfixe de langue)
# -----------------------------------------------------------
urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("__reload__/", include("django_browser_reload.urls")),
]

# -----------------------------------------------------------
# URLs de l'interface utilisateur (Traduites et préfixées par la langue - ex: /fr/admin/, /en/catalogue/)
# -----------------------------------------------------------
urlpatterns += i18n_patterns(
    path("", HomeView.as_view(), name="home"),

    path("", include("src.users.urls")),
    path("catalogue/", include("src.catalogue.urls")),
    path("admin/", admin.site.urls),

    prefix_default_language=False,
)
