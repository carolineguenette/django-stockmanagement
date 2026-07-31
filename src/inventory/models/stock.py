from django.db import models
from django.utils.translation import gettext_lazy as _

class Stock(models.Model):
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name=_('company')
    )
    product = models.ForeignKey(
        'catalogue.Product',
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name=_('product')
    )
    location = models.ForeignKey(
        'company.Location',
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name=_('location')
    )
    quantity = models.IntegerField(
        default=0,
        verbose_name=_('quantity')
    )

    class Meta:
        db_table = 'inventory_stock'
        verbose_name = _('stock')
        verbose_name_plural = _('stocks')

    def __str__(self):
        return f"{self.product.name} @ {self.location.name}: {self.quantity}"