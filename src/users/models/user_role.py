from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class UserRole(models.Model):
    """
    Modèle gérant l'assignation d'un rôle à un utilisateur.
    Remplace le modèle par défaut de Django pour l'attribution des permissions,
    qui n'avait aucun moyen d'isoler les données de chaque entreprise (company).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="role_assignments",
        verbose_name=_('User')
    )

    role = models.ForeignKey(
        'access.Role',
        on_delete=models.RESTRICT,
        related_name='user_assignments',
        verbose_name=_('Role'),
    )

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name="user_roles",
        null=True,
        blank=True,
        verbose_name=_("Company"),
        help_text=_("The company to which the user is assigned. If None, this permission is apply to ALL companies.")
    )

    location = models.ForeignKey(
        'company.Location',
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="user_roles",
        verbose_name=_('Location'),
        help_text=_("The location to which the user is assigned. If None, this permission is apply globally.")
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is active"),
        help_text=_("Designates whether this user assignment to the role is active. Set it to False to disable this permission instead of deleting it.")
    )

    class Meta:
        db_table = "users_userrole"
        verbose_name = _("role")
        verbose_name_plural = _("roles")

        constraints = [
            models.UniqueConstraint(
                fields=["user", "role", "company", "location"],
                name="unique_user_role_company_location",
                violation_error_message=_(
                    "The user already has this role assigned to this company and location."
                ),
            )
        ]

    def __str__(self):
        # Gestion de l'entreprise (Company)
        comp_str = self.company.official_name if self.company else _("GLOBAL")

        # Gestion du site (Location)
        loc_str = f" ({self.location.name})" if self.location else ""

        # Assemblage de la chaîne finale
        return f"{self.user.username} ({comp_str}) : {self.role.name}{loc_str}"

