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
        verbose_name=_("user"),
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="company_roles",
        verbose_name=_("company"),
    )
    role = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="role_assignments",
        verbose_name=_("role"),
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="location_roles",
        verbose_name=_("location"),
    )

    class Meta:
        db_table = "users_role"
        unique_together = ("user", "company", "role", "location")
        verbose_name = _("Role by company")
        verbose_name_plural = _("Roles by company")

    def __str__(self):
        loc_str = (
            f" ({self.location.name})" if self.location else f" ({_('All company')})"
        )
        return f"{self.user.username} - {self.company.name} : {self.role.name}{loc_str}"
