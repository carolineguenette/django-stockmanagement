from django.contrib import admin
from parler.admin import TranslatableAdmin

from src.access.models import Permission


@admin.register(Permission)
class PermissionAdmin(TranslatableAdmin):
    list_display = ('name', 'codename', 'category', 'context', 'sensibility')
    list_filter = ('category', 'context', 'sensibility')
    search_fields = ('codename', 'translations__name')

    fieldsets = (
        ("Identifiants", {
            'fields': ('codename', 'display_order'),
        }),
        ("Champs Traduisibles (Multilingue)", {
            'fields': ('name', 'help_text'),
        }),
        ("Classification et Sécurité", {
            'fields': ('category', 'context', 'sensibility'),
        }),
    )
