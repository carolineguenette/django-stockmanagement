from django.db import models
from django.utils.translation import gettext_lazy as _

from src.scope.models.company_owned import CompanyOwned


class ProductFamilyImage(CompanyOwned):
    product_family = models.ForeignKey(
        "catalogue.ProductFamily",
        on_delete=models.CASCADE,
        related_name="product_family_images",
        verbose_name=_("Product family"),
    )

    image = models.ForeignKey(
        "core.Image",
        on_delete=models.CASCADE,
        related_name="product_family_images",
        verbose_name=_("Image"),
    )

    is_main = models.BooleanField(
        default=False,
        verbose_name=_("Is main"),
    )

    class Meta:
        db_table = "catalogue_productfamilyimage"
        verbose_name = _("Product family image")
        verbose_name_plural = _("Product family images")
        constraints = [
            models.UniqueConstraint(
                fields=["product_family", "image"],
                name="unique_productmodel_image",
                violation_error_message=_(
                    "This image is already linked to this product family."
                ),
            )
        ]

    def __str__(self):
        return f"{self.product_family.slug} -> {self.image_id}"
