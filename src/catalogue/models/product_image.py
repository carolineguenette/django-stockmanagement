from django.db import models
from django.utils.translation import gettext_lazy as _

from src.scope.models.company_owned import CompanyOwned


# def product_image_upload_name(instance, filename):
#     # TODO Revoir la stratégie de nommage de fichiers plus tard.
#     # Code temporairement désactivé à la demande.
#     return filename


class ProductImage(CompanyOwned):
    product = models.ForeignKey(
        "catalogue.Product",
        on_delete=models.CASCADE,
        related_name="product_images",
        verbose_name=_("Product"),
    )

    image = models.ForeignKey(
        "core.Image",
        on_delete=models.CASCADE,
        related_name="product_images",
        verbose_name=_("Image"),
    )

    is_main = models.BooleanField(
        default=False,
        verbose_name=_("Is main"),
    )

    class Meta:
        db_table = "catalogue_productimage"
        verbose_name = _("Product image")
        verbose_name_plural = _("Product images")
        constraints = [
            models.UniqueConstraint(
                fields=["product", "image"],
                name="unique_product_image",
                violation_error_message=_(
                    "This image is already linked to this product."
                ),
            )
        ]

    def __str__(self):
        return f"{self.product.slug} -> {self.image_id}"
