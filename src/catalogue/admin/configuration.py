from django.contrib import admin

from src.catalogue.models import (
    ProductAttributes,
    ProductCategory,
    ProductConfig,
    ProductFamilyImage,
    ProductImage,
)
from src.core.admin import admin_audit_register


class CompanyRelationAdmin(admin.ModelAdmin):
    list_filter = ("company",)
    list_select_related = ("company",)
    ordering = ("company", "id")


@admin.register(ProductCategory)
class ProductCategoryAdmin(CompanyRelationAdmin):
    list_display = ("id", "product_family", "category", "company", "is_main")
    list_filter = ("company", "is_main")
    search_fields = (
        "product_family__slug",
        "product_family__translations__name",
        "category__slug",
        "category__translations__name",
    )
    list_select_related = ("company", "product_family", "category")


@admin.register(ProductAttributes)
class ProductAttributesAdmin(CompanyRelationAdmin):
    list_display = ("id", "product", "attribute_value", "company", "is_main")
    list_filter = ("company", "is_main", "attribute_value__attribute_key")
    search_fields = (
        "product__slug",
        "attribute_value__translations__value",
        "attribute_value__attribute_key__translations__name",
    )
    list_select_related = (
        "company",
        "product",
        "attribute_value",
        "attribute_value__attribute_key",
    )


@admin.register(ProductFamilyImage)
class ProductFamilyImageAdmin(CompanyRelationAdmin):
    list_display = ("id", "product_family", "image", "company", "is_main")
    list_filter = ("company", "is_main")
    search_fields = ("product_family__slug", "product_family__translations__name")
    list_select_related = ("company", "product_family", "image")


@admin.register(ProductImage)
class ProductImageAdmin(CompanyRelationAdmin):
    list_display = ("id", "product", "image", "company", "is_main")
    list_filter = ("company", "is_main")
    search_fields = ("product__slug",)
    list_select_related = ("company", "product", "image")


@admin_audit_register(ProductConfig)
class ProductConfigAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "location",
        "product_packaging",
        "alert_threshold",
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
    fieldsets = (
        (None, {"fields": ("company", "product", "location")}),
        (
            "Stock alert",
            {"fields": ("product_packaging", "alert_threshold")},
        ),
    )
