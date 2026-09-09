import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from src.scope.models.company_owned import CompanyOwned
from src.inventory.choices import TransitStatusChoices


class Transit(CompanyOwned):
    # id PK bigint AUTO est géré automatiquement par BigAutoField de Django par défaut

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_('UUID')
    )
    source_company_name = models.CharField(
        max_length=255,
        verbose_name=_('Source Company Official Name')
    )
    source_location_parent_name = models.CharField(
        max_length=255,
        verbose_name=_('Source Location Parent Name')
    )
    source_product_name = models.CharField(
        max_length=255,
        verbose_name=_('Source Product Name')
    )
    source_product_description = models.TextField(
        verbose_name=_('Source Product Description')
    )
    source_infos = models.JSONField(
        verbose_name=_('Source Information Snapshot')
    )
    source_pack_quantity_send = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        verbose_name=_('Source Pack Quantity Sent')
    )
    source_comment = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Source Comment')
    )
    source_created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Source Created At')
    )
    product_sku = models.CharField(
        max_length=100,
        verbose_name=_('Product SKU')
    )

    # company_id FK = destination (Hérité de la classe abstraite CompanyOwned)

    dest_pack_quantity_received = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        null=True,
        blank=True,
        default=None,
        verbose_name=_('Destination Pack Quantity Received')
    )
    status = models.CharField(
        max_length=50,
        choices=TransitStatusChoices.choices,
        default=TransitStatusChoices.PENDING,
        verbose_name=_('Status')
    )
    dest_comment = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Destination Comment')
    )

    class Meta:
        db_table = 'inventory_transit'
        verbose_name = _('Inventory Transit')
        verbose_name_plural = _('Inventory Transits')

    def __str__(self):
        return f"Transit {self.product_sku} ({self.get_status_display()})"
