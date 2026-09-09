import json
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from src.access.models import Log


@admin.register(Log)
class AccessLogAdmin(admin.ModelAdmin):
    # Configuration de la liste principale
    list_display = ('changed_at', 'uuid', 'action', 'target_table', 'target_id', 'role_id', 'changed_by')
    list_filter = ('action', 'target_table', 'changed_at')
    search_fields = ('uuid', 'target_id', 'snap_infos')
    ordering = ('-changed_at',)

    # Structuration du formulaire de consultation
    fieldsets = (
        (_("Métadonnées de l'Action"), {
            'fields': ('uuid', 'action', 'changed_at', 'changed_by'),
        }),
        (_("Cible de la Modification"), {
            'fields': ('target_table', 'target_id', 'role_id'),
        }),
        (_("Instantané des Données (Snapshot)"), {
            'fields': ('get_formatted_snap_infos',),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """
        Rend TOUS les champs du modèle non modifiables dans l'interface.
        """
        if obj:
            # Récupère tous les champs concrets du modèle + notre méthode formatée
            return [f.name for f in self.model._meta.fields] + ['get_formatted_snap_infos']
        return super().get_readonly_fields(request, obj)

    # --------------------------------------------------------------------------
    # SÉCURITÉS CONTRE L'ALTÉRATION DES LOGS
    # --------------------------------------------------------------------------
    def has_add_permission(self, request):
        """Désactive l'ajout manuel de logs via l'admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Désactive la modification des logs existants."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Désactive la suppression de logs."""
        return False

    # --------------------------------------------------------------------------
    # RENDU VISUEL AMÉLIORÉ
    # --------------------------------------------------------------------------
    @admin.display(description=_("Contenu du Snapshot (JSON)"))
    def get_formatted_snap_infos(self, obj):
        """
        Formate le JSON de snap_infos en HTML indenté et lisible
        au lieu d'une simple ligne de texte brute.
        """
        if not obj.snap_infos:
            return "-"

        try:
            # Si c'est déjà un dictionnaire (JSONField de Django)
            data = obj.snap_infos
            if isinstance(data, str):
                data = json.loads(data)

            formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
            return format_html(
                '<pre style="background: #f8f9fa; color: #333; padding: 10px; '
                'border: 1px solid #ced4da; border-radius: 4px; '
                'font-family: monospace; overflow-x: auto;">{}</pre>',
                formatted_json
            )
        except Exception:
            return str(obj.snap_infos)
