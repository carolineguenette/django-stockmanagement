from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from src.core.models.abstract_audit import AbstractAudit


class Role(TranslatableModel):
    """
    Modèle représentant les rôles métier. Un rôle regroupe plusieurs permissions.
    Personnalisable par l'utilisateur
    """
    slug = models.SlugField(
        max_length=100,
        verbose_name=_('Slug')
    )

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='roles',
        null=True,
        blank=True,
        verbose_name=_('Company'),
        help_text=_('Leave empty to create a global role. If set, the role will be limited to this company.')
    )

    # Déclaration des champs traduisibles pour django-parler
    translations = TranslatedFields(
        name = models.CharField(
            max_length=100,
            verbose_name=_('Name')
        ),
        description = models.TextField(
            blank=True,
            null=True,
            verbose_name=_('Description')
        ),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is active')
    )
    permissions = models.ManyToManyField(
        'access.Permission',
        through='access.RolePermissions',
        related_name='roles',
        verbose_name=_('Permissions')
    )

    manage_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manages_roles',
        verbose_name=_('Manage by')
    )

    class Meta:
        db_table = 'access_role'
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        constraints = [
            models.UniqueConstraint(
                fields=["slug", "company"],
                name="unique_role_per_company",
                violation_error_message=_(
                    "A role with this slug already exists for this company."
                ),
            )
        ]

    def __str__(self):
        if self.company:
            return f"{self.name} [{self.company.official_name}]"
        return f"{self.name} (Global)"
