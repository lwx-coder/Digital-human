from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """
    角色模型
    """
    name = models.CharField(_('角色名称'), max_length=50, unique=True)
    description = models.TextField(_('角色描述'), blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('角色')
        verbose_name_plural = _('角色')
        ordering = ['name']

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create_default_roles(cls):
        """创建默认角色"""
        default_roles = [
            {'name': 'passenger', 'description': '旅客'},
            {'name': 'admin', 'description': '管理员'},
        ]
        for role_data in default_roles:
            cls.objects.get_or_create(name=role_data['name'], defaults=role_data)


class CustomUser(AbstractUser):
    """
    自定义用户模型，扩展了Django默认的User模型
    """
    phone = models.CharField(_('手机号'), max_length=20, blank=True, null=True)
    address = models.CharField(_('地址'), max_length=255, blank=True, null=True)
    avatar = models.ImageField(_('头像'), upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(_('个人简介'), blank=True, null=True)
    birth_date = models.DateField(_('出生日期'), blank=True, null=True)
    roles = models.ManyToManyField(Role, verbose_name=_('角色'), blank=True)
    selected_flights = models.JSONField(_('已选航班'), default=list, blank=True, null=True, help_text=_('存储用户选择的航班ID列表'))
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        
    def __str__(self):
        return self.username

    def get_roles(self):
        """获取用户的所有角色名称列表"""
        roles = list(self.roles.values_list('name', flat=True))
        if self.is_staff:
            if 'admin' not in roles:
                roles.append('admin')
        return roles
