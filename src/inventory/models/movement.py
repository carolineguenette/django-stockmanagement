import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from src.scope.models.company_owned import CompanyOwned
from src.core.models.abstract_audit import AbstractAudit

class Movement(CompanyOwned, AbstractAudit):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    stock = models.ForeignKey(
        'inventory.Stock',
        on_delete=models.PROTECT,
        related_name='movements',
        verbose_name=_('Stock')
    )

    product = models.ForeignKey(
        'catalogue.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_movements',
        verbose_name=_('Product')
    )
    location_source = models.ForeignKey(
        'company.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_movements',
        verbose_name=_('Source Location')
    )
    location_dest = models.ForeignKey(
        'company.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='destination_movements',
        verbose_name=_('Destination Location')
    )
    product_packaging_source = models.ForeignKey(
        'catalogue.ProductPackaging',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='packaging_init',
        verbose_name=_('Initial Product Packaging')
    )
    product_packaging_dest = models.ForeignKey(
        'catalogue.ProductPackaging',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='packaging_final',
        verbose_name=_('Final Product Packaging')
    )
    reason = models.ForeignKey(
        'inventory.MovementReason',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movements',
        verbose_name=_('Movement Reason')
    )

    # Exact metric recording fields for quick filtering without traversing JSON
    pack_quantity_init = models.DecimalField(max_digits=20, decimal_places=6, verbose_name=_('Initial Pack Quantity'))
    pack_quantity_final = models.DecimalField(max_digits=20, decimal_places=6, verbose_name=_('Final Pack Quantity'))
    pack_quantity_delta = models.DecimalField(max_digits=20, decimal_places=6, verbose_name=_('Delta Pack Quantity'))
    ref_quantity_init = models.DecimalField(max_digits=20, decimal_places=6, verbose_name=_('Initial Ref Quantity'))
    ref_quantity_final = models.DecimalField(max_digits=20, decimal_places=6, verbose_name=_('Final Ref Quantity'))
    ref_quantity_delta = models.DecimalField(max_digits=20, decimal_places=6, verbose_name=_('Delta Ref Quantity'))

    snap_infos = models.JSONField(verbose_name=_('Snapshot Information'))

    created_by_comment = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('User Comment')
    )


    class Meta:
        db_table = 'inventory_movement'
        indexes = [
            models.Index(fields=['company', 'product']),
        ]
        verbose_name = _('Inventory Movement')
        verbose_name_plural = _('Inventory Movements')
