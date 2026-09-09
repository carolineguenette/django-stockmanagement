from django.db import models
from parler.managers import TranslatableManager, TranslatableQuerySet

from src.scope.context import CompanyContext
from src.scope.exceptions import MissingCompaniesScope


class CompaniesScopedQuerySetMixin:
    def filter_by_companies_context(self, manager_name: str):
        if self._companies_ids is None:
            raise MissingCompaniesScope(
                f"{manager_name} requires explicit company_ids via for_companies(). "
                "Usage: Model.companies.for_companies([1, 2, 3])"
            )
        return self.filter(company_id__in=self._companies_ids)


class CompaniesScopedQuerySet(CompaniesScopedQuerySetMixin, models.QuerySet):
    pass


class CompaniesScopedTranslatableQuerySet(CompaniesScopedQuerySetMixin, TranslatableQuerySet):
    pass


class CompaniesScopedManager(models.Manager):
    """
    Manager pour les requêtes multi-compagnies sans champs dynamiques traduisibles.
    Nécessite un appel explicite à for_companies(company_ids).
    Lève MissingCompaniesScope si for_companies() n'est pas appelé.
    """
    def __init__(self):
        super().__init__()
        self._companies_ids = None

    def for_companies(self, company_ids):
        """
        Définit la liste des compagnies pour le filtrage.

        Args:
            company_ids: Liste d'IDs de compagnies (list[int] ou list[UUID])
        """
        self._companies_ids = company_ids
        return self

    def get_queryset(self):
        queryset = models.QuerySet(self.model, using=self._db)
        queryset.__class__ = type(
            "CompaniesScopedQuerySet",
            (CompaniesScopedQuerySetMixin, models.QuerySet),
            {}
        )
        queryset._companies_ids = self._companies_ids
        return queryset.filter_by_companies_context(manager_name=self.__class__.__name__)


class CompaniesScopedTranslatableManager(TranslatableManager):
    """
    Manager pour les requêtes multi-compagnies ayant aussi un ou des champs dynamiques traduisibles (avec django-parler).
    Nécessite un appel explicite à for_companies(company_ids).
    Lève MissingCompaniesScope si for_companies() n'est pas appelé.
    """
    def __init__(self):
        super().__init__()
        self._companies_ids = None

    def for_companies(self, company_ids):
        """
        Définit la liste des compagnies pour le filtrage.

        Args:
            company_ids: Liste d'IDs de compagnies (list[int] ou list[UUID])
        """
        self._companies_ids = company_ids
        return self

    def get_queryset(self):
        queryset = TranslatableQuerySet(self.model, using=self._db)
        queryset.__class__ = type(
            "CompaniesScopedTranslatableQuerySet",
            (CompaniesScopedQuerySetMixin, TranslatableQuerySet),
            {}
        )
        queryset._companies_ids = self._companies_ids
        return queryset.filter_by_companies_context(manager_name=self.__class__.__name__)