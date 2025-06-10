from rest_framework import serializers
from .models import AnnouncementType, Announcement, AnnouncementBroadcast


class AnnouncementTypeSerializer(serializers.ModelSerializer):
    """公告类型序列化器"""
    class Meta:
        model = AnnouncementType
        fields = ['id', 'name', 'description', 'icon', 'color', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AnnouncementListSerializer(serializers.ModelSerializer):
    """公告列表序列化器"""
    type_name = serializers.CharField(source='type.description', read_only=True)
    type_color = serializers.CharField(source='type.color', read_only=True)
    type_icon = serializers.CharField(source='type.icon', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'type', 'type_name', 'type_color', 'type_icon',
            'priority', 'priority_display', 'is_active', 'start_time', 'end_time',
            'location', 'created_by', 'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by_username', 'type_name', 'type_color', 'type_icon']


class AnnouncementDetailSerializer(serializers.ModelSerializer):
    """公告详情序列化器"""
    type_data = AnnouncementTypeSerializer(source='type', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'type', 'type_data', 'priority', 'priority_display',
            'is_active', 'start_time', 'end_time', 'location',
            'created_by', 'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by_username', 'type_data']


class AnnouncementCreateUpdateSerializer(serializers.ModelSerializer):
    """公告创建和更新序列化器"""
    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'type', 'priority', 'is_active', 
            'start_time', 'end_time', 'location'
        ]

    def create(self, validated_data):
        # 设置创建者为当前用户
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AnnouncementBroadcastSerializer(serializers.ModelSerializer):
    """公告播报记录序列化器"""
    announcement_title = serializers.CharField(source='announcement.title', read_only=True)
    announcement_type = serializers.CharField(source='announcement.type.description', read_only=True)
    broadcast_by_username = serializers.CharField(source='broadcast_by.username', read_only=True)
    
    class Meta:
        model = AnnouncementBroadcast
        fields = [
            'id', 'announcement', 'announcement_title', 'announcement_type',
            'content', 'broadcast_by', 'broadcast_by_username', 'broadcast_at'
        ]
        read_only_fields = ['broadcast_at', 'broadcast_by_username', 'announcement_title', 'announcement_type']


class AnnouncementBroadcastCreateSerializer(serializers.Serializer):
    """公告播报创建序列化器"""
    announcement_id = serializers.IntegerField()
    content = serializers.CharField(required=False, allow_blank=True)

    def validate_announcement_id(self, value):
        try:
            announcement = Announcement.objects.get(pk=value)
            if not announcement.is_active:
                raise serializers.ValidationError("此公告当前未激活")
            return value
        except Announcement.DoesNotExist:
            raise serializers.ValidationError("公告不存在") 