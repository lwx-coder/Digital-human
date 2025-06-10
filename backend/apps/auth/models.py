from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class Permission(models.Model):
    """
    权限模型
    """
    name = models.CharField(_('权限名称'), max_length=100)
    codename = models.CharField(_('权限代码'), max_length=100, unique=True)
    description = models.TextField(_('权限描述'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('权限')
        verbose_name_plural = _('权限')
        ordering = ['codename']
    
    def __str__(self):
        return self.name


class Role(models.Model):
    """
    角色模型
    """
    name = models.CharField(_('角色名称'), max_length=100)
    code = models.CharField(_('角色代码'), max_length=100, unique=True)
    description = models.TextField(_('角色描述'), blank=True, null=True)
    permissions = models.ManyToManyField(
        Permission, 
        verbose_name=_('权限'),
        blank=True,
        related_name='roles'
    )
    
    class Meta:
        verbose_name = _('角色')
        verbose_name_plural = _('角色')
        ordering = ['code']
    
    def __str__(self):
        return self.name


class UserRole(models.Model):
    """
    用户角色关联模型
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name=_('用户'),
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role, 
        on_delete=models.CASCADE, 
        verbose_name=_('角色'),
        related_name='user_roles'
    )
    
    class Meta:
        verbose_name = _('用户角色')
        verbose_name_plural = _('用户角色')
        unique_together = ['user', 'role']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
