from django.contrib import admin
from .models import ItemCategory, LostItem, ItemBroadcast

@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    """物品类别管理"""
    list_display = ('name', 'description', 'icon', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)


@admin.register(LostItem)
class LostItemAdmin(admin.ModelAdmin):
    """失物信息管理"""
    list_display = ('title', 'category', 'status', 'lost_location', 
                    'contact_name', 'is_broadcasted', 'created_at')
    list_filter = ('status', 'category', 'is_broadcasted', 'created_at')
    search_fields = ('title', 'description', 'lost_location', 'contact_name')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ItemBroadcast)
class ItemBroadcastAdmin(admin.ModelAdmin):
    """物品广播记录管理"""
    list_display = ('lost_item', 'broadcast_by', 'broadcast_at')
    list_filter = ('broadcast_at',)
    search_fields = ('lost_item__title', 'content')
    date_hierarchy = 'broadcast_at'
    readonly_fields = ('broadcast_at',)
