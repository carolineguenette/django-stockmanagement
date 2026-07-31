from django.db import models
from django.contrib.auth.models import Group
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from src.company.models.company import Company
from src.company.models.location import Location


class Role(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name=_('user')
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="roles",
        verbose_name=_("company role"),
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="location_roles",
        verbose_name=_("location_role"),
    )

    role = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name=_('auth group role')
    )

    class Meta:
        db_table = "users_role"
        verbose_name = _("role")
        verbose_name_plural = _("roles")

        constraints = [
            models.UniqueConstraint(
                fields=["user", "company", "role", "location"],
                name='unique_users_role'
            )
        ]

    def __str__(self):
        loc_str = (
            f" ({self.location.name})" if self.location else f" ({_('All company')})"
        )
        return f"{self.user.username} - {self.company.name} : {self.role.name}{loc_str}"
