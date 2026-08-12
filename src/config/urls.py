"""
URL configuration for django-stock project.
Centralized router linking language prefixes and local applications.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.defaults import page_not_found
from src.core.views import HomeView

# -----------------------------------------------------------
# URLs globales et techniques (Sans aucun préfixe de langue)
# -----------------------------------------------------------
urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("__reload__/", include("django_browser_reload.urls")),
]

# -----------------------------------------------------------
# Groupe d'URLs cloisonnées (Espace Entreprise)
# - Toutes ces routes hériteront du préfixe /c/<company_slug>/
# -----------------------------------------------------------
company_patterns = [
    path("catalogue/", include("src.catalogue.urls")),
    # Futures applications ayant besoin d'une compagnie active (ex: path("inventory/", include("src.inventory.urls")),)
]

# -----------------------------------------------------------
# Routage principal (Traduites et préfixées par la langue)
# -----------------------------------------------------------
urlpatterns += [
    # Routes globales
    path("", HomeView.as_view(), name="home"),
    path("", include("src.users.urls")),  # users:login, users:register, etc.
    path("core/", include("src.core.urls")),
    path("admin/", admin.site.urls),

    # Point d'entrée unique pour l'espace entreprise
    path("c/<slug:company_slug>/", include(company_patterns)),
]

# -----------------------------------------------------------
#  Route de test pour le gabarit 404 (Mode DEBUG uniquement)
# -----------------------------------------------------------
if settings.DEBUG:
    urlpatterns += [
        path("test-404/", page_not_found, {"exception": Exception("Fake company not found (Simulation)")}),
    ]