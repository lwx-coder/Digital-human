from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    LoginSerializer,
    PhoneLoginSerializer,
    ResetPasswordRequestSerializer,
    ResetPasswordConfirmSerializer,
    CustomUserSimpleSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    用户视图集，提供用户的CRUD操作
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """获取当前用户信息"""
        user = request.user
        serializer = self.get_serializer(user)
        user_data = serializer.data
        
        # 构建完整的头像URL
        if user.avatar and 'avatar' in user_data:
            avatar_url = user.avatar.url
            if not avatar_url.startswith(('http://', 'https://')):
                # 获取当前请求的域名
                protocol = 'https' if request.is_secure() else 'http'
                domain = request.get_host()
                user_data['avatar'] = f"{protocol}://{domain}{avatar_url}"
        
        return Response(user_data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def update_me(self, request):
        """更新当前用户信息"""
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        user_data = serializer.data
        
        # 构建完整的头像URL
        if user.avatar and 'avatar' in user_data:
            avatar_url = user.avatar.url
            if not avatar_url.startswith(('http://', 'https://')):
                # 获取当前请求的域名
                protocol = 'https' if request.is_secure() else 'http'
                domain = request.get_host()
                user_data['avatar'] = f"{protocol}://{domain}{avatar_url}"
        
        return Response(user_data)


class LoginView(APIView):
    """用户名密码登录视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            print(f"登录校验失败: {serializer.errors}")
            raise e
        user = serializer.validated_data['user']
        refresh = serializer.validated_data['refresh']
        access = serializer.validated_data['access']
        
        user_data = UserSerializer(user).data
        
        # 构建完整的头像URL
        if user.avatar and 'avatar' in user_data:
            avatar_url = user.avatar.url
            if not avatar_url.startswith(('http://', 'https://')):
                # 获取当前请求的域名
                protocol = 'https' if request.is_secure() else 'http'
                domain = request.get_host()
                user_data['avatar'] = f"{protocol}://{domain}{avatar_url}"
        
        return Response({
            'user': user_data,
            'roles': user.get_roles(),  # 明确返回角色信息
            'refresh': refresh,
            'access': access
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """退出登录视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # 简化退出登录逻辑，不再依赖token黑名单
        try:
            refresh_token = request.data.get('refresh', None)
            if refresh_token:
                # 尝试使token失效，但不强制要求成功
                try:
                    token = RefreshToken(refresh_token)
                    # 如果配置了黑名单，则加入黑名单
                    token.blacklist()
                except (TokenError, AttributeError):
                    # 忽略token错误或黑名单未配置的情况
                    pass
        except Exception:
            # 捕获所有异常，确保退出登录总是成功
            pass
                
        return Response({'message': '退出登录成功'}, status=status.HTTP_200_OK)


class PhoneLoginView(APIView):
    """手机号验证码登录视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PhoneLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = serializer.validated_data['refresh']
        access = serializer.validated_data['access']
        
        user_data = UserSerializer(user).data
        
        # 构建完整的头像URL
        if user.avatar and 'avatar' in user_data:
            avatar_url = user.avatar.url
            if not avatar_url.startswith(('http://', 'https://')):
                # 获取当前请求的域名
                protocol = 'https' if request.is_secure() else 'http'
                domain = request.get_host()
                user_data['avatar'] = f"{protocol}://{domain}{avatar_url}"
        
        return Response({
            'user': user_data,
            'roles': user.get_roles(),  # 明确返回角色信息
            'refresh': refresh,
            'access': access
        }, status=status.HTTP_200_OK)


class UserInfoView(APIView):
    """获取用户信息视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # 构建完整的头像URL
        avatar_url = ''
        if user.avatar:
            avatar_url = user.avatar.url
            if not avatar_url.startswith(('http://', 'https://')):
                # 获取当前请求的域名
                protocol = 'https' if request.is_secure() else 'http'
                domain = request.get_host()
                avatar_url = f"{protocol}://{domain}{avatar_url}"
        
        return Response({
            'name': user.username,
            'avatar': avatar_url,
            'roles': user.get_roles(),  # 返回角色信息
            'introduction': user.bio or '',
            'email': user.email,
            'phone': user.phone,
        })


class ChangePasswordView(APIView):
    """修改密码视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({'detail': '请提供旧密码和新密码'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证旧密码
        user = request.user
        if not user.check_password(old_password):
            return Response({'detail': '当前密码不正确'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 设置新密码
        user.set_password(new_password)
        user.save()
        
        return Response({'detail': '密码修改成功'}, status=status.HTTP_200_OK)


class UploadAvatarView(APIView):
    """用户头像上传视图"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        if 'avatar' not in request.FILES:
            return Response({'error': '请提供头像图片'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user.avatar = request.FILES['avatar']
        user.save()
        
        # 构建完整的头像URL
        avatar_url = user.avatar.url
        if not avatar_url.startswith(('http://', 'https://')):
            # 获取当前请求的域名
            protocol = 'https' if request.is_secure() else 'http'
            domain = request.get_host()
            avatar_url = f"{protocol}://{domain}{avatar_url}"
        
        # 返回头像的URL
        return Response({
            'success': True,
            'avatar_url': avatar_url,
            'message': '头像上传成功'
        }, status=status.HTTP_200_OK)


class SendPhoneCodeView(APIView):
    """发送手机验证码视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response({'error': '请提供手机号'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否有用户使用此手机号
        try:
            User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({'error': '该手机号未注册'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 这里不实际发送验证码，固定为123456
        return Response({'message': '验证码发送成功'}, status=status.HTTP_200_OK)


class ResetPasswordRequestView(APIView):
    """请求重置密码视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            serializer = ResetPasswordRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            print(f"请求重置密码校验失败: {serializer.errors}")
            raise e
        # 这里不实际发送验证码，固定为123456
        return Response({'message': '验证码已发送到您的邮箱'}, status=status.HTTP_200_OK)


class ResetPasswordConfirmView(APIView):
    """确认重置密码视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            serializer = ResetPasswordConfirmSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            print(f"确认重置密码校验失败: {serializer.errors}")
            return Response({'error': str(e) if isinstance(e, str) else e.detail if hasattr(e, 'detail') else '验证失败'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        new_password = serializer.validated_data['new_password']
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': '密码重置成功'}, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """用户注册视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # 生成JWT令牌
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        user_data = UserSerializer(user).data
        
        # 构建完整的头像URL
        if user.avatar and 'avatar' in user_data:
            avatar_url = user.avatar.url
            if not avatar_url.startswith(('http://', 'https://')):
                # 获取当前请求的域名
                protocol = 'https' if request.is_secure() else 'http'
                domain = request.get_host()
                user_data['avatar'] = f"{protocol}://{domain}{avatar_url}"
        
        return Response({
            'user': user_data,
            'roles': user.get_roles(),  # 添加角色信息
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)
