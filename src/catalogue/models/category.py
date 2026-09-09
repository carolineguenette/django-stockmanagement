from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from treebeard.mp_tree import MP_Node

from src.scope.models.translatable_company_owned import TranslatableCompanyOwned


class Category(TranslatableCompanyOwned, MP_Node):
    node_order_by = ["name"]

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("Slug"),
    )

    image = models.ForeignKey(
        "core.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="category_images",
        verbose_name=_("Image"),
    )

    translations = TranslatedFields(
        name=models.CharField(
            max_length=150,
            verbose_name=_("Name"),
        ),
    )

    class Meta:
        db_table = "catalogue_category"
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        constraints = [
            models.UniqueConstraint(
                fields=["company", "slug"],
                name="unique_slug_category_by_company",
                violation_error_message=_(
                    "This slug is already used in this company."
                ),
            )
        ]

    def __str__(self):
        return f"{self.company.official_name} - {self.name}"
