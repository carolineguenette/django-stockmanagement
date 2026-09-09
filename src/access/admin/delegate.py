from django import forms
from django.contrib import admin
from django.contrib.admin import widgets
from django.utils.translation import gettext_lazy as _

from src.access.models import Role, Permission, RoleDelegatePermissions


# ==============================================================================
# MODÈLE PROXY DE RÔLE
# ==============================================================================
class RoleDelegate(Role):
    """
    Modèle Proxy de Role pour afficher les rôles possédant au moins une permission de catégorie DELEGATE.
    Les données de Role sont en lecture seule. Seule la liste des permissions déléguées est modifiable.
    """

    class Meta:
        proxy = True
        verbose_name = _("Délégation")
        verbose_name_plural = _("Délégations")


# ==============================================================================
# FORMULAIRE DE MODIFICATION DES PERMISSIONS DÉLÉGUÉES
# ==============================================================================
class RoleDelegateAdminForm(forms.ModelForm):
    """
    Formulaire personnalisé pour la gestion des permissions déléguées.

    Il remplace les champs d'édition standards du Rôle par un widget de sélection
    double (FilteredSelectMultiple) lié à la table intermédiaire des délégations.
    """
    # Champ virtuel représentant les permissions que ce rôle a le droit de déléguer.
    # On exclut les permissions de catégorie 'DELEGATE' à l'initialisation.
    delegate_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.exclude(category='DELEGATE'),
        required=False,
        label=_("Permissions déléguées à ce rôle"),
        widget=widgets.FilteredSelectMultiple(
            verbose_name=_('Permissions'),
            is_stacked=False
        )
    )

    class Meta:
        model = RoleDelegate
        fields = ['company', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Garantir l'exclusion à chaque initialisation dynamique du formulaire
        self.fields['delegate_permissions'].queryset = Permission.objects.exclude(
            category='DELEGATE'
        )
        # Si on modifie une instance existante, on pré-remplit le widget avec les
        # permissions actuellement associées dans la table de liaison (RoleDelegatePermissions)
        if self.instance and self.instance.pk:
            initial_perms = RoleDelegatePermissions.objects.filter(
                role_id=self.instance.pk
            ).values_list('delegate_perm_id', flat=True)

            self.fields['delegate_permissions'].initial = list(initial_perms)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            self.save_delegate_permissions()
        return instance

    def save_delegate_permissions(self):
        """
        Synchronisation manuelle (Ajouts / Suppressions)
        de la table intermédiaire 'access_roledelegatepermissions'.
        """
        # Récupération des permissions sélectionnées dans la colonne de droite
        selected_perms = self.cleaned_data.get('delegate_permissions', [])
        current_perms_ids = set(selected_perms.values_list('id', flat=True))

        # Récupération des permissions actuellement stockées en base pour ce rôle
        existing_relations = RoleDelegatePermissions.objects.filter(role_id=self.instance.pk)
        existing_perms_ids = set(existing_relations.values_list('delegate_perm_id', flat=True))

        # Calcul des écarts pour optimiser les requêtes SQL (Bulk operations)
        to_delete = existing_perms_ids - current_perms_ids
        to_add = current_perms_ids - existing_perms_ids

        # Suppression des relations décochées
        if to_delete:
            existing_relations.filter(delegate_perm_id__in=to_delete).delete()

        # Ajout en masse (Bulk create) des nouvelles relations cochées
        new_relations = [
            RoleDelegatePermissions(role_id=self.instance.pk, delegate_perm_id=perm_id)
            for perm_id in to_add
        ]
        if new_relations:
            RoleDelegatePermissions.objects.bulk_create(new_relations)


# ==============================================================================
# INTERFACE D'ADMINISTRATION
# ==============================================================================
@admin.register(RoleDelegate)
class RoleDelegateAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour les Délégations.

    Cette vue restreint l'accès en lecture seule pour les informations du rôle d'origine
    et fournit une interface pour sélectionner/désélectionner ses permissions déléguées.
    """

    form = RoleDelegateAdminForm

    list_display = ('id', 'get_translated_name', 'company', 'is_active')
    list_display_links = ('id', 'get_translated_name')

    readonly_fields = ('get_translated_name', 'get_translated_description', 'company', 'is_active')

    fieldsets = (
        (_("Informations du Rôle (Lecture Seule)"), {
            'fields': ('get_translated_name', 'get_translated_description', 'company', 'is_active'),
        }),
        (_("Permissions associées à ce rôle"), {
            'fields': ('delegate_permissions',),
        }),
    )

    def get_queryset(self, request):
        """
        Filtre la liste principale pour n'afficher que les rôles qui possèdent
        au moins une permission de catégorie DELEGATE (via access_rolepermissions)
        """
        qs = super().get_queryset(request)
        return qs.filter(permissions__category='DELEGATE').distinct()

    @admin.display(description=_("Nom"))
    def get_translated_name(self, obj):
        """Récupère le nom traduit de manière sécurisée (fallback sur la langue disponible)."""
        try:
            return obj.safe_translation_getter('name', any_language=True)
        except Exception:
            return str(obj)

    @admin.display(description=_("Description"))
    def get_translated_description(self, obj):
        """Récupère la description traduite de manière sécurisée (fallback sur la langue disponible)."""

        try:
            return obj.safe_translation_getter('description', any_language=True)
        except Exception:
            return "-"

    def has_add_permission(self, request):
        """Désactive l'affichage du bouton d'ajout et la création d'instances."""
        return False


    def changelist_view(self, request, extra_context=None):
        """
        Injecte un message d'information personnalisé sous le titre principal.
        """
        extra_context = extra_context or {}
        extra_context['subtitle'] = _("List of roles with at least one DELEGATE category permission")
        return super().changelist_view(request, extra_context=extra_context)


    def save_related(self, request, form, formsets, change):
        """
        Sécurité pour forcer la synchronisation de la table intermédiaire lors d'une
        sauvegarde via les mécanismes internes de l'admin Django.
        """
        super().save_related(request, form, formsets, change)
        form.save_delegate_permissions()
