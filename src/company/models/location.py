from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from treebeard.mp_tree import MP_Node

from src.core.models.abstract_audit import AbstractAudit
from src.scope.models.abstract_companyowned import CompanyOwned

class Location(TranslatableModel, CompanyOwned, MP_Node, AbstractAudit):

    slug = models.SlugField(
        max_length=255,
        verbose_name=_('Slug')
    )

    # Déclaration des champs traduisibles pour django-parler
    translations = TranslatedFields(
        name = models.CharField(
            max_length=150,
            verbose_name=_('Name')
        ),
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_('name')
    )

    address_line1 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('address (line 1)')
    )
    address_line2 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('address (line 2)')
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

    class Meta:
        db_table = 'company_location'
        verbose_name = _('location')
        verbose_name_plural = _('locations')

    def __str__(self): 
        return f"{self.company.official_name} - {self.name}"
