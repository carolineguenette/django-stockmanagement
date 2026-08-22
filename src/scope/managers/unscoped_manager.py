from django.db import models


class UnscopedManager(models.Manager):
    """
    Manager par défaut pour les modèles company-scoped en mode UNSCOPED.
    Retourne un queryset non filtré.

    Usage légitime:
    - Vues globales sans contexte de compagnie (/login, /g/*)
    - Admin Django avec get_queryset() explicite
    - Migrations et commandes de maintenance
    """
    pass