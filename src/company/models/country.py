 
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class Country(TranslatableModel):
    iso_code = models.CharField(
        max_length=2,
        unique=True,
        verbose_name=_("ISO code"),
    )

    translations = TranslatedFields(
        name=models.CharField(
            max_length=100,
            verbose_name=_("Name"),
        ),
    )

    class Meta:
        db_table = "company_country"
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
        ordering = ["iso_code"]

    def __str__(self):
        return f"{self.iso_code} - {self.name}"