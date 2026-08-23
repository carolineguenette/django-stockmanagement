from django.db import models
from django.utils.translation import gettext_lazy as _

from src.core.models.abstract_audit import AbstractAudit
from src.scope.models.company_owned import CompanyOwned


class ProductConfig(CompanyOwned, AbstractAudit):
    product = models.ForeignKey(
        "catalogue.Product",
        on_delete=models.CASCADE,
        related_name="location_configs",
        verbose_name=_("Product"),
    )

    location = models.ForeignKey(
        "company.Location",
        on_delete=models.CASCADE,
        related_name="product_configs",
        verbose_name=_("Location"),
    )

    product_packaging = models.ForeignKey(
        "catalogue.ProductPackaging",
        on_delete=models.CASCADE,
        related_name="product_configs",
        verbose_name=_("Product packaging"),
    )

    alert_threshold = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        verbose_name=_("Low stock threshold"),
    )

    class Meta:
        db_table = "catalogue_productconfig"
        verbose_name = _("Product config")
        verbose_name_plural = _("Product configs")

    def __str__(self):
        return f"{self.product.slug} @ {self.location.slug}"
