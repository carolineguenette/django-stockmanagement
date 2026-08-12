from django.db import models
from src.scope.context import CompanyContext


class CompanyScopedQuerySet(models.QuerySet):
    def delete(self):
        # Sécurité : force le passage par l'isolation même à la suppression globale
        return super().delete()


class CompanyScopedManager(models.Manager):
    """Filtre les résultats par l'entreprise active à chaque requête."""
    def get_queryset(self):
        queryset = CompanyScopedQuerySet(self.model, using=self._db)
        company_id = CompanyContext.get()

        if company_id is not None:
            return queryset.filter(company_id=company_id)

        # SÉCURITÉ : Si aucun contexte n'est actif, on retourne un QuerySet vide
        # TODO et si on est dans l'interface d'administration Django? (vide ou complet?)
        return queryset.none()
