from django import forms
from django.contrib.auth.models import Group, Permission
from applications.security.models import Menu, Module, GroupModulePermission

class GroupModulePermissionForm(forms.ModelForm):
    menus = forms.ModelMultipleChoiceField(
        queryset=Menu.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'id': 'id_menus'}),
        required=False,
        label='Menús'
    )
    modules = forms.ModelMultipleChoiceField(
        queryset=Module.objects.all(),  # Cargar todos de entrada
        widget=forms.CheckboxSelectMultiple(attrs={'id': 'id_modules'}),
        required=True,
        label='Módulos'
    )
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'id': 'id_permissions'}),
        required=True,
        label='Permisos'
    )

    class Meta:
        model = GroupModulePermission
        fields = ['group', 'modules', 'permissions']

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['group'].queryset = Group.objects.all()