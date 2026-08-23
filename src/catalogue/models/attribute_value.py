from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from src.scope.models.company_owned import CompanyOwned


class AttributeValue(TranslatableModel, CompanyOwned):
    attribute_key = models.ForeignKey(
        "catalogue.AttributeKey",
        on_delete=models.CASCADE,
        related_name="attribute_values",
        verbose_name=_("Attribute key"),
    )

    translations = TranslatedFields(
        value=models.CharField(
            max_length=150,
            verbose_name=_("Value"),
        ),
    )

    class Meta:
        db_table = "catalogue_attributevalue"
        verbose_name = _("Attribute value")
        verbose_name_plural = _("Attribute values")

    def __str__(self):
        return f"{self.attribute_key.name}: {self.value}"
