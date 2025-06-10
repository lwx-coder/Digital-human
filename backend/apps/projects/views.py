from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import requests
import json
from django.conf import settings
from django.urls import reverse

from apps.users.models import CustomUser


def index(request):
    """首页视图"""
    return render(request, 'projects/index.html')


def login_view(request):
    """登录视图"""
    if request.method == 'POST':
        login_type = request.POST.get('login_type', 'password')
        
        if login_type == 'password':
            # 账号密码登录
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            # 通过API接口进行登录
            try:
                response = requests.post(
                    request.build_absolute_uri('/api/users/login/'),
                    json={'username': username, 'password': password}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # 使用Django的认证系统进行登录
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        login(request, user)
                        messages.success(request, '登录成功！')
                        # 将token存储在会话中，以便后续API请求使用
                        request.session['access_token'] = data.get('access')
                        request.session['refresh_token'] = data.get('refresh')
                        return redirect('projects:index')
                else:
                    error_msg = response.json().get('error', '用户名或密码错误！')
                    messages.error(request, error_msg)
            except Exception as e:
                messages.error(request, f'登录失败：{str(e)}')
        
        elif login_type == 'phone':
            # 手机验证码登录
            phone = request.POST.get('phone')
            code = request.POST.get('code')
            
            # 通过API接口进行手机验证码登录
            try:
                response = requests.post(
                    request.build_absolute_uri('/api/users/phone-login/'),
                    json={'phone': phone, 'code': code}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # 获取用户信息
                    user_response = requests.get(
                        request.build_absolute_uri('/api/users/me/'),
                        headers={'Authorization': f'Bearer {data.get("access")}'}
                    )
                    
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        # 使用Django的认证系统进行登录
                        user = CustomUser.objects.get(phone=phone)
                        login(request, user)
                        messages.success(request, '登录成功！')
                        # 将token存储在会话中，以便后续API请求使用
                        request.session['access_token'] = data.get('access')
                        request.session['refresh_token'] = data.get('refresh')
                        return redirect('projects:index')
                else:
                    error_msg = response.json().get('error', '手机号或验证码错误！')
                    messages.error(request, error_msg)
            except Exception as e:
                messages.error(request, f'登录失败：{str(e)}')
    
    return render(request, 'projects/login.html')


def register_view(request):
    """注册视图"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # 通过API接口进行注册
        try:
            response = requests.post(
                request.build_absolute_uri('/api/users/register/'),
                json={
                    'username': username,
                    'email': email,
                    'phone': phone,
                    'password': password,
                    'password_confirm': password_confirm
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                # 使用Django的认证系统进行登录
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, '注册成功！')
                    # 将token存储在会话中，以便后续API请求使用
                    request.session['access_token'] = data.get('access')
                    request.session['refresh_token'] = data.get('refresh')
                    return redirect('projects:index')
            else:
                errors = response.json()
                for field, error_list in errors.items():
                    if isinstance(error_list, list):
                        for error in error_list:
                            messages.error(request, f"{field}: {error}")
                    else:
                        messages.error(request, f"{field}: {error_list}")
        except Exception as e:
            messages.error(request, f'注册失败：{str(e)}')
    
    return render(request, 'projects/register.html')


def logout_view(request):
    """登出视图"""
    logout(request)
    # 清除会话中的token
    if 'access_token' in request.session:
        del request.session['access_token']
    if 'refresh_token' in request.session:
        del request.session['refresh_token']
    messages.success(request, '您已成功退出登录！')
    return redirect('projects:login')


def password_reset_view(request):
    """密码重置请求视图"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # 通过API接口请求重置密码
        try:
            response = requests.post(
                request.build_absolute_uri('/api/users/reset-password-request/'),
                json={'email': email}
            )
            
            if response.status_code == 200:
                messages.success(request, '重置密码邮件已发送，请查收！')
                return redirect('projects:password_reset_confirm')
            else:
                error_msg = response.json().get('error', '该邮箱未注册！')
                messages.error(request, error_msg)
        except Exception as e:
            messages.error(request, f'请求失败：{str(e)}')
    
    return render(request, 'projects/password_reset.html')


def password_reset_confirm_view(request):
    """密码重置确认视图"""
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        new_password_confirm = request.POST.get('new_password_confirm')
        
        # 通过API接口确认重置密码
        try:
            response = requests.post(
                request.build_absolute_uri('/api/users/reset-password-confirm/'),
                json={
                    'email': email,
                    'code': code,
                    'new_password': new_password,
                    'new_password_confirm': new_password_confirm
                }
            )
            
            if response.status_code == 200:
                messages.success(request, '密码重置成功，请使用新密码登录！')
                return redirect('projects:login')
            else:
                errors = response.json()
                for field, error_list in errors.items():
                    if isinstance(error_list, list):
                        for error in error_list:
                            messages.error(request, f"{field}: {error}")
                    else:
                        messages.error(request, f"{field}: {error_list}")
        except Exception as e:
            messages.error(request, f'请求失败：{str(e)}')
    
    return render(request, 'projects/password_reset_confirm.html')


@login_required
def profile_view(request):
    """用户中心视图"""
    if request.method == 'POST':
        # 获取表单数据
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        bio = request.POST.get('bio', '')
        
        # 准备请求数据
        data = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'address': address,
            'bio': bio
        }
        
        # 通过API接口更新用户信息
        try:
            headers = {'Authorization': f'Bearer {request.session.get("access_token", "")}'}
            response = requests.put(
                request.build_absolute_uri('/api/users/update_me/'),
                json=data,
                headers=headers
            )
            
            if response.status_code == 200:
                # 更新本地用户对象
                user = request.user
                user.first_name = first_name
                user.last_name = last_name
                user.phone = phone
                user.address = address
                user.bio = bio
                
                # 处理头像上传
                if 'avatar' in request.FILES:
                    # 头像上传需要单独处理，因为需要使用multipart/form-data
                    files = {'avatar': request.FILES['avatar']}
                    avatar_response = requests.put(
                        request.build_absolute_uri('/api/users/update_me/'),
                        files=files,
                        headers=headers
                    )
                    if avatar_response.status_code == 200:
                        # 更新成功后，需要刷新用户对象
                        user = CustomUser.objects.get(pk=user.pk)
                
                messages.success(request, '个人信息更新成功！')
            else:
                errors = response.json()
                for field, error_list in errors.items():
                    if isinstance(error_list, list):
                        for error in error_list:
                            messages.error(request, f"{field}: {error}")
                    else:
                        messages.error(request, f"{field}: {error_list}")
        except Exception as e:
            messages.error(request, f'更新失败：{str(e)}')
    
    return render(request, 'projects/profile.html')


@login_required
def api_test_view(request):
    """API测试页面视图"""
    # 获取API基础URL
    base_url = request.build_absolute_uri('/api/')
    
    # 获取当前用户信息
    user_info = {
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'phone': request.user.phone,
    }
    
    # 获取可用的API端点
    api_endpoints = [
        {'name': '用户注册', 'url': 'users/register/', 'method': 'POST'},
        {'name': '用户登录', 'url': 'users/login/', 'method': 'POST'},
        {'name': '手机验证码登录', 'url': 'users/phone-login/', 'method': 'POST'},
        {'name': '发送手机验证码', 'url': 'users/send-phone-code/', 'method': 'POST'},
        {'name': '请求重置密码', 'url': 'users/reset-password-request/', 'method': 'POST'},
        {'name': '确认重置密码', 'url': 'users/reset-password-confirm/', 'method': 'POST'},
        {'name': '获取当前用户信息', 'url': 'users/me/', 'method': 'GET'},
        {'name': '更新当前用户信息', 'url': 'users/update_me/', 'method': 'PUT'},
    ]
    
    # 如果启用了RBAC，添加权限管理相关API
    if settings.ENABLE_RBAC:
        rbac_endpoints = [
            {'name': '权限列表', 'url': 'auth/permissions/', 'method': 'GET'},
            {'name': '角色列表', 'url': 'auth/roles/', 'method': 'GET'},
            {'name': '用户角色关联', 'url': 'auth/user-roles/', 'method': 'GET'},
            {'name': '获取当前用户的角色', 'url': 'auth/user-permissions/my_roles/', 'method': 'GET'},
            {'name': '获取当前用户的权限', 'url': 'auth/user-permissions/my_permissions/', 'method': 'GET'},
            {'name': '检查当前用户是否拥有指定权限', 'url': 'auth/user-permissions/check_permission/', 'method': 'POST'},
        ]
        api_endpoints.extend(rbac_endpoints)
    
    context = {
        'base_url': base_url,
        'user_info': user_info,
        'api_endpoints': api_endpoints,
    }
    
    return render(request, 'projects/api_test.html', context)


@login_required
def rbac_test_view(request):
    """权限管理测试页面视图"""
    # 如果未启用RBAC，则重定向到首页
    if not settings.ENABLE_RBAC:
        messages.warning(request, '权限管理模块未启用！')
        return redirect('projects:index')
    
    # 获取当前用户的角色和权限
    user_roles = []
    user_permissions = []
    
    # 通过API获取用户角色和权限
    try:
        headers = {'Authorization': f'Bearer {request.session.get("access_token", "")}'}
        
        # 获取用户角色
        roles_response = requests.get(
            request.build_absolute_uri('/api/auth/user-permissions/my_roles/'),
            headers=headers
        )
        if roles_response.status_code == 200:
            user_roles = roles_response.json()
        
        # 获取用户权限
        permissions_response = requests.get(
            request.build_absolute_uri('/api/auth/user-permissions/my_permissions/'),
            headers=headers
        )
        if permissions_response.status_code == 200:
            user_permissions = permissions_response.json()
    except Exception as e:
        messages.error(request, f'获取权限信息失败：{str(e)}')
    
    context = {
        'user_roles': user_roles,
        'user_permissions': user_permissions,
    }
    
    return render(request, 'projects/rbac_test.html', context)
