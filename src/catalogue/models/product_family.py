from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from src.core.models.abstract_audit import AbstractAudit
from src.scope.models.company_owned import CompanyOwned


class ProductFamily(TranslatableModel, CompanyOwned, AbstractAudit):
    slug = models.SlugField(
        max_length=255,
        verbose_name=_("Slug"),
    )

    translations = TranslatedFields(
        name=models.CharField(
            max_length=150,
            verbose_name=_("Name"),
        ),
        description=models.TextField(
            blank=True,
            verbose_name=_("Description"),
        ),
    )

    is_productvariant_on = models.BooleanField(
        default=False,
        verbose_name=_("Variants enabled"),
    )

    is_productpackaging_on = models.BooleanField(
        default=False,
        verbose_name=_("Packaging enabled"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is active"),
    )

    class Meta:
        db_table = "catalogue_productfamily"
        verbose_name = _("Product family")
        verbose_name_plural = _("Product families")
        constraints = [
            models.UniqueConstraint(
                fields=["company", "slug"],
                name="unique_slug_productmodel_by_company",
                violation_error_message=_(
                    "This slug is already used in this company."
                ),
            )
        ]

    def __str__(self):
        return f"{self.company.official_name} - {self.name}"
