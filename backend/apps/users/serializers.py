from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Role

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    
    class Meta:
        model = User.roles.field.model
        fields = ('name',)


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'address', 'first_name', 'last_name', 'avatar', 'bio', 'birth_date', 'roles')
        read_only_fields = ('id',)

    def get_roles(self, obj):
        return obj.get_roles()


class CustomUserSimpleSerializer(serializers.ModelSerializer):
    """简化的用户信息序列化器，用于在其他模型中引用用户信息"""
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'avatar', 'roles')
        read_only_fields = ('id',)
    
    def get_roles(self, obj):
        return obj.get_roles()


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'required': True},
            'phone': {'required': False},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password": "两次密码输入不一致"})
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data.get('phone', ''),
            password=validated_data['password']
        )
        
        # 添加默认旅客角色
        role, _ = Role.objects.get_or_create(name='passenger')
        user.roles.add(role)
        
        return user


class LoginSerializer(serializers.Serializer):
    """用户名密码登录序列化器"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username or not password:
            raise serializers.ValidationError({"error": "请提供用户名和密码"})
        
        # 尝试使用用户名登录
        user = authenticate(username=username, password=password)
        
        # 如果用户名登录失败，尝试使用邮箱登录
        if not user:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if not user:
            raise serializers.ValidationError({"error": "用户名或密码错误"})
        
        if not user.is_active:
            raise serializers.ValidationError({"error": "用户账号已被禁用"})
        
        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class PhoneLoginSerializer(serializers.Serializer):
    """手机号验证码登录序列化器"""
    phone = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        code = attrs.get('code')
        
        if not phone or not code:
            raise serializers.ValidationError({"error": "请提供手机号和验证码"})
        
        # 验证码固定为123456
        if code != '123456':
            raise serializers.ValidationError({"error": "验证码错误"})
        
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "该手机号未注册"})
        
        if not user.is_active:
            raise serializers.ValidationError({"error": "用户账号已被禁用"})
        
        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class ResetPasswordRequestSerializer(serializers.Serializer):
    """重置密码请求序列化器"""
    email = serializers.CharField(required=True)
    
    def validate_email(self, value):
        # 简单的邮箱格式验证
        if '@' not in value or '.' not in value:
            raise serializers.ValidationError("邮箱格式不正确")
            
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("该邮箱未注册")
        return value


class ResetPasswordConfirmSerializer(serializers.Serializer):
    """重置密码确认序列化器"""
    email = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        # 简单的邮箱格式验证
        if '@' not in email or '.' not in email:
            raise serializers.ValidationError({"error": "邮箱格式不正确"})
        
        # 验证码固定为123456
        if code != '123456':
            raise serializers.ValidationError({"error": "验证码错误"})
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError({"error": "两次密码输入不一致"})
        
        try:
            user = User.objects.get(email=email)
            attrs['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "该邮箱未注册"})
        
        return attrs 