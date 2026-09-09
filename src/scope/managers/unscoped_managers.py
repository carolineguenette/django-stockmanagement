from django.db import models
from parler.managers import TranslatableManager, TranslatableQuerySet


class UnscopedManager(models.Manager):
    """
    Manager par défaut pour les modèles CompanyOwned en mode UNSCOPED.
    Retourne un queryset non filtré par compagnie.

    Usage légitime :
    - Admin Django (via UnscopedAdminMixin)
    - Vues globales sans contexte de compagnie (/login, /g/*)
    - Migrations et commandes de maintenance
    - Tests d'isolation inter-compagnies
    """
    pass


class UnscopedTranslatableManager(TranslatableManager):
    """
    Manager non filtré pour les modèles traduisibles (django-parler).

    Note : Ce manager n'est généralement pas nécessaire car :
    - Dans l'admin, TranslatableAdmin applique la logique de traduction sur le queryset
      retourné par UnscopedManager standard
    - Dans les tests, on peut utiliser UnscopedManager et appliquer .language() manuellement

    Ce manager est disponible pour les cas d'usage avancés où un accès direct
    au TranslatableQuerySet non filtré est nécessaire.
    """
    pass