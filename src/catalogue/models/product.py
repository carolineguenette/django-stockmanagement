from django.db import models
from django.utils.translation import gettext_lazy as _

from src.core.models.abstract_audit import AbstractAudit
from src.scope.models.company_owned import CompanyOwned


class Product(CompanyOwned, AbstractAudit):
    slug = models.SlugField(
        max_length=255,
        verbose_name=_("Slug"),
    )

    product_family = models.ForeignKey(
        "catalogue.ProductFamily",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Product family"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is active"),
    )

    class Meta:
        db_table = "catalogue_product"
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        constraints = [
            models.UniqueConstraint(
                fields=["company", "slug"],
                name="unique_slug_product_by_company",
                violation_error_message=_(
                    "This slug is already used in this company."
                ),
            )
        ]

    def __str__(self):
        return f"{self.company.official_name} - {self.slug}"
