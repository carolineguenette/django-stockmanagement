from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Movement(models.Model):
    DIRECTION_CHOICES = [
        ("IN", _("IN: Qty added")),
        ("OUT", _("OUT: Qty subtracted")),
        ("NONE", _("NONE: No global change")),
    ]

    REASON_CHOICES = [
        ("PURCHASE", _("Purchase")),
        ("MANUFACTURE", _("Manufacture")),
        ("SALE", _("Sale")),
        ("LOSS", _("Loss")),
        ("TRANSFER_IN", _("Transfer In")),
        ("TRANSFER_OUT", _("Transfer Out")),
        ("RELOCATE", _("Relocate")),
    ]

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="movements",
        verbose_name=_("company"),
    )
    stock = models.ForeignKey(
        "inventory.Stock",
        on_delete=models.CASCADE,
        related_name="movements",
        verbose_name=_("stock"),
    )
    when = models.DateTimeField(auto_now_add=True, verbose_name=_("when"))
    by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movements",
        verbose_name=_("by user"),
    )
    quantity_move = models.IntegerField(verbose_name=_("quantity moved"))
    direction = models.CharField(
        max_length=4,
        choices=DIRECTION_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("direction"),
    )
    reason = models.CharField(
        max_length=20, choices=REASON_CHOICES, verbose_name=_("reason")
    )
    source_location = models.ForeignKey(
        "company.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_movements",
        verbose_name=_("source location"),
    )
    dest_location = models.ForeignKey(
        "company.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dest_movements",
        verbose_name=_("destination location"),
    )
    create_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    create_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movements_created",
        verbose_name=_("created by"),
    )

    class Meta:
        db_table = "inventory_movement"
        verbose_name = _("movement")
        verbose_name_plural = _("movements")
