from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("name")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at")
    )

    class Meta:
        db_table = "company_company"
        verbose_name = _("company")
        verbose_name_plural = _("companies")

    def __str__(self):
        return self.name
