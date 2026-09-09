from django.db import models
from parler.managers import TranslatableManager, TranslatableQuerySet

from src.scope.context import CompanyContext
from src.scope.exceptions import MissingCompanyScope

"""
NOTE D'IMPLÉMENTATION - ARCHITECTURE DES MANAGERS

Pourquoi 2 managers différents (régulier vs Translatable) ?
----------------------------------------------------------
django-parler impose l'utilisation de TranslatableManager/TranslatableQuerySet pour gérer
les traductions. Ce manager ne peut être contourné sans perdre les fonctionnalités de traduction.

Options envisagées et rejetées :
---------------------------------
1. SmartManager avec try/except : Anti-pattern architectural, fragile, masque les erreurs
2. Filtrage au niveau des vues/middleware : Moins sécurisé (risque d'oubli), moins testable
3. Détection dynamique dans CompanyOwned : Impossible (classe abstraite ne connaît pas ses enfants)

Solution retenue :
------------------
- CompanyScopedManager : Modèles non-traduisibles (ex: Product, Stock, Movement)
- CompanyScopedTranslatableManager : Modèles traduisibles (ex: LocationType, ProductFamily)

Les deux utilisent un mixin commun (CompanyScopedQuerySetMixin) pour éviter la duplication
de la logique de filtrage par compagnie.

Pour l'admin Django :
---------------------
L'admin utilise UnscopedManager (standard) via UnscopedAdminMixin (défini dans core). TranslatableAdmin
applique ensuite la logique de traduction sur le queryset, donc pas besoin de manager hybride
pour l'admin.
"""

class CompanyScopedQuerySetMixin:
    def filter_by_company_context(self, manager_name:str):
        company_id = CompanyContext.get()
        if company_id is None:
            raise MissingCompanyScope(
                f"{manager_name} requires an active company context. "
                f"Use this manager only in company-scoped views (/c/<slug>/...)."
            )
        return self.filter(company_id=company_id)


class CompanyScopedManager(models.Manager):
    """
    Manager pour les requêtes mono-compagnie sans champs dynamiques traduisibles.
    Filtre automatiquement par l'entreprise active via ContextVar.
    Lève MissingCompanyScope si aucun contexte n'est défini.
    """
    def get_queryset(self):
        # Dans l'admin django, ne pas filtrer
        if CompanyContext.is_admin():
            return super().get_queryset()

        # On récupère le QuerySet personnalisé et on filtre
        queryset = models.QuerySet(self.model, using=self._db)
        queryset.__class__ = type(
            "CompanyScopedQuerySet",
            (CompanyScopedQuerySetMixin, models.QuerySet),
            {}
        )
        return queryset.filter_by_company_context(manager_name=self.__class__.__name__)

class CompanyScopedTranslatableManager(TranslatableManager):
    """
    Manager pour les requêtes mono-compagnie ayant aussi un ou des champs dynamiques traduisibles (avec django-parler)
    Filtre automatiquement par l'entreprise active via ContextVar.
    Lève MissingCompanyScope si aucun contexte n'est défini.
    """
    def get_queryset(self):
        # Dans l'admin django, ne pas filtrer
        if CompanyContext.is_admin():
            return super().get_queryset()

        # On récupère le QuerySet de Parler et on filtre
        queryset = TranslatableQuerySet(self.model, using=self._db)
        queryset.__class__ = type(
            "CompanyScopedTranslatableQuerySet",
            (CompanyScopedQuerySetMixin, TranslatableQuerySet),
            {}
        )
        return queryset.filter_by_company_context(manager_name=self.__class__.__name__)
