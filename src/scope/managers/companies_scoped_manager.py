from django.db import models
from src.scope.exceptions import MissingCompaniesScope


class CompaniesScopedManager(models.Manager):
    """
    Manager pour les requêtes multi-compagnies.
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
        queryset = super().get_queryset()

        if self._companies_ids is None:
            raise MissingCompaniesScope(
                "CompaniesScopedManager requires explicit company_ids via for_companies(). "
                "Usage: Model.companies.for_companies([1, 2, 3])"
            )

        return queryset.filter(company_id__in=self._companies_ids)