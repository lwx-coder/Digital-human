from rest_framework import serializers
from .models import Permission, Role, UserRole
from django.contrib.auth import get_user_model

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'description']


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        write_only=True,
        many=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'description', 'permissions', 'permission_ids']
    
    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        role.permissions.set(permission_ids)
        return role
    
    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        instance = super().update(instance, validated_data)
        if permission_ids is not None:
            instance.permissions.set(permission_ids)
        return instance


class UserRoleSerializer(serializers.ModelSerializer):
    """用户角色关联序列化器"""
    role_detail = RoleSerializer(source='role', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['id', 'user', 'role', 'role_detail', 'username']


class UserWithRolesSerializer(serializers.ModelSerializer):
    """带有角色信息的用户序列化器"""
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'is_active', 'roles']
    
    def get_roles(self, obj):
        user_roles = UserRole.objects.filter(user=obj)
        return RoleSerializer([ur.role for ur in user_roles], many=True).data 