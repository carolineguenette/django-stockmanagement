from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from src.core.models.abstract_audit import AbstractAudit
from src.scope.models.company_owned import CompanyOwned


class Address(TranslatableModel, CompanyOwned, AbstractAudit):
    location = models.ForeignKey(
        "company.Location",
        on_delete=models.RESTRICT,
        related_name="addresses",
        verbose_name=_("Location"),
    )

    country = models.ForeignKey(
        "company.Country",
        on_delete=models.RESTRICT,
        related_name="addresses",
        verbose_name=_("Country"),
    )

    translations = TranslatedFields(
        street_address=models.CharField(
            max_length=255,
            blank=True,
            null=True,
            default=None,
            verbose_name=_("Street address"),
            help_text=_("Street name, number, P.O. box"),
        ),
        extended_address=models.CharField(
            max_length=255,
            blank=True,
            null=True,
            default=None,
            verbose_name=_("Extended address"),
            help_text=_("Apartment, suite, unit, building, floor"),
        ),
        locality=models.CharField(
            max_length=150,
            blank=True,
            null=True,
            default=None,
            verbose_name=_("Locality"),
            help_text=_("City, town, or village"),
        ),
        region=models.CharField(
            max_length=150,
            blank=True,
            null=True,
            default=None,
            verbose_name=_("Region"),
            help_text=_("State, province, county, or canton"),
        ),
    )

    postal_code = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Postal code"),
    )

    time_zone = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Time zone"),
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Latitude"),
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Longitude"),
    )

    class Meta:
        db_table = "company_address"
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        constraints = [
            models.UniqueConstraint(
                fields=["company", "location"],
                name="unique_address_per_company_location",
                violation_error_message=_(
                    "An address already exists for this location in this company."
                ),
            )
        ]

    def __str__(self):
        return f"{self.company.official_name} - {self.location.slug}"