from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'rbac'

router = DefaultRouter()
router.register('permissions', views.PermissionViewSet, basename='permissions')
router.register('roles', views.RoleViewSet, basename='roles')
router.register('user-roles', views.UserRoleViewSet, basename='user-roles')
router.register('user-permissions', views.UserPermissionViewSet, basename='user-permissions')

urlpatterns = [
    # 在这里添加其他URL
]

urlpatterns += router.urls

