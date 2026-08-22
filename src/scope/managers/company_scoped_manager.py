from django.db import models

from src.scope.context import CompanyContext
from src.scope.exceptions import MissingCompanyScope


class CompanyScopedManager(models.Manager):
    """
    Manager pour les requêtes mono-compagnie.
    Filtre automatiquement par l'entreprise active via ContextVar.
    Lève MissingCompanyScope si aucun contexte n'est défini.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        company_id = CompanyContext.get()

        if company_id is None:
            raise MissingCompanyScope(
                "CompanyScopedManager requires an active company context. "
                "Use this manager only in company-scoped views (/c/<slug>/...)."
            )

        return queryset.filter(company_id=company_id)