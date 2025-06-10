from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Role


class RoleAdmin(admin.ModelAdmin):
    """角色管理界面"""
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)


class CustomUserAdmin(UserAdmin):
    """自定义用户管理界面"""
    list_display = ('username', 'email', 'phone', 'first_name', 'last_name', 'is_staff', 'get_roles')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'roles')
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'avatar', 'bio', 'birth_date')}),
        (_('角色'), {'fields': ('roles',)}),
        (_('权限'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('重要日期'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    def get_roles(self, obj):
        return ', '.join(obj.get_roles())
    get_roles.short_description = '角色'


admin.site.register(Role, RoleAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
