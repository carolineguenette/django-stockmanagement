from django.db import models
from django.utils.translation import gettext_lazy as _
from src.company.models.company import Company


class Location(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="locations",
        verbose_name=_("company"),
    )
    name = models.CharField(max_length=255, verbose_name=_("name"))
    street_address = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("street address")
    )
    city = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("city")
    )
    country = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("country")
    )
    postal_code = models.CharField(
        max_length=20, null=True, blank=True, verbose_name=_("postal code")
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sub_locations",
        verbose_name=_("parent location"),
    )

    class Meta:
        db_table = "company_location"
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")

    def __str__(self):
        return f"{self.company.name} - {self.name}"
