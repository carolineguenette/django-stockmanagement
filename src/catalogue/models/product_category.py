from django.db import models
from django.utils.translation import gettext_lazy as _

from src.scope.models.company_owned import CompanyOwned


class ProductCategory(CompanyOwned):
    product_family = models.ForeignKey(
        "catalogue.ProductFamily",
        on_delete=models.CASCADE,
        related_name="product_categories",
        verbose_name=_("Product family"),
    )

    category = models.ForeignKey(
        "catalogue.Category",
        on_delete=models.CASCADE,
        related_name="product_categories",
        verbose_name=_("Category"),
    )

    is_main = models.BooleanField(
        default=False,
        verbose_name=_("Is main"),
    )

    class Meta:
        db_table = "catalogue_productcategory"
        verbose_name = _("Product category")
        verbose_name_plural = _("Product categories")
        constraints = [
            models.UniqueConstraint(
                fields=["product_family", "category"],
                name="unique_productmodel_category",
                violation_error_message=_(
                    "This category is already linked to this product family."
                ),
            )
        ]

    def __str__(self):
        return f"{self.product_family.slug} -> {self.category.slug}"
