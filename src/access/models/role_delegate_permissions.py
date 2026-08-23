from django.db import models
from django.utils.translation import gettext_lazy as _


class RoleDelegatePermissions(models.Model):
    """
    Table d'association entre un rôle et les permissions qu'il peut déléguer.
    """

    role = models.ForeignKey(
        "access.Role",
        on_delete=models.CASCADE,
        related_name="delegate_permissions",
        verbose_name=_("Role"),
    )
    delegate_perm = models.ForeignKey(
        "access.Permission",
        on_delete=models.RESTRICT,
        related_name="delegated_by_roles",
        verbose_name=_("Delegate permission"),
    )

    class Meta:
        db_table = "access_roledelegatepermissions"
        verbose_name = _("Access role delegate permission")
        verbose_name_plural = _("Access role delegate permissions")
        constraints = [
            models.UniqueConstraint(
                fields=["role", "delegate_perm"],
                name="unique_role_delegate_permission",
                violation_error_message=_(
                    "This role already has this delegate permission assigned."
                ),
            )
        ]

    def __str__(self):
        return f"{self.role.name} -> {self.delegate_perm.codename}"