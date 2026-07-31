from django.db import models
from django.utils.translation import gettext_lazy as _
from src.company.models.company import Company

class Location(models.Model):

    # --- PHASE: POC ---

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='locations',
        verbose_name=_('company')
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('name')
    )

    # --- PHASE: MVP ---
    address_line1 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('address line 1')
    )
    address_line2 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('address line 2')
    )
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('city')
    )
    state_province = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('state or province')
    )
    country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('country')
    )
    postal_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_('postal code')
    )

    # --- PHASE: VX ---
    parent_location = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_locations',
        verbose_name=_('parent location')
    )

    class Meta:
        db_table = 'company_location'
        verbose_name = _('location')
        verbose_name_plural = _('locations')

    def __str__(self):
        if self.parent_location:
            return f"{self.parent_location} > {self.name}"
        return f"{self.company.name} - {self.name}"
