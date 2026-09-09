from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from treebeard.mp_tree import MP_Node

from src.scope.models.translatable_company_owned import TranslatableCompanyOwned
from src.core.models.abstract_audit import AbstractAudit


class Location(TranslatableCompanyOwned, MP_Node, AbstractAudit):

    node_order_by = ["slug"]

    slug = models.SlugField(
        max_length=150,
        verbose_name=_('Slug')
    )

    location_type = models.ForeignKey(
        "company.LocationType",
        on_delete=models.RESTRICT,
        related_name="locations",
        verbose_name=_("Location type"),
    )

    is_stockable = models.BooleanField(
        default=None,
        verbose_name=_("Stockable (override)"),
        null=True,
        blank=True,
        help_text=_(
            "Leave blank (Null) to let the system decide automatically: leaf nodes "
            "will be stockable, parent nodes will not. Set explicitly to True or False "
            "to override this behavior."
        ),
    )

    @property
    def can_stock(self) -> bool:
        """
        Calcule dynamiquement si la location peut recevoir du stock.
        """
        # Si une décision explicite a été prise sur la location, on la respecte
        if self.is_stockable is not None:
            return self.is_stockable

        # Sinon, le comportement dépend de la structure de l'arbre (Treebeard)
        # django-treebeard maintient 'numchild'. Si numchild == 0, c'est une feuille.
        is_leaf = getattr(self, 'numchild', 0) == 0
        return is_leaf

    image = models.ForeignKey(
        "core.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locations",
        verbose_name=_("Image"),
    )

    # Déclaration des champs traduisibles pour django-parler
    translations = TranslatedFields(
        name = models.CharField(
            max_length=150,
            verbose_name=_('Name')
        ),
    )

    class Meta:
        db_table = 'company_location'
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')

        constraints = [
            models.UniqueConstraint(
                fields=["company", "slug"],
                name="unique_slug_location_by_company",
                violation_error_message=_(
                    "This slug is already used in this company."
                ),
            )
        ]

    def __str__(self): 
        return f"{self.name} ({self.company.official_name})"
