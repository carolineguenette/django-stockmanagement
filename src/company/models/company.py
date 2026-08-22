from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from src.core.models.abstract_audit import AbstractAudit


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

    # Déclaration des champs traduisibles pour django-parler
    translations = TranslatedFields(
        name = models.CharField(
            max_length=150,
            verbose_name=_('Name')
        ),
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = "company_company"
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self):
        return self.official_name
