from django.db import models
from django.utils.translation import gettext_lazy as _

from src.scope.models.company_owned import CompanyOwned


class ProductAttributes(CompanyOwned):
    product = models.ForeignKey(
        "catalogue.Product",
        on_delete=models.CASCADE,
        related_name="attributes",
        verbose_name=_("Product"),
    )

    attribute_value = models.ForeignKey(
        "catalogue.AttributeValue",
        on_delete=models.CASCADE,
        related_name="product_attributes",
        verbose_name=_("Attribute value"),
    )

    is_main = models.BooleanField(
        default=False,
        verbose_name=_("Is main"),
    )

    class Meta:
        db_table = "catalogue_productattributes"
        verbose_name = _("Product attribute")
        verbose_name_plural = _("Product attributes")
        constraints = [
            models.UniqueConstraint(
                fields=["product", "attribute_value"],
                name="unique_product_attributevalue",
                violation_error_message=_(
                    "This attribute value is already linked to this product."
                ),
            )
        ]

    def __str__(self):
        return f"{self.product.slug} -> {self.attribute_value.value}"
