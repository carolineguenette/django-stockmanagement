# src/catalogue/signals.py
from pathlib import Path
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models.product_image import ProductImage


@receiver(post_delete, sender=ProductImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        file_path = Path(instance.image.path)
        if file_path.is_file():
            file_path.unlink()

            sku_folder = file_path.parent
            if sku_folder.is_dir() and not any(sku_folder.iterdir()):
                sku_folder.rmdir()


@receiver(pre_save, sender=ProductImage)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = ProductImage.objects.get(pk=instance.pk).image
    except ProductImage.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        file_path = Path(old_file.path)
        if file_path.is_file():
            file_path.unlink()
