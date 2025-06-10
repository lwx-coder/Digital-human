from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Location(models.Model):
    """位置信息模型"""
    name = models.CharField("位置名称", max_length=100)
    description = models.TextField("位置描述", blank=True, null=True)
    floor = models.IntegerField("楼层", default=1)
    x_coordinate = models.FloatField("X坐标")
    y_coordinate = models.FloatField("Y坐标")
    type = models.CharField("位置类型", max_length=50, choices=[
        ('gate', '登机口'),
        ('shop', '商店'),
        ('restaurant', '餐厅'),
        ('toilet', '卫生间'),
        ('security', '安检口'),
        ('check_in', '值机柜台'),
        ('luggage', '行李提取处'),
        ('exit', '出口'),
        ('entrance', '入口'),
        ('lounge', '休息室'),
        ('other', '其他')
    ])
    is_active = models.BooleanField("是否启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "位置信息"
        verbose_name_plural = verbose_name
        ordering = ['floor', 'name']

    def __str__(self):
        return f"{self.name} (楼层:{self.floor})"


class NavigationRecord(models.Model):
    """导航记录模型"""
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="旅客", related_name="navigation_records")
    start_location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="起始位置", related_name="nav_start")
    end_location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="目标位置", related_name="nav_end")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    estimated_time = models.IntegerField("预计时间(分钟)", default=0)
    distance = models.IntegerField("距离(米)", default=0)
    completed = models.BooleanField("是否完成", default=False)
    completed_at = models.DateTimeField("完成时间", null=True, blank=True)

    class Meta:
        verbose_name = "导航记录"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.passenger.username}: {self.start_location.name} -> {self.end_location.name}"


class TimeSchedule(models.Model):
    """时间安排模型"""
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="旅客", related_name="time_schedules")
    flight_code = models.CharField("航班号", max_length=20, blank=True, null=True)
    event_name = models.CharField("事件名称", max_length=100)
    event_type = models.CharField("事件类型", max_length=50, choices=[
        ('check_in', '办理登机'),
        ('security', '安检'),
        ('boarding', '登机'),
        ('shopping', '购物'),
        ('dining', '用餐'),
        ('resting', '休息'),
        ('other', '其他')
    ])
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, verbose_name="位置", null=True, blank=True)
    start_time = models.DateTimeField("开始时间")
    end_time = models.DateTimeField("结束时间", null=True, blank=True)
    notes = models.TextField("备注", blank=True, null=True)
    is_completed = models.BooleanField("是否完成", default=False)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "时间安排"
        verbose_name_plural = verbose_name
        ordering = ['start_time']

    def __str__(self):
        return f"{self.passenger.username}: {self.event_name} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"
