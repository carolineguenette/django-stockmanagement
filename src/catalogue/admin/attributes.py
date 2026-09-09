from django.contrib import admin
from parler.admin import TranslatableAdmin
from treebeard.forms import movenodeform_factory

from src.catalogue.models import AttributeKey, AttributeValue, Category
from src.core.admin import TranslatableMoveNodeForm, TranslatableTreeAdmin


@admin.register(AttributeKey)
class AttributeKeyAdmin(TranslatableAdmin):
    list_display = ("id", "name", "slug", "company")
    list_filter = ("company",)
    search_fields = ("translations__name", "slug", "company__official_name")
    ordering = ("company", "slug")

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(AttributeValue)
class AttributeValueAdmin(TranslatableAdmin):
    list_display = ("id", "value", "attribute_key", "company")
    list_filter = ("company", "attribute_key")
    search_fields = (
        "translations__value",
        "attribute_key__translations__name",
        "company__official_name",
    )
    list_select_related = ("company", "attribute_key")
    ordering = ("company", "attribute_key")


@admin.register(Category)
class CategoryAdmin(TranslatableTreeAdmin):
    form = movenodeform_factory(
        Category,
        form=TranslatableMoveNodeForm,
    )
    list_display = ("name", "company", "slug", "depth", "numchild")
    list_filter = ("company",)
    search_fields = ("translations__name", "slug", "company__official_name")
    ordering = ("path",)
    fieldsets = (
        (None, {"fields": ("company", "name", "slug", "image")}),
        ("Tree position", {"fields": ("_ref_node_id", "_position")}),
    )

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}
