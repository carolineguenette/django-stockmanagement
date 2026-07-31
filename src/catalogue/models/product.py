# src/catalogue/models/product.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from src.company.models.company import Company


class Product(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('company')
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_("name")
    )

    # SKU : indexé pour des recherches rapides
    sku = models.CharField(
        max_length=50, db_index=True,
        verbose_name=_("SKU"),
        help_text = _("Unique stock keeping unit identifier.")
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("description")
    )

    # Audit : horodatage et user id
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at")
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='products_created',
        verbose_name=_("created by")
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("updated at")
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='products_updated',
        verbose_name=_("updated by")
    )

    class Meta:
        db_table = "catalogue_product"
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ['name']

    def __str__(self):
        return f"{self.company.name} : {self.name}"