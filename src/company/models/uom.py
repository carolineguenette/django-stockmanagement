from django.db import models
from django.db.models import Case, When, Value, IntegerField
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from src.core.models.abstract_audit import AbstractAudit
from src.scope.models.company_owned import CompanyOwned
from src.company.choices import UomTypeChoices, UomSystemChoices

class Uom(TranslatableModel, CompanyOwned, AbstractAudit):
    type = models.CharField(
        max_length=20,
        choices=UomTypeChoices.choices,
        verbose_name=_("Type"),
    )

    system = models.CharField(
        max_length=20,
        choices=UomSystemChoices.choices,
        default=UomSystemChoices.NONE,
        verbose_name=_("System"),
    )

    translations = TranslatedFields(
        name=models.CharField(
            max_length=100,
            verbose_name=_("Name"),
        ),
        code=models.CharField(
            max_length=20,
            blank=True,
            verbose_name=_("Code"),
        ),
    )

    is_reference = models.BooleanField(
        default=False,
        verbose_name=_("Is reference"),
    )

    # Colonne technique calculée au niveau de la DB pour pouvoir créer une contrainte UNIQUE
    # sur is_reference = True et PAS sur is_reference = False
    is_ref_contraint = models.GeneratedField(
        expression=Case(
            When(is_reference=True, then=Value(1)),
            default=None,
            output_field=models.IntegerField(),
        ),
        output_field=models.IntegerField(),
        db_persist=True, # Important pour pouvoir mettre un index dessus
        null=True
    )

    ratio = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        verbose_name=_("Ratio"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is active"),
    )

    class Meta:
        db_table = "company_uom"
        verbose_name = _("Unit of measure")
        verbose_name_plural = _("Units of measure")
        constraints = [
            models.UniqueConstraint(
                fields=["company", "type", "is_ref_contraint"],
                name="unique_reference_uom_per_company_type",
                violation_error_message = _(
                    "A reference unit already exists for this type."
                ),
            )
        ]

    def __str__(self):
        return f"{self.company.official_name} - {self.name}"