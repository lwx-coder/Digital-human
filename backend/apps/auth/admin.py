from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Permission, Role, UserRole


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'description')
    search_fields = ('name', 'codename')
    list_filter = ('roles',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'get_permissions')
    search_fields = ('name', 'code')
    filter_horizontal = ('permissions',)
    
    def get_permissions(self, obj):
        return ", ".join([p.name for p in obj.permissions.all()[:5]])
    get_permissions.short_description = _('权限')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username', 'role__name')
    list_filter = ('role',)
    autocomplete_fields = ('user', 'role')
