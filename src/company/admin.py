from django.contrib import admin
from parler.admin import TranslatableAdmin

from src.company.models import Company

@admin.register(Company)
class CompanyAdmin(TranslatableAdmin):
    # Colonnes visibles dans la liste
    list_display = ('id', 'name', 'slug', 'is_active', 'created_at')

    # Barre de recherche textuelle
    search_fields = ('translations__name', 'slug')

    # Configuration du formulaire d'édition (Form View)
    fieldsets = (
        ('Informations Générales (Global)', {
            'fields': ('official_name', 'slug', 'is_active')
        }),
        ('Données Traduisibles', {
            'fields': ('name',), # Ce champ apparaîtra automatiquement sous forme d'onglets de langues (FR/EN)
        }),
    )