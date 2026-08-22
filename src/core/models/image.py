from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from src.core.models import AbstractAudit


class Image(TranslatableModel, AbstractAudit):
    """
    Modèle gérant le stockage des images avec support d'audit
    et traduction des textes alternatifs et légendes.
    """

    image = models.ImageField(
        verbose_name=_("Image")
    )

    # Déclaration des champs traduits avec django-parler
    translations = TranslatedFields(
        alt_text=models.CharField(
            max_length=255,
            null=True,
            blank=True,
            default=None,
            verbose_name=_("Alternative text"),
            help_text=_("Alternative text for accessibility (img alt attribute)"),
        ),
        legend=models.CharField(
            max_length=255,
            null=True,
            blank=True,
            default=None,
            verbose_name=_("Legend"),
            help_text=_("Optional legend for the image. If support by the model, it will be displayed below the image."),
        ),
    )

    class Meta:
        db_table = "core_image"
        verbose_name = _("Image")
        verbose_name_plural = _("Images")

    def __str__(self):
        return self.alt_text or f"Image {self.id}"
