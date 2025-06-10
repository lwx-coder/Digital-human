from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'users'

router = DefaultRouter()
router.register('', views.UserViewSet, basename='users')

urlpatterns = [
    # 用户认证相关路由
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('phone-login/', views.PhoneLoginView.as_view(), name='phone-login'),
    path('send-phone-code/', views.SendPhoneCodeView.as_view(), name='send-phone-code'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('reset-password-request/', views.ResetPasswordRequestView.as_view(), name='reset-password-request'),
    path('reset-password-confirm/', views.ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
    path('info/', views.UserInfoView.as_view(), name='user-info'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('upload_avatar/', views.UploadAvatarView.as_view(), name='upload-avatar'),
]

urlpatterns += router.urls
