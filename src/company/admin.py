from django.contrib import admin
from django import forms
from parler.admin import TranslatableAdmin
from treebeard.forms import movenodeform_factory

from src.core.admin import admin_audit_register, TranslatableTreeAdmin, TranslatableMoveNodeForm
from src.company.models.company import Company
from src.company.models.location_type import LocationType
from src.company.models.location import Location
from src.company.models.address import Address
from src.company.models.country import Country



@admin_audit_register(Company, TranslatableAdmin)
class CompanyAdmin(TranslatableAdmin):
    # Colonnes visibles dans la liste
    list_display = ('id', 'official_name', 'slug', 'is_active', 'created_at')

    # Barre de recherche textuelle
    search_fields = ('translations__name', 'slug')

    prepopulated_fields = {"slug": ("official_name",)}

    # Configuration du formulaire d'édition (Form View)
    fieldsets = (
        ('Informations Générales', {
            'fields': ('official_name', 'slug', 'logo')
        }),
        ('Données Traduisibles', {
            'fields': ('name',),
        }),
        ('Configuration', {
            'fields': ('accept_negative_stock', 'translation_mode', 'is_active')
        }),
    )

@admin.register(LocationType)
class LocationTypeAdmin(TranslatableAdmin):
    list_display = ('id', 'name', 'company')
    list_filter = ('company', )

    # Solution django-parler pour le prepopulated slug
    def get_prepopulated_fields(self, request, obj=None):
        return {
            'slug': ('name',)
        }

    # Configuration du formulaire d'édition (Form View)
    fieldsets = (
        ('Données Traduisibles', {
            'fields': ('name', 'description'),
        }),
        ('Informations générales', {
            'fields': ('slug', 'company')
        }),
    )

def location_formfield_callback(db_field, **kwargs):
    if db_field.name == "location_type":
        return forms.ModelChoiceField(
            queryset=LocationType.unscoped.all(),
            required=not db_field.blank,
            label=db_field.verbose_name,
            help_text=db_field.help_text,
            to_field_name=db_field.remote_field.field_name,
        )

    return db_field.formfield(**kwargs)

@admin_audit_register(Location, TranslatableTreeAdmin)
class LocationAdmin(TranslatableTreeAdmin):
    form = movenodeform_factory(
        Location,
        form=TranslatableMoveNodeForm,
        formfield_callback=location_formfield_callback,
    )
    ordering = ('path',)
    list_display = ('name', 'path', 'depth', 'numchild')
    list_filter = ('company',)

    # Configuration du formulaire d'édition (Form View)
    fieldsets = (
        ('Informations Générales', {
            'fields': ('company', 'name', 'slug' )
        }),
        ('Configuration', {
            'fields': ('location_type', 'is_stockable', 'image')
        }),
        ("Tree position", {
            "fields": ("_ref_node_id", "_position"),
        }),
    )

    # Solution django-parler pour le prepopulated slug
    def get_prepopulated_fields(self, request, obj=None):
        return {
            'slug': ('name',)
        }

@admin_audit_register(Address, TranslatableAdmin)
class AddressAdmin(TranslatableAdmin):
    # Colonnes visibles dans la liste
    list_display = ('id', 'location', 'country', 'postal_code')
    list_filter = ('company',)

    # Configuration du formulaire d'édition (Form View)
    fieldsets = (
        ('Informations Générales', {
            'fields': ('company', 'location', 'country', 'postal_code')
        }),
        ('Données Traduisibles', {
            'fields': ('street_address', 'extended_address', 'locality', 'region'),
        }),
        ('Configuration', {
            'fields': ('time_zone', 'latitude', 'longitude')
        }),
    )

@admin.register(Country)
class CountryAdmin(TranslatableAdmin):
    list_display = ('id', 'iso_code', 'name')
    search_fields = ('translations__name', )