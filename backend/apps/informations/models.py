from django.db import models
from django.utils.translation import gettext_lazy as _


class AnnouncementType(models.Model):
    """公告类型模型"""
    name = models.CharField(_('类型名称'), max_length=50)
    description = models.TextField(_('类型描述'), blank=True, null=True)
    icon = models.CharField(_('图标'), max_length=50, blank=True, null=True)
    color = models.CharField(_('颜色'), max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('公告类型')
        verbose_name_plural = _('公告类型')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_or_create_default_types(cls):
        """创建默认公告类型"""
        default_types = [
            {
                'name': 'emergency',
                'description': '紧急通知',
                'icon': 'el-icon-warning',
                'color': '#F56C6C'
            },
            {
                'name': 'regular',
                'description': '常规通知',
                'icon': 'el-icon-info',
                'color': '#Ecf5ff'
            },
            {
                'name': 'congestion',
                'description': '拥堵区预警',
                'icon': 'el-icon-warning-outline',
                'color': '#E6A23C'
            },
            {
                'name': 'gate_change',
                'description': '登机口变更',
                'icon': 'el-icon-position',
                'color': '#67C23A'
            }
        ]
        
        for type_data in default_types:
            cls.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )


class Announcement(models.Model):
    """公告信息模型"""
    PRIORITY_CHOICES = (
        (1, '低'),
        (2, '中'),
        (3, '高'),
    )
    
    title = models.CharField(_('公告标题'), max_length=100)
    content = models.TextField(_('公告内容'))
    type = models.ForeignKey(
        AnnouncementType,
        on_delete=models.CASCADE,
        related_name='announcements',
        verbose_name=_('公告类型')
    )
    priority = models.IntegerField(_('优先级'), choices=PRIORITY_CHOICES, default=2)
    is_active = models.BooleanField(_('是否激活'), default=True)
    start_time = models.DateTimeField(_('生效时间'), null=True, blank=True)
    end_time = models.DateTimeField(_('失效时间'), null=True, blank=True)
    location = models.CharField(_('相关位置'), max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_announcements',
        verbose_name=_('创建者')
    )
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('公告信息')
        verbose_name_plural = _('公告信息')
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_voice_content(self):
        """获取语音播报内容"""
        type_name = self.type.description if self.type else "通知"
        if self.location:
            return f"{type_name}：{self.title}。{self.content}。相关区域：{self.location}。"
        return f"{type_name}：{self.title}。{self.content}。"


class AnnouncementBroadcast(models.Model):
    """公告播报记录模型"""
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='broadcasts',
        verbose_name=_('公告信息')
    )
    content = models.TextField(_('播报内容'))
    broadcast_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='broadcasted_announcements',
        verbose_name=_('播报者')
    )
    broadcast_at = models.DateTimeField(_('播报时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('公告播报记录')
        verbose_name_plural = _('公告播报记录')
        ordering = ['-broadcast_at']
    
    def __str__(self):
        return f"{self.announcement.title} - {self.broadcast_at.strftime('%Y-%m-%d %H:%M:%S')}"
