from django.contrib import admin
from .models import PassengerNote, PassengerActivity, PassengerTag, PassengerProfile


@admin.register(PassengerTag)
class PassengerTagAdmin(admin.ModelAdmin):
    """旅客标签管理界面"""
    list_display = ('name', 'description', 'color', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)


@admin.register(PassengerNote)
class PassengerNoteAdmin(admin.ModelAdmin):
    """旅客备注管理界面"""
    list_display = ('passenger', 'note', 'created_by', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'created_by')
    search_fields = ('passenger__username', 'note', 'created_by__username')
    raw_id_fields = ('passenger', 'created_by')
    date_hierarchy = 'created_at'


@admin.register(PassengerActivity)
class PassengerActivityAdmin(admin.ModelAdmin):
    """旅客活动记录管理界面"""
    list_display = ('passenger', 'activity_type', 'description', 'ip_address', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('passenger__username', 'description', 'ip_address')
    raw_id_fields = ('passenger',)
    date_hierarchy = 'created_at'
    readonly_fields = ('passenger', 'activity_type', 'description', 'ip_address', 'user_agent', 'created_at')

    def has_add_permission(self, request):
        """禁止在管理界面添加活动记录"""
        return False

    def has_change_permission(self, request, obj=None):
        """禁止在管理界面修改活动记录"""
        return False


@admin.register(PassengerProfile)
class PassengerProfileAdmin(admin.ModelAdmin):
    """旅客资料管理界面"""
    list_display = ('passenger', 'vip_level', 'frequent_flyer_number', 'created_at', 'updated_at')
    list_filter = ('vip_level', 'created_at', 'updated_at')
    search_fields = ('passenger__username', 'passenger__email', 'frequent_flyer_number', 'passport_number')
    raw_id_fields = ('passenger',)
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
