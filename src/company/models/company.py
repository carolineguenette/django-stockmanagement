from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from src.core.models.abstract_audit import AbstractAudit
from src.company.choices import TranslationModeChoices

class Company(TranslatableModel, AbstractAudit):
    official_name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_("Official name")
    )

    slug = models.SlugField(
        max_length=150,
        unique=True,
        verbose_name=_("Slug")
    )

    # Déclaration des champs traduisibles par django-parler
    translations = TranslatedFields(
        name = models.CharField(
            max_length=150,
            verbose_name=_('Name')
        ),
    )

    logo = models.ForeignKey(
        'core.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="company_logos",
        verbose_name=_("Logo"),
    )

    accept_negative_stock = models.BooleanField(
        default=False,
        verbose_name = _("Accept negative stock"),
        # POC: block to False
        # V1: Fully integrated
    )

    translation_mode = models.CharField(
        max_length=20,
        choices=TranslationModeChoices.choices,
        default=TranslationModeChoices.DISABLED,
        verbose_name=_("Translation mode"),
        help_text=_(
            "Defines how dynamic company data translations are handled: "
            "disabled (only 1 language), generic languages, or with regional variants."
        ),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is active"),
        help_text=_(
            "An inactive company becomes read-only: its settings, catalogue, and inventory "
            "can no longer be modified and it is excluded from consolidated reports."
        ),
    )

    class Meta:
        db_table = "company_company"
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self):
        return self.official_name
