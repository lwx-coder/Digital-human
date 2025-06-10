from django.db import models
from django.utils.translation import gettext_lazy as _


class Flight(models.Model):
    """航班信息模型"""
    FLIGHT_STATUS_CHOICES = (
        ('scheduled', '计划'),
        ('delayed', '延误'),
        ('boarding', '登机中'),
        ('departed', '已起飞'),
        ('arrived', '已到达'),
        ('cancelled', '取消'),
    )
    
    flight_number = models.CharField(_('航班号'), max_length=20, unique=True)
    airline = models.CharField(_('航空公司'), max_length=100)
    departure_city = models.CharField(_('出发城市'), max_length=100)
    arrival_city = models.CharField(_('到达城市'), max_length=100)
    departure_airport = models.CharField(_('出发机场'), max_length=100)
    arrival_airport = models.CharField(_('到达机场'), max_length=100)
    scheduled_departure_time = models.DateTimeField(_('计划出发时间'))
    scheduled_arrival_time = models.DateTimeField(_('计划到达时间'))
    actual_departure_time = models.DateTimeField(_('实际出发时间'), null=True, blank=True)
    actual_arrival_time = models.DateTimeField(_('实际到达时间'), null=True, blank=True)
    gate = models.CharField(_('登机口'), max_length=50, null=True, blank=True)
    terminal = models.CharField(_('航站楼'), max_length=50, null=True, blank=True)
    status = models.CharField(_('航班状态'), max_length=20, choices=FLIGHT_STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('航班')
        verbose_name_plural = _('航班')
        ordering = ['-scheduled_departure_time']
    
    def __str__(self):
        return f"{self.flight_number} - {self.departure_city} 至 {self.arrival_city}"
    
    def get_status_display_for_voice(self):
        """
        返回适合语音播报的航班状态描述
        """
        status_map = {
            'scheduled': f'航班{self.flight_number}计划于{self.scheduled_departure_time.strftime("%Y年%m月%d日 %H时%M分")}从{self.departure_airport}{self.terminal}航站楼{self.gate}登机口出发。',
            'delayed': f'航班{self.flight_number}延误，预计延误到{self.actual_departure_time.strftime("%Y年%m月%d日 %H时%M分") if self.actual_departure_time else "未知时间"}，请关注航班动态。',
            'boarding': f'航班{self.flight_number}正在{self.terminal}航站楼{self.gate}登机口登机，请尽快前往。',
            'departed': f'航班{self.flight_number}已于{self.actual_departure_time.strftime("%Y年%m月%d日 %H时%M分") if self.actual_departure_time else "未知时间"}起飞。',
            'arrived': f'航班{self.flight_number}已于{self.actual_arrival_time.strftime("%Y年%m月%d日 %H时%M分") if self.actual_arrival_time else "未知时间"}到达{self.arrival_airport}。',
            'cancelled': f'航班{self.flight_number}已取消，请联系航空公司获取更多信息。',
        }
        return status_map.get(self.status, f'航班{self.flight_number}状态未知')


class FlightAnnouncement(models.Model):
    """航班播报模型，记录数字人播报记录"""
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='announcements', verbose_name=_('航班'))
    content = models.TextField(_('播报内容'))
    created_at = models.DateTimeField(_('播报时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('航班播报')
        verbose_name_plural = _('航班播报')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.flight.flight_number} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
