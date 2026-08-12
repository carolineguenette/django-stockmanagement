# src/catalogue/models/product.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from src.company.models.company import Company
from src.scope.managers import CompanyScopedManager


class Product(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('company')
    )

    # TEMPORAIRE : en attendant d'avoir model ProductModel
    name = models.CharField(
        max_length=255,
        verbose_name=_("name")
    )

    # Modèles personnalisés
    objects = CompanyScopedManager()
    # mc_objects = MultiCompanyScopedManager()

    class Meta:
        db_table = "catalogue_product"
        verbose_name = _("product")
        verbose_name_plural = _("products")

    def __str__(self):
        return f"{self.company.official_name} : {self.name}"