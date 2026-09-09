from django import forms
from django.contrib import admin
from django.db import transaction
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _

from src.access.models import Role, Permission, RolePermissions


class RoleAdminForm(TranslatableModelForm):
    form_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name=_('Permissions'), is_stacked=False),
        label=_("Permissions assignées")
    )

    class Meta:
        model = Role
        fields = ['name', 'description', 'slug', 'company', 'is_active', 'form_permissions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On pré-remplit uniquement si le rôle existe déjà.
        # Si c'est une création (pas de pk), le widget restera simplement vide et prêt à l'emploi.
        if self.instance and self.instance.pk:
            self.fields['form_permissions'].initial = RolePermissions.objects.filter(
                role=self.instance
            ).values_list('permission_id', flat=True)


@admin.register(Role)
class RoleAdmin(TranslatableAdmin):
    form = RoleAdminForm
    list_display = ('id', 'name', 'company', 'is_active')
    search_fields = ('slug', 'translations__name', 'company__name')

    # Fieldset pour la création et la modification
    fieldsets = (
        ("Champs Traduisibles (Multilingue)", {
            'fields': ('name', 'description'),
        }),
        ("Autres champs", {
            'fields': ('slug', 'company', 'is_active'),
        }),
        ("Permissions associées à ce rôle", {
            'fields': ('form_permissions',),
        }),
    )

    # Solution officielle django-parler pour le prepopulated slug
    def get_prepopulated_fields(self, request, obj=None):
        # Ne pas utiliser l'attribut de classe standard, mais retourner le dictionnaire ici.
        # Cela injectera le JavaScript nécessaire de manière transparente dans l'Admin.
        return {
            'slug': ('name',)
        }

    # Sauvegarde Role et permissions, en 1 transaction
    @transaction.atomic
    def save_model(self, request, obj, form, change):
        # Sauvegarde le rôle et génère ou récupère l'ID
        super().save_model(request, obj, form, change)

        # L'ID du rôle existe désormais dans 'obj', on peut lier les permissions
        if 'form_permissions' in form.cleaned_data:
            selected_perms = form.cleaned_data['form_permissions']
            new_perms_ids = set(p.id for p in selected_perms)

            # Récupère l'existant (sera un set vide lors d'une création)
            current_perms_ids = set(
                RolePermissions.objects.filter(role=obj).values_list('permission_id', flat=True)
            )

            # Supprime ce qui a été décoché (ne fait rien lors d'une création puisque RolePermissions sera vide)
            RolePermissions.objects.filter(
                role=obj,
                permission_id__in=current_perms_ids - new_perms_ids
            ).delete()

            # Enregistre en masse les nouvelles associations
            to_create = [
                RolePermissions(role=obj, permission_id=p_id)
                for p_id in (new_perms_ids - current_perms_ids)
            ]
            RolePermissions.objects.bulk_create(to_create)

    class Media:
        js = ('/admin/jsi18n/',)
