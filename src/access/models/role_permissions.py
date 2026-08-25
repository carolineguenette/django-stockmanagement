from django.db import models
from django.utils.translation import gettext_lazy as _

class RolePermissions(models.Model):
    """
    Table d'association Many-to-Many entre Role et Permission (POC).
    """
    role = models.ForeignKey(
        'access.Role',
        on_delete=models.CASCADE,
        verbose_name=_('Role')
    )
    permission = models.ForeignKey(
        'access.Permission',
        on_delete=models.RESTRICT,
        verbose_name=_('Permission')
    )

    class Meta:
        db_table = 'access_rolepermissions'
        verbose_name = _('Permission associée à un rôle')
        verbose_name_plural = _('Permissions associées à un rôle')
        constraints = [
            models.UniqueConstraint(
                fields=["role", "permission"],
                name="unique_role_permission",
                violation_error_message=_(
                    "This role already has this permission assigned."
                ),
            )
        ]

    def __str__(self):
        return f"{self.role.name} -> {self.permission.codename}"
