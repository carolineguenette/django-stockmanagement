from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    official_name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("official name")
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name=_("slug")
    )

    class Meta:
        db_table = "company_company"
        verbose_name = _("company")
        verbose_name_plural = _("companies")

    def __str__(self):
        return self.official_name
