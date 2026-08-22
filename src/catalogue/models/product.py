# src/catalogue/models/product.py
from django.db import models
from django.utils.translation import gettext_lazy as _

from src.scope.models.abstract_companyowned import CompanyOwned
from src.core.models.abstract_audit import AbstractAudit


class Product(CompanyOwned, AbstractAudit):
    """
    Modèle de produit isolé par entreprise et audité.
    Hérite des champs d'audit et des 3 managers de scope.
    """

    # TEMPORAIRE : en attendant d'avoir model ProductModel
    official_name = models.CharField(
        max_length=255,
        verbose_name=_("name")
    )


    class Meta:
        db_table = "catalogue_product"
        verbose_name = _("product")
        verbose_name_plural = _("products")

    def __str__(self):
        return f"{self.company.official_name}"