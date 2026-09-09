import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from src.access.choices import AccessLogTargetChoices
from src.core.choices import ActionChoices

class Log(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("UUID"),
    )

    target_table = models.CharField(
        max_length=64,
        choices=AccessLogTargetChoices.choices,
        verbose_name=_("Target table"),
    )

    target_id = models.BigIntegerField(
        verbose_name=_("Target ID"),
    )

    role = models.ForeignKey(
        "access.Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="access_logs",
        verbose_name=_("Role"),
    )

    action = models.CharField(
        max_length=10,
        choices=ActionChoices.choices,
        verbose_name=_("Action"),
    )

    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="access_logs_authored",
        verbose_name=_("Changed by"),
    )

    snap_infos = models.JSONField(
        verbose_name=_("Snapshot infos"),
    )

    class Meta:
        db_table = "access_log"
        verbose_name = _("Log (access)")
        verbose_name_plural = _("Logs (access)")
        indexes = [
            models.Index(fields=["role"], name="access_log_role_idx"),
        ]
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.target_table}:{self.target_id}"
