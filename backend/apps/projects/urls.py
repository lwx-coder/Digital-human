from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # 首页
    path('', views.index, name='index'),
    
    # 用户认证相关页面
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-reset-confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
    
    # 用户中心
    path('profile/', views.profile_view, name='profile'),
    
    # API测试页面
    path('api-test/', views.api_test_view, name='api_test'),
    
    # 权限管理测试页面
    path('rbac-test/', views.rbac_test_view, name='rbac_test'),
]
