# src/catalogue/models/product.py
from django.db import models
from django.utils.translation import gettext_lazy as _

from src.company.models.company import Company


class ProductModel(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='product-models',
        verbose_name=_('company')
    )

    # TEMPORAIRE : en attendant d'avoir model ProductModel
    slug = models.SlugField()