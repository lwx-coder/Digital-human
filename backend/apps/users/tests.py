from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAuthTests(TestCase):
    """用户认证测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            phone='13800138000',
            password='testpassword'
        )
    
    def test_register(self):
        """测试用户注册"""
        url = reverse('api:users:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'phone': '13900139000',
            'password': 'newpassword',
            'password_confirm': 'newpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_login(self):
        """测试用户名密码登录"""
        url = reverse('api:users:login')
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
    
    def test_phone_login(self):
        """测试手机号验证码登录"""
        url = reverse('api:users:phone-login')
        data = {
            'phone': '13800138000',
            'code': '123456'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
    
    def test_reset_password(self):
        """测试重置密码"""
        # 请求重置密码
        request_url = reverse('api:users:reset-password-request')
        request_data = {
            'email': 'test@example.com'
        }
        response = self.client.post(request_url, request_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 确认重置密码
        confirm_url = reverse('api:users:reset-password-confirm')
        confirm_data = {
            'email': 'test@example.com',
            'code': '123456',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        response = self.client.post(confirm_url, confirm_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 使用新密码登录
        login_url = reverse('api:users:login')
        login_data = {
            'username': 'testuser',
            'password': 'newpassword123'
        }
        response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
