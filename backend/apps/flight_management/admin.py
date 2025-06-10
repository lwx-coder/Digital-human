from django.contrib import admin
from .models import Flight, FlightAnnouncement


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    """航班管理"""
    list_display = ('flight_number', 'airline', 'departure_city', 'arrival_city', 
                   'scheduled_departure_time', 'scheduled_arrival_time', 'status')
    list_filter = ('status', 'airline', 'departure_city', 'arrival_city')
    search_fields = ('flight_number', 'airline', 'departure_city', 'arrival_city')
    date_hierarchy = 'scheduled_departure_time'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(FlightAnnouncement)
class FlightAnnouncementAdmin(admin.ModelAdmin):
    """航班播报管理"""
    list_display = ('flight', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('flight__flight_number', 'content')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
