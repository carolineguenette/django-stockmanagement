from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from src.core.models.abstract_audit import AbstractAudit
from src.scope.models.company_owned import CompanyOwned


class ProductPackaging(TranslatableModel, CompanyOwned, AbstractAudit):
    product = models.ForeignKey(
        "catalogue.Product",
        on_delete=models.CASCADE,
        related_name="packagings",
        verbose_name=_("Product"),
    )

    base_uom = models.ForeignKey(
        "company.Uom",
        on_delete=models.RESTRICT,
        related_name="product_packagings",
        verbose_name=_("Base unit of measure"),
    )

    translations = TranslatedFields(
        name=models.CharField(
            max_length=150,
            verbose_name=_("Name"),
        ),
        code=models.CharField(
            max_length=50,
            blank=True,
            verbose_name=_("Code"),
        ),
    )

    ratio = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        verbose_name=_("Ratio"),
    )

    class Meta:
        db_table = "catalogue_productpackaging"
        verbose_name = _("Product packaging")
        verbose_name_plural = _("Product packagings")

    def __str__(self):
        return f"{self.product.slug} - {self.name}"
