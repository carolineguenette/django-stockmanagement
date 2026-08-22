from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from src.scope.managers.company_scoped_manager import CompanyScopedManager
from src.scope.managers.companies_scoped_manager import CompaniesScopedManager
from src.scope.managers.unscoped_manager import UnscopedManager


class CompanyOwned(models.Model):
    # Clé étrangère vers le modèle Company de l'application company
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",  # Évite les conflits de relations inverses
        related_query_name="%(app_label)s_%(class)s",
    )

    # Modèles personnalisés
    objects = CompanyScopedManager()
    companies = CompaniesScopedManager()
    unscoped = UnscopedManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On mémorise la valeur initiale pour le contrôle lors du save()
        self._initial_company_id = self.company_id

    def save(self, *args, **kwargs):
        # Si l'instance existe déjà en BDD et que l'ID de l'entreprise a changé
        if self.pk is not None and self.company_id != self._initial_company_id:
            raise ValidationError(_("The 'company' field is immutable after creation."))

        super().save(*args, **kwargs)
        # Mettre à jour la valeur initiale après une sauvegarde réussie (ex: création)
        self._initial_company_id = self.company_id
