from django.contrib import admin
from parler.admin import TranslatableAdmin

from src.catalogue.models import Product, ProductFamily, ProductPackaging
from src.core.admin import admin_audit_register


@admin_audit_register(ProductFamily, TranslatableAdmin)
class ProductFamilyAdmin(TranslatableAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "company",
        "is_productvariant_on",
        "is_productpackaging_on",
        "is_active",
    )
    list_filter = (
        "company",
        "is_productvariant_on",
        "is_productpackaging_on",
        "is_active",
    )
    search_fields = (
        "translations__name",
        "translations__description",
        "slug",
        "company__official_name",
    )
    ordering = ("company", "slug")
    fieldsets = (
        (None, {"fields": ("company", "name", "description", "slug")}),
        (
            "Configuration",
            {
                "fields": (
                    "is_productvariant_on",
                    "is_productpackaging_on",
                    "is_active",
                )
            },
        ),
    )

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin_audit_register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "slug", "product_family", "company", "is_active")
    list_filter = ("company", "is_active")
    search_fields = (
        "slug",
        "product_family__slug",
        "product_family__translations__name",
        "company__official_name",
    )
    list_select_related = ("company", "product_family")
    ordering = ("company", "slug")
    fieldsets = (
        (None, {"fields": ("company", "product_family", "slug")}),
        ("Configuration", {"fields": ("is_active",)}),
    )


@admin_audit_register(ProductPackaging, TranslatableAdmin)
class ProductPackagingAdmin(TranslatableAdmin):
    list_display = ("id", "name", "product", "base_uom", "ratio", "company")
    list_filter = ("company", "base_uom__type")
    search_fields = (
        "translations__name",
        "translations__code",
        "product__slug",
        "company__official_name",
    )
    list_select_related = ("company", "product", "base_uom")
    ordering = ("company", "product")
    fieldsets = (
        (None, {"fields": ("company", "product", "name", "code")}),
        ("Conversion", {"fields": ("base_uom", "ratio")}),
    )
