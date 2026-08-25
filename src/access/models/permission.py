from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from src.access.choices import PermissionContextChoices, PermissionSensibilityChoices, PermissionCategoryChoices

class Permission(TranslatableModel):
    """
    Catalogue des permissions métier disponibles dans l'application.
    Les données de cette table sont insérées à l'initialisation du système et ne changeront plus (sauf développement)
    """
    codename = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Codename')
    )

    # Déclaration des champs traduisibles avec django-parler
    translations = TranslatedFields(
        name = models.CharField(
            max_length=150,
            verbose_name=_('Name')
        ),
        help_text = models.TextField(
            blank=True,
            null=True,
            verbose_name=_('Help text')
        ),
    )

    context = models.CharField(
        max_length=20,
        choices=PermissionContextChoices.choices,
        verbose_name=_('Context')
    )
    sensibility = models.CharField(
        max_length=10,
        choices=PermissionSensibilityChoices.choices,
        verbose_name=_('Sensibility')
    )
    category = models.CharField(
        max_length=20,
        choices=PermissionCategoryChoices.choices,
        verbose_name=_('Category')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is active')
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name=_('Display order')
    )

    class Meta:
        db_table = 'access_permission'
        verbose_name = _('Permission')
        verbose_name_plural = _('Permissions')
        ordering = ['display_order', 'codename']

    def __str__(self):
        return f"{self.name} ({self.codename})"
