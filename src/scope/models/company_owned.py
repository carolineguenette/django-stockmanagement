from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from src.scope.managers.company_managers import CompanyScopedManager
from src.scope.managers.companies_managers import CompaniesScopedManager
from src.scope.managers.unscoped_managers import UnscopedManager


class CompanyOwned(models.Model):
    # Clé étrangère vers le modèle Company de l'application company
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",  # Évite les conflits de relations inverses
        related_query_name="%(app_label)s_%(class)s",
    )

    # Managers par défaut (pour les classes non traduisibles - donc sans TranslatableModel comme classe héritée)
    objects = CompanyScopedManager()
    companies = CompaniesScopedManager()
    unscoped = UnscopedManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On mémorise la valeur initiale pour le contrôle lors du save()
        self._initial_company_id = self.company_id

    def validate_company_consistency(self):
        errors = {}

        for field in self._meta.concrete_fields:
            if not isinstance(field, models.ForeignKey):
                continue

            related_model = field.remote_field.model
            if not (
                isinstance(related_model, type)
                and issubclass(related_model, CompanyOwned)
            ):
                continue

            related_id = getattr(self, field.attname)
            if related_id is None:
                continue

            if field.is_cached(self):
                related_company_id = getattr(self, field.name).company_id
            else:
                related_company_id = (
                    related_model._base_manager.filter(pk=related_id)
                    .values_list("company_id", flat=True)
                    .first()
                )

            if (
                related_company_id is not None
                and related_company_id != self.company_id
            ):
                errors[field.name] = _(
                    "The selected object must belong to the same company."
                )

        # Treebeard matérialise le parent dans `path`, et non dans une FK.
        get_parent = getattr(self, "get_parent", None)
        if callable(get_parent) and getattr(self, "depth", 0) > 1:
            parent = get_parent()
            if parent is not None and parent.company_id != self.company_id:
                errors["company"] = _(
                    "A tree node and its parent must belong to the same company."
                )

        if errors:
            raise ValidationError(errors)

    def clean(self):
        super().clean()
        self.validate_company_consistency()

    def move(self, target, pos=None):
        if self.company_id != target.company_id:
            raise ValidationError(
                {
                    "company": _(
                        "A tree node and its parent must belong to the same company."
                    )
                }
            )

        return super().move(target, pos)

    def save(self, *args, **kwargs):
        # Si l'instance existe déjà en BDD et que l'ID de l'entreprise a changé
        if self.pk is not None and self.company_id != self._initial_company_id:
            raise ValidationError(_("The 'company' field is immutable after creation."))

        # `save()` n'appelle pas `full_clean()` nativement. Cette validation doit
        # aussi protéger les créations faites hors des formulaires Django.
        self.validate_company_consistency()

        super().save(*args, **kwargs)
        # Mettre à jour la valeur initiale après une sauvegarde réussie (ex: création)
        self._initial_company_id = self.company_id
