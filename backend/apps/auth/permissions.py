from functools import wraps
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .models import UserRole


def has_permission(codename):
    """
    检查用户是否拥有指定权限的装饰器
    
    用法示例:
    @has_permission('can_view_reports')
    def my_view(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 如果未启用RBAC，则允许所有已认证用户访问
            if not settings.ENABLE_RBAC:
                return view_func(request, *args, **kwargs)
            
            user = request.user
            
            # 管理员拥有所有权限
            if user.is_staff or user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # 检查用户是否拥有指定权限
            user_roles = UserRole.objects.filter(user=user)
            for user_role in user_roles:
                if user_role.role.permissions.filter(codename=codename).exists():
                    return view_func(request, *args, **kwargs)
            
            # 用户没有权限
            return Response(
                {'detail': '您没有执行此操作的权限'},
                status=status.HTTP_403_FORBIDDEN
            )
        return _wrapped_view
    return decorator


class RBACPermission:
    """
    RBAC权限类，用于DRF权限检查
    
    用法示例:
    permission_classes = [RBACPermission('can_view_reports')]
    """
    def __init__(self, codename):
        self.codename = codename
    
    def has_permission(self, request, view):
        # 如果未启用RBAC，则允许所有已认证用户访问
        if not settings.ENABLE_RBAC:
            return True
        
        user = request.user
        
        # 未认证用户没有权限
        if not user or not user.is_authenticated:
            return False
        
        # 管理员拥有所有权限
        if user.is_staff or user.is_superuser:
            return True
        
        # 检查用户是否拥有指定权限
        user_roles = UserRole.objects.filter(user=user)
        for user_role in user_roles:
            if user_role.role.permissions.filter(codename=self.codename).exists():
                return True
        
        return False 