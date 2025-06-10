from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import Permission, Role, UserRole
from .serializers import (
    PermissionSerializer, 
    RoleSerializer, 
    UserRoleSerializer,
    UserWithRolesSerializer
)

User = get_user_model()


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    只允许管理员进行修改操作，其他用户只能查看
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class RBACPermissionMixin:
    """
    RBAC权限控制混入类
    """
    def get_permissions(self):
        if not settings.ENABLE_RBAC:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()


class PermissionViewSet(RBACPermissionMixin, viewsets.ModelViewSet):
    """
    权限视图集
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminOrReadOnly]


class RoleViewSet(RBACPermissionMixin, viewsets.ModelViewSet):
    """
    角色视图集
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """获取拥有该角色的用户列表"""
        role = self.get_object()
        user_roles = UserRole.objects.filter(role=role)
        users = [ur.user for ur in user_roles]
        serializer = UserWithRolesSerializer(users, many=True)
        return Response(serializer.data)


class UserRoleViewSet(RBACPermissionMixin, viewsets.ModelViewSet):
    """
    用户角色关联视图集
    """
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def create(self, request, *args, **kwargs):
        # 检查是否已存在相同的用户角色关联
        user_id = request.data.get('user')
        role_id = request.data.get('role')
        if UserRole.objects.filter(user_id=user_id, role_id=role_id).exists():
            return Response(
                {'detail': '该用户已拥有此角色'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def batch_assign(self, request):
        """批量分配角色给用户"""
        user_ids = request.data.get('user_ids', [])
        role_id = request.data.get('role_id')
        
        if not role_id:
            return Response(
                {'detail': '请提供角色ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response(
                {'detail': '角色不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        created_count = 0
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                if not UserRole.objects.filter(user=user, role=role).exists():
                    UserRole.objects.create(user=user, role=role)
                    created_count += 1
            except User.DoesNotExist:
                pass
        
        return Response({
            'detail': f'成功为{created_count}个用户分配角色',
            'created_count': created_count
        })
    
    @action(detail=False, methods=['post'])
    def batch_remove(self, request):
        """批量移除用户的角色"""
        user_ids = request.data.get('user_ids', [])
        role_id = request.data.get('role_id')
        
        if not role_id:
            return Response(
                {'detail': '请提供角色ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count = UserRole.objects.filter(
            user_id__in=user_ids,
            role_id=role_id
        ).delete()[0]
        
        return Response({
            'detail': f'成功移除{deleted_count}个用户的角色',
            'deleted_count': deleted_count
        })


class UserPermissionViewSet(RBACPermissionMixin, viewsets.ViewSet):
    """
    用户权限视图集
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_roles(self, request):
        """获取当前用户的角色列表"""
        user = request.user
        user_roles = UserRole.objects.filter(user=user)
        roles = [ur.role for ur in user_roles]
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_permissions(self, request):
        """获取当前用户的权限列表"""
        user = request.user
        user_roles = UserRole.objects.filter(user=user)
        roles = [ur.role for ur in user_roles]
        
        # 收集所有角色的权限
        permissions_set = set()
        for role in roles:
            for perm in role.permissions.all():
                permissions_set.add(perm)
        
        serializer = PermissionSerializer(list(permissions_set), many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def check_permission(self, request):
        """检查当前用户是否拥有指定权限"""
        if not settings.ENABLE_RBAC:
            return Response({'has_permission': True})
            
        codename = request.data.get('codename')
        if not codename:
            return Response(
                {'detail': '请提供权限代码'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        
        # 管理员拥有所有权限
        if user.is_staff or user.is_superuser:
            return Response({'has_permission': True})
        
        user_roles = UserRole.objects.filter(user=user)
        roles = [ur.role for ur in user_roles]
        
        for role in roles:
            if role.permissions.filter(codename=codename).exists():
                return Response({'has_permission': True})
        
        return Response({'has_permission': False})
