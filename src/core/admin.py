from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm
from treebeard.admin import TreeAdmin
from treebeard.forms import MoveNodeForm

from src.core.models.image import Image


# ****************************************************
# Désenregistrer le modèle Group de Authentication and Authorization (Non utilisé)
# ****************************************************
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

# ****************************************************
# Admin - Classes Translatable + Tree combinées
# -> Utilisée pour company.Location et catalogue.Category
# ****************************************************
class TranslatableTreeAdmin(TranslatableAdmin, TreeAdmin):
    pass

class TranslatableMoveNodeForm(MoveNodeForm, TranslatableModelForm):
    pass

# ****************************************************
# Admin - Décorateur d'audit
# ****************************************************
def admin_audit_register(model, base_admin_site=admin.ModelAdmin):
    """
    Décorateur d'audit :
    - déplace les champs d'audits read-only dans un volet replié "Audit Logs"
    - injecte la sauvegarde automatique des champs d'audits à partir du service core/services/AuditService
    """

    def decorator(admin_class):
        # Injection de la sauvegarde automatique
        def new_save_model(self, request, obj, form, change):
            from src.core.services.audit_service import AuditService
            AuditService.apply_audit(obj, user=request.user)

            base_admin_site.save_model(self, request, obj, form, change)

        admin_class.save_model = new_save_model

        # Injection des champs en lecture seule
        admin_class.readonly_fields = tuple(
            set(getattr(admin_class, 'readonly_fields', ()) + ("created_by", "created_at", "updated_by", "updated_at")))

        # Injection du volet replié "Audit Logs" tout en bas
        original_get_fieldsets = admin_class.get_fieldsets

        def new_get_fieldsets(self, request, obj=None):
            fieldsets = list(original_get_fieldsets(self, request, obj))
            audit_fields = ["created_by", "created_at", "updated_by", "updated_at"]
            cleaned_fieldsets = []
            for section_title, section_options in fieldsets:
                fields = [f for f in section_options.get("fields", []) if f not in audit_fields]
                if fields:
                    new_options = dict(section_options)
                    new_options["fields"] = tuple(fields)
                    cleaned_fieldsets.append((section_title, new_options))
            cleaned_fieldsets.append((_("Audit Logs"), {"classes": ("collapse",), "fields": tuple(audit_fields)}))
            return tuple(cleaned_fieldsets)

        admin_class.get_fieldsets = new_get_fieldsets

        # Enregistrement officiel dans Django
        admin.site.register(model, admin_class)
        return admin_class

    return decorator


# ****************************************************
# Admin - register
# ****************************************************
@admin_audit_register(Image, TranslatableAdmin)
class ImageAdmin(TranslatableAdmin):
    list_display = ('id', 'image')
    search_fields = ('translations__alt_text',) # Indispensable pour l'autocomplete

    # On ne définit que le champ métier principal.
    # L'audit est injecté par BaseAuditAdmin.
    fieldsets = (
        (None, {
            'fields': ('image', 'alt_text', 'legend'),
        }),
    )
