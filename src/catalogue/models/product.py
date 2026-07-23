# src/catalogue/models/product.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings


class Product(models.Model):
    # SKU : Unique, indexé pour des recherches rapides
    sku = models.CharField(
        max_length=50, unique=True, db_index=True,
        verbose_name=_("SKU"),
        help_text = _("Unique stock keeping unit identifier.")
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_("Name")
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )

    # Prix : Validation pour empêcher un prix négatif
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_("Price")
    )

    alert_threshold = models.PositiveIntegerField(default=5, verbose_name=_("Alert Threshold"))

    # Audit : horodatage et user id
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_products',
        verbose_name=_("Created by")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='updated_products',
        verbose_name=_("Updated by")
    )

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['name']

    def __str__(self):
        return f"{self.sku} - {self.name}"
