import json

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from src.core.admin import admin_audit_register
from src.inventory.models import Movement, MovementReason, Stock, Transit


class ReadOnlyInventoryAdmin(admin.ModelAdmin):
    """Consultation technique sans contournement des services métier."""

    def get_readonly_fields(self, request, obj=None):
        return tuple(field.name for field in self.model._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Stock)
class StockAdmin(ReadOnlyInventoryAdmin):
    list_display = (
        "id",
        "product",
        "location",
        "product_packaging",
        "pack_quantity",
        "company",
    )
    list_filter = ("company", "location")
    search_fields = (
        "product__slug",
        "location__slug",
        "product_packaging__translations__name",
    )
    list_select_related = (
        "company",
        "product",
        "location",
        "product_packaging",
    )
    ordering = ("company", "product", "location")


@admin_audit_register(MovementReason, TranslatableAdmin)
class MovementReasonAdmin(TranslatableAdmin):
    list_display = ("id", "name", "slug", "permission_required", "company")
    list_filter = ("company", "permission_required")
    search_fields = (
        "translations__name",
        "slug",
        "permission_required__codename",
        "company__official_name",
    )
    list_select_related = ("company", "permission_required")
    ordering = ("company", "slug")
    fieldsets = (
        (None, {"fields": ("company", "name", "slug")}),
        ("Authorization", {"fields": ("permission_required",)}),
    )

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(Movement)
class MovementAdmin(ReadOnlyInventoryAdmin):
    list_display = (
        "created_at",
        "uuid",
        "product",
        "location_source",
        "location_dest",
        "reason",
        "ref_quantity_delta",
        "company",
    )
    list_filter = ("company", "reason", "created_at")
    search_fields = (
        "uuid",
        "product__slug",
        "location_source__slug",
        "location_dest__slug",
        "created_by_comment",
    )
    list_select_related = (
        "company",
        "product",
        "location_source",
        "location_dest",
        "reason",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    fieldsets = (
        (_("Identity"), {"fields": ("uuid", "company", "stock", "product")}),
        (
            _("Movement"),
            {
                "fields": (
                    "reason",
                    "location_source",
                    "location_dest",
                    "product_packaging_source",
                    "product_packaging_dest",
                )
            },
        ),
        (
            _("Quantities"),
            {
                "fields": (
                    "pack_quantity_init",
                    "pack_quantity_final",
                    "pack_quantity_delta",
                    "ref_quantity_init",
                    "ref_quantity_final",
                    "ref_quantity_delta",
                )
            },
        ),
        (_("Traceability"), {"fields": ("created_by_comment", "formatted_snapshot")}),
        (
            _("Audit Logs"),
            {"fields": ("created_by", "created_at", "updated_by", "updated_at")},
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj) + ("formatted_snapshot",)

    @admin.display(description=_("Snapshot information"))
    def formatted_snapshot(self, obj):
        formatted_json = json.dumps(obj.snap_infos, indent=2, ensure_ascii=False)
        return format_html(
            '<pre style="white-space: pre-wrap; overflow-wrap: anywhere;">{}</pre>',
            formatted_json,
        )


@admin.register(Transit)
class TransitAdmin(ReadOnlyInventoryAdmin):
    list_display = (
        "source_created_at",
        "uuid",
        "product_sku",
        "source_company_name",
        "source_pack_quantity_send",
        "dest_pack_quantity_received",
        "status",
        "company",
    )
    list_filter = ("status", "company", "source_created_at")
    search_fields = (
        "uuid",
        "product_sku",
        "source_product_name",
        "source_company_name",
        "source_location_parent_name",
    )
    list_select_related = ("company",)
    ordering = ("-source_created_at",)
    date_hierarchy = "source_created_at"
