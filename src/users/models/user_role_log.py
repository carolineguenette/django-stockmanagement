import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from src.core.choices import ActionChoices

class UserRoleLog(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("UUID"),
    )

    user_role = models.ForeignKey(
        "users.UserRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
        verbose_name=_("User role"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="userrole_logs_received",
        verbose_name=_("User"),
    )

    role = models.ForeignKey(
        "access.Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="userrole_logs",
        verbose_name=_("Role"),
    )

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="userrole_logs",
        verbose_name=_("Company"),
    )

    location = models.ForeignKey(
        "company.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="userrole_logs",
        verbose_name=_("Location"),
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="userrole_logs_authored",
        verbose_name=_("Changed by"),
    )

    action = models.CharField(
        max_length=10,
        choices=ActionChoices.choices,
        verbose_name=_("Action"),
    )

    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Changed at"),
    )

    snap_infos = models.JSONField(
        verbose_name=_("Snapshot infos"),
    )

    class Meta:
        db_table = "users_userrolelog"
        verbose_name = _("log")
        verbose_name_plural = _("logs")
        indexes = [
            models.Index(fields=["role"], name="userrole_log_role_idx"),
        ]
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.action} user_role={self.user_role_id}"
