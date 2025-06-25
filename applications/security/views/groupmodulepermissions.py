from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from applications.security.models import GroupModulePermission
from applications.security.forms.groupmodulepermission import GroupModulePermissionForm
from applications.security.components.mixin_crud import PermissionMixin, CreateViewMixin, UpdateViewMixin, DeleteViewMixin, ListViewMixin

class GroupModulePermissionListView(PermissionMixin, ListViewMixin, ListView):
    model = GroupModulePermission
    template_name = 'security/groupmodulepermission/list.html'
    context_object_name = 'groupmodulepermissions'
    permission_required = 'view_groupmodulepermission'
    

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        queryset = self.model.objects.all()
        if q:
            queryset = queryset.filter(
                Q(group_name_icontains=q) |
                Q(module_name_icontains=q)
            )
        return queryset.order_by('group_name', 'module_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('security:groupmodulepermission_create')
        return context

class GroupModulePermissionCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = GroupModulePermission
    form_class = GroupModulePermissionForm
    template_name = 'security/groupmodulepermission/form.html'
    success_url = reverse_lazy('security:groupmodulepermission_list')
    permission_required = 'add_groupmodulepermission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']

        # IDs de permisos seleccionados para inicializar checkboxes
        if form.initial.get('permissions'):
            context['selected_permissions'] = list(form.initial['permissions'].values_list('id', flat=True))
        else:
            context['selected_permissions'] = []

        # Para facilitar el manejo de permisos por módulo en JS, pasamos un diccionario {module_id: [{id, name}, ...]}
        modules = form.fields['modules'].queryset
        module_permissions = {}
        for module in modules:
            perms = list(module.permissions.values('id', 'name'))
            module_permissions[str(module.id)] = perms
        context['module_permissions_json'] = module_permissions

        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        obj = self.object
        obj.permissions.set(form.cleaned_data['permissions'])
        messages.success(self.request, f"Permisos asignados correctamente al grupo {obj.group.name} sobre el módulo {obj.module.name}.")
        return response

class GroupModulePermissionUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = GroupModulePermission
    form_class = GroupModulePermissionForm
    template_name = 'security/groupmodulepermission/form.html'
    success_url = reverse_lazy('security:groupmodulepermission_list')
    permission_required = 'change_groupmodulepermission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']

        # Pasar permisos seleccionados para checkboxes en update
        if self.object.permissions.exists():
            context['selected_permissions'] = list(self.object.permissions.values_list('id', flat=True))
        else:
            context['selected_permissions'] = []

        # Pasar permisos por módulo para JS
        modules = form.fields['modules'].queryset
        module_permissions = {}
        for module in modules:
            perms = list(module.permissions.values('id', 'name'))
            module_permissions[str(module.id)] = perms
        context['module_permissions_json'] = module_permissions

        context['grabar'] = 'Actualizar Permisos por Grupo y Módulo'
        context['back_url'] = self.success_url

        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.permissions.set(form.cleaned_data['permissions'])
        messages.success(self.request, f"Permisos para grupo '{self.object.group.name}' y módulo '{self.object.module.name}' actualizados con éxito.")
        return response



class GroupModulePermissionDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = GroupModulePermission
    template_name = 'core/delete.html'
    success_url = reverse_lazy('security:groupmodulepermission_list')
    permission_required = 'delete_groupmodulepermission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Permisos por Grupo y Módulo'
        context['description'] = f"¿Desea eliminar los permisos para el grupo '{self.object.group.name}' y el módulo '{self.object.module.name}'?"
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        group = self.object.group.name
        module = self.object.module.name
        response = super().form_valid(form)
        messages.success(self.request, f"Permisos para grupo '{group}' y módulo '{module}' eliminados con éxito.")
        return response