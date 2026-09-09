import copy
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from src.core.admin import admin_audit_register
from src.users.models.user import User
from src.users.models.user_hierarchy import UserHierarchy
from src.users.models.user_role import UserRole
from src.users.models.user_role_log import UserRoleLog

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Liste les colonnes à afficher dans le tableau récapitulatif
    list_display = ("username", "email", "first_name", "last_name", "is_owner", "is_active")
    list_filter = ("is_owner", "is_active", "is_staff", "is_superuser")

    # Ajout d'une barre de recherche
    search_fields = ("email", "username", "first_name", "last_name")

    # Rendre les champs d'audit non modifiables dans le formulaire
    readonly_fields = ('date_joined', 'created_by', 'update_at', 'updated_by')

    # Désactiver les filtres horizontaux natifs des groupes/permissions qui n'existent plus
    filter_horizontal = ()

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)

        # Copie profonde de la configuration native de Django pour la modifier et réordonner
        base_fieldsets = copy.deepcopy(DjangoUserAdmin.fieldsets)
        new_fieldsets = []

        # Liste des champs inexistants ou déplacés à supprimer
        fields_to_remove = {"date_joined", "groups", "user_permissions"}

        # Parcours et nettoyage de chaque section d'origine
        for section_title, section_options in base_fieldsets:
            fields = [
                f
                for f in section_options.get("fields", [])
                if f not in fields_to_remove
            ]
            if fields:
                # On reconstruit temporairement l'option sous forme de dictionnaire modifiable
                # pour pouvoir ajouter nos sections custom
                new_options = dict(section_options)
                new_options["fields"] = list(fields)
                new_fieldsets.append((section_title, new_options))

        # Injection de 'photo' et 'is_owner' dans les sections natives de Django
        for section_title, section_options in new_fieldsets:
            # Déplacement de la photo dans les infos personnelles
            if section_title == _("Personal info"):
                section_options["fields"].append("photo")

            # Déplacement du statut de propriétaire dans les permissions
            elif section_title == _("Permissions"):
                section_options["fields"].append("is_owner")

        # Reconversion des listes de champs en tuples (format requis par Django)
        final_base_fieldsets = []
        for section_title, section_options in new_fieldsets:
            section_options['fields'] = tuple(section_options['fields'])
            final_base_fieldsets.append((section_title, section_options))

        # Assemblage final avec les nouveaux champs et la section d'audit
        self.fieldsets = tuple(new_fieldsets) + (
            ( _("Preferences"), {
                "fields": ( "preferred_language", "preferred_home_page", "preferred_company", ),
            }),
            ( _("Audit Logs"), {
                "classes": ("collapse", ),  # Bloc replié par défaut pour plus de clarté
                "fields": ("created_by", "date_joined", "updated_by", "update_at"),
            }),
        )

@admin_audit_register(UserHierarchy, TreeAdmin)
class UserHierarchyAdmin(TreeAdmin):
    form = movenodeform_factory(UserHierarchy)
    list_display = ("user", "path", "depth", "numchild")
    search_fields = ("user__email", "user__username", "user__first_name", "user__last_name")
    ordering = ('path',)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role', 'company', 'location', 'is_active')
    list_filter = ('is_active', 'role_id', 'company_id', 'location_id')
    search_fields = ('user_id', 'role_id')


@admin.register(UserRoleLog)
class UserRoleLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'user_role', 'action', 'changed_at', 'changed_by')
    list_filter = ('action', 'changed_at')
    search_fields = ('uuid', 'userrole', 'user')
    readonly_fields = ('changed_at',)