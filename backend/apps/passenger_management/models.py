from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class PassengerNote(models.Model):
    """旅客备注信息模型，用于管理员记录旅客特殊情况"""
    passenger = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('旅客')
    )
    note = models.TextField(_('备注内容'))
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_notes',
        verbose_name=_('创建者')
    )
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('旅客备注')
        verbose_name_plural = _('旅客备注')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.passenger.username} - {self.note[:20]}"


class PassengerActivity(models.Model):
    """旅客活动记录模型，记录旅客在系统中的重要行为"""
    ACTIVITY_TYPES = (
        ('login', _('登录')),
        ('logout', _('登出')),
        ('profile_update', _('更新个人信息')),
        ('flight_booking', _('航班预订')),
        ('flight_checkin', _('航班值机')),
        ('lost_item_report', _('物品报失')),
        ('other', _('其他'))
    )

    passenger = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name=_('旅客')
    )
    activity_type = models.CharField(
        _('活动类型'),
        max_length=50,
        choices=ACTIVITY_TYPES
    )
    description = models.TextField(_('活动描述'))
    ip_address = models.GenericIPAddressField(_('IP地址'), null=True, blank=True)
    user_agent = models.TextField(_('用户代理'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('旅客活动')
        verbose_name_plural = _('旅客活动')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.passenger.username} - {self.get_activity_type_display()}"


class PassengerTag(models.Model):
    """旅客标签模型，用于给旅客添加标签进行分类管理"""
    name = models.CharField(_('标签名称'), max_length=50, unique=True)
    description = models.TextField(_('标签描述'), blank=True, null=True)
    color = models.CharField(_('标签颜色'), max_length=20, default='#409EFF')
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('旅客标签')
        verbose_name_plural = _('旅客标签')
        ordering = ['name']

    def __str__(self):
        return self.name


class PassengerProfile(models.Model):
    """旅客扩展资料模型，存储旅客的额外信息"""
    passenger = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='passenger_profile',
        verbose_name=_('旅客')
    )
    tags = models.ManyToManyField(
        PassengerTag,
        related_name='passengers',
        verbose_name=_('标签'),
        blank=True
    )
    frequent_flyer_number = models.CharField(
        _('常旅客号码'),
        max_length=50,
        blank=True,
        null=True
    )
    passport_number = models.CharField(
        _('护照号码'),
        max_length=50,
        blank=True,
        null=True
    )
    id_card_number = models.CharField(
        _('身份证号码'),
        max_length=18,
        blank=True,
        null=True
    )
    emergency_contact = models.CharField(
        _('紧急联系人'),
        max_length=50,
        blank=True,
        null=True
    )
    emergency_phone = models.CharField(
        _('紧急联系电话'),
        max_length=20,
        blank=True,
        null=True
    )
    last_login_ip = models.GenericIPAddressField(
        _('最后登录IP'),
        blank=True,
        null=True
    )
    vip_level = models.PositiveSmallIntegerField(
        _('VIP等级'),
        default=0
    )
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('旅客资料')
        verbose_name_plural = _('旅客资料')

    def __str__(self):
        return f"{self.passenger.username}的旅客资料"
