from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatedFields

from src.scope.models.translatable_company_owned import TranslatableCompanyOwned

class LocationType(TranslatableCompanyOwned):

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("Slug"),
    )

    translations = TranslatedFields(
        name=models.CharField(
            max_length=150,
            verbose_name=_("Name"),
        ),
        description=models.TextField(
            blank=True,
            verbose_name=_("Description"),
        ),
    )

    class Meta:
        db_table = "company_locationtype"
        verbose_name = _("Location type")
        verbose_name_plural = _("Location types")
        constraints = [
            models.UniqueConstraint(
                fields=["company", "slug"],
                name="unique_slug_locationtype_by_company",
                violation_error_message=_(
                    "This slug is already used in the company."
                ),
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.company.official_name})"