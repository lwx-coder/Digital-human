from django.contrib import admin
from .models import AnnouncementType, Announcement, AnnouncementBroadcast


@admin.register(AnnouncementType)
class AnnouncementTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'priority', 'is_active', 'created_at', 'updated_at')
    list_filter = ('type', 'priority', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'location')
    date_hierarchy = 'created_at'
    raw_id_fields = ('created_by',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AnnouncementBroadcast)
class AnnouncementBroadcastAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'broadcast_by', 'broadcast_at')
    list_filter = ('broadcast_at',)
    search_fields = ('announcement__title', 'content')
    date_hierarchy = 'broadcast_at'
    raw_id_fields = ('announcement', 'broadcast_by')
