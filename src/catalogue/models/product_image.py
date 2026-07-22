# src/catalogue/models/product_image.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from pathlib import Path
from .product import Product  # <-- Importation relative du modèle principal
import uuid

# Renomme les fichiers image téléchargés selon le SKU et un uuid
def product_image_upload_name(instance, filename):
    ext = filename.split('.')[-1]
    short_uuid = uuid.uuid4().hex[:6]   # Génère un jeton court et unique de 6 caractères (ex: a1b2c3)
    sku = instance.product.sku
    new_filename = f"{sku}_{short_uuid}.{ext}"
    return str(Path("products") / sku / new_filename)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',  # Permet d'appeler product.images.all() dans les templates
        verbose_name=_("Product")
    )

    # Champ Image (Pillow)
    image = models.ImageField(
        upload_to=product_image_upload_name,
        verbose_name=_("Image")
    )

    # Texte alternatif pour le SEO/Accessibilité
    alt_text = models.CharField(
        max_length=255, blank=True,
        verbose_name=_("Alternative text")
    )

    # Est-ce l'image principale du produit
    is_main = models.BooleanField(
        default=False,
        verbose_name=_("Main image")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        ordering = ['-is_main', 'created_at']   # L'image principale apparaît toujours en premier

    def __str__(self):
        return f"Image for {self.product.name} (SKU {self.product.sku})"
