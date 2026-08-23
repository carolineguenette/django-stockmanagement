from django.db import models
from django.utils.translation import gettext_lazy as _

from parler.models import TranslatableModel, TranslatedFields

from src.scope.models.company_owned import CompanyOwned
from src.core.models.abstract_audit import AbstractAudit

class MovementReason(TranslatableModel, CompanyOwned, AbstractAudit):
    slug = models.SlugField(
        max_length=150,
        verbose_name=_('Slug')
    )

    translations = TranslatedFields(
        name=models.CharField(
            max_length=150,
            verbose_name=_("Name"),
        )
    )

    permission_required = models.ForeignKey(
        'access.Permission',
        on_delete=models.RESTRICT,
        related_name='movement_reasons',
        verbose_name=_('Permission Required')

    )

    class Meta:
        db_table = 'inventory_movementreason'
        verbose_name = _('Movement Reason')
        verbose_name_plural = _('Movement Reasons')
        constraints = [
            models.UniqueConstraint(
                fields=["company", "slug"],
                name="unique_movement_reason_by_company_and_slug",
                violation_error_message=_(
                    "A reason movement already exists with this slug."
                ),
            )
        ]
    def __str__(self):
        return f"{self.company.official_name} - {self.translations.name}"
