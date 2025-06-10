from django.db import models
from django.utils.translation import gettext_lazy as _

class ItemCategory(models.Model):
    """物品类别模型"""
    name = models.CharField(_('类别名称'), max_length=50)
    description = models.TextField(_('类别描述'), blank=True, null=True)
    icon = models.CharField(_('图标'), max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('物品类别')
        verbose_name_plural = _('物品类别')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_or_create_default_categories(cls):
        """创建默认物品类别"""
        default_categories = [
            {
                'name': 'electronic',
                'description': '电子产品',
                'icon': 'el-icon-mobile-phone'
            },
            {
                'name': 'luggage',
                'description': '行李箱包',
                'icon': 'el-icon-suitcase'
            },
            {
                'name': 'document',
                'description': '证件文件',
                'icon': 'el-icon-document'
            },
            {
                'name': 'clothing',
                'description': '衣物鞋帽',
                'icon': 'el-icon-shopping-bag'
            },
            {
                'name': 'accessories',
                'description': '配饰饰品',
                'icon': 'el-icon-watch'
            },
            {
                'name': 'other',
                'description': '其他物品',
                'icon': 'el-icon-more'
            }
        ]
        
        for category_data in default_categories:
            cls.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )


class LostItem(models.Model):
    """失物信息模型"""
    STATUS_CHOICES = (
        ('lost', '寻物中'),
        ('found', '已找到'),
        ('claimed', '已认领'),
        ('closed', '已关闭')
    )
    
    title = models.CharField(_('物品名称'), max_length=100)
    category = models.ForeignKey(
        ItemCategory, 
        on_delete=models.CASCADE,
        related_name='lost_items',
        verbose_name=_('物品类别')
    )
    description = models.TextField(_('物品描述'))
    lost_time = models.DateTimeField(_('丢失时间'))
    lost_location = models.CharField(_('丢失地点'), max_length=200)
    contact_name = models.CharField(_('联系人姓名'), max_length=50)
    contact_phone = models.CharField(_('联系电话'), max_length=20)
    contact_email = models.EmailField(_('联系邮箱'), blank=True, null=True)
    image = models.URLField(_('物品图片'), blank=True, null=True)
    reported_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_lost_items',
        verbose_name=_('报失人')
    )
    status = models.CharField(_('状态'), max_length=20, choices=STATUS_CHOICES, default='lost')
    is_broadcasted = models.BooleanField(_('是否已广播'), default=False)
    admin_notes = models.TextField(_('管理员备注'), blank=True, null=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('失物信息')
        verbose_name_plural = _('失物信息')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_broadcast_content(self):
        """获取广播内容"""
        content = f"紧急失物通知：{self.contact_name}在{self.lost_location}丢失了{self.title}。"
        content += f"物品描述：{self.description}。"
        content += f"丢失时间：{self.lost_time.strftime('%Y年%m月%d日 %H:%M')}。"
        content += f"如有发现，请联系{self.contact_name}，电话{self.contact_phone}。谢谢！"
        return content


class ItemBroadcast(models.Model):
    """物品广播记录模型"""
    lost_item = models.ForeignKey(
        LostItem,
        on_delete=models.CASCADE,
        related_name='broadcasts',
        verbose_name=_('失物信息')
    )
    content = models.TextField(_('广播内容'))
    broadcast_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='item_broadcasts',
        verbose_name=_('广播者')
    )
    broadcast_at = models.DateTimeField(_('广播时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('物品广播记录')
        verbose_name_plural = _('物品广播记录')
        ordering = ['-broadcast_at']
    
    def __str__(self):
        return f"{self.lost_item.title} - {self.broadcast_at.strftime('%Y-%m-%d %H:%M:%S')}"
