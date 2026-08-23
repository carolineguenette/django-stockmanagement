from django.db import models
from django.utils.translation import gettext_lazy as _

from src.scope.models.company_owned import CompanyOwned

class Stock(CompanyOwned):
    product = models.ForeignKey(
        'catalogue.Product',
        on_delete=models.PROTECT,
        related_name='stocks',
        verbose_name=_('Product')
    )
    location = models.ForeignKey(
        'company.Location',
        on_delete=models.PROTECT,
        related_name='stocks',
        verbose_name=_('Location')
    )
    product_packaging = models.ForeignKey(
        'catalogue.ProductPackaging',
        on_delete=models.PROTECT,
        related_name='stocks',
        verbose_name=_('Product Packaging')
    )
    pack_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=5,
        verbose_name=_('Pack Quantity')
    )

    class Meta:
        db_table = 'inventory_stock'
        verbose_name = _('Stock')
        verbose_name_plural = _('Stocks')
        constraints = [
            models.UniqueConstraint(
                fields=["company", "product", "location", "product_packaging"],
                name="unique_stock_by_company_location_and_packaging",
                violation_error_message=_(
                    "There is already a stock for this product, location and packaging."
                ),
            )
        ]

    def __str__(self):
        return f"{self.product} - {self.location} ({self.pack_quantity})"

    def delete(self, *args, **kwargs):
        # Preventing physical hard deletion to protect inventory_movement integrity
        raise NotImplementedError(_("Physical deletion of stock records is prohibited."))