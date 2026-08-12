# src/core/urls.py
from django.urls import path
from .views.debug_views import HomeDebugView

app_name = "core"  # Définit l'espace de noms 'core:'

urlpatterns = [
    path("debug/", HomeDebugView.as_view(), name="home_debug"),
]