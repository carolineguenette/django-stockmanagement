from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from parler.admin import TranslatableAdmin

from src.core.models.image import Image

# Désenregistrer le modèle Group de Authentication and Authorization (Non utilisé)
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

class BaseAuditAdmin(admin.ModelAdmin):
    """
    Classe parente pour les modèles héritant de AbstractAudit.
    Verrouille les champs d'audit et les regroupe dans une section repliée.
    """

    # On fige les champs en lecture seule
    readonly_fields = ("created_by", "created_at", "updated_by", "updated_at")

    def get_fieldsets(self, request, obj=None):
        # Récupère les champs définis dans la classe enfant
        fieldsets = list(super().get_fieldsets(request, obj))

        audit_fields = ["created_by", "created_at", "updated_by", "updated_at"]

        # Nettoyage des sections existantes (pour éviter les doublons FieldError)
        cleaned_fieldsets = []
        for section_title, section_options in fieldsets:
            fields = [
                f for f in section_options.get("fields", []) if f not in audit_fields
            ]
            if fields:
                new_options = dict(section_options)
                new_options["fields"] = tuple(fields)
                cleaned_fieldsets.append((section_title, new_options))

        # Ajout du bloc d'audit tout en bas
        cleaned_fieldsets.append(
            (
                _("Audit Logs"),
                {
                    "classes": ("collapse",),
                    "fields": tuple(audit_fields),
                },
            )
        )

        return tuple(cleaned_fieldsets)

@admin.register(Image)
class ImageAdmin(TranslatableAdmin, BaseAuditAdmin):
    """
    Combine les onglets de traduction et la section d'audit automatique.
    """
    list_display = ('id', 'image')
    search_fields = ('translations__alt_text',) # Indispensable pour l'autocomplete

    # On ne définit que le champ métier principal.
    # L'audit est injecté tout seul par BaseAuditAdmin.
    fieldsets = (
        (None, {
            'fields': ('image', 'alt_text', 'legend'),
        }),
    )
