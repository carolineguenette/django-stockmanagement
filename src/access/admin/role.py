from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _

from src.access.models import Role, Permission, RolePermissions


class RoleAdminForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Permissions'),
            is_stacked=False
        ),
        label=_("Permissions assignées")
    )

    class Meta:
        model = Role
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            initial_perms = RolePermissions.objects.filter(role=self.instance).values_list('permission_id', flat=True)
            self.fields['permissions'].initial = initial_perms

    def save(self, commit=True):
        role = super().save(commit=commit)
        if commit:
            self.save_permissions()
        return role

    def save_permissions(self):
        selected_perms = self.cleaned_data.get('permissions', [])
        current_perms = set(RolePermissions.objects.filter(role=self.instance).values_list('permission_id', flat=True))
        new_perms = set(p.id for p in selected_perms)

        RolePermissions.objects.filter(role=self.instance, permission_id__in=current_perms - new_perms).delete()

        to_create = [
            RolePermissions(role=self.instance, permission_id=p_id)
            for p_id in (new_perms - current_perms)
        ]
        RolePermissions.objects.bulk_create(to_create)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    form = RoleAdminForm
    list_display = ('slug', 'company', 'is_active')
    search_fields = ('slug', 'company__name')
    inlines = []

    class Media:
        js = ('/admin/jsi18n/',)
