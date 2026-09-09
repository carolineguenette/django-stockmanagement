from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatedFields

from src.scope.models.translatable_company_owned import TranslatableCompanyOwned


class AttributeKey(TranslatableCompanyOwned):
    slug = models.SlugField(
        max_length=150,
        verbose_name=_("Slug"),
    )

    translations = TranslatedFields(
        name=models.CharField(
            max_length=100,
            verbose_name=_("Name"),
        ),
    )

    class Meta:
        db_table = "catalogue_attributekey"
        verbose_name = _("Attribute key")
        verbose_name_plural = _("Attribute keys")
        constraints = [
            models.UniqueConstraint(
                fields=["company", "slug"],
                name="unique_slug_attributekey_by_company",
                violation_error_message=_(
                    "This slug is already used in this company."
                ),
            )
        ]

    def __str__(self):
        return f"{self.company.official_name} - {self.name}"
