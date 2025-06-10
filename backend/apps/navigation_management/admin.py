from django.contrib import admin
from .models import Location, NavigationRecord, TimeSchedule

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'floor', 'type', 'is_active']
    list_filter = ['floor', 'type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(NavigationRecord)
class NavigationRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'passenger', 'start_location', 'end_location', 
                   'estimated_time', 'distance', 'completed', 'created_at']
    list_filter = ['completed', 'created_at']
    search_fields = ['passenger__username', 'start_location__name', 'end_location__name']
    date_hierarchy = 'created_at'


@admin.register(TimeSchedule)
class TimeScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'passenger', 'event_name', 'event_type', 'location', 
                   'start_time', 'is_completed']
    list_filter = ['event_type', 'is_completed', 'start_time']
    search_fields = ['passenger__username', 'event_name', 'flight_code']
    date_hierarchy = 'start_time'
