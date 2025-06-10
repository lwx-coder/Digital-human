from rest_framework import serializers
from .models import ItemCategory, LostItem, ItemBroadcast
from apps.users.serializers import CustomUserSimpleSerializer


class ItemCategorySerializer(serializers.ModelSerializer):
    """物品类别序列化器"""
    class Meta:
        model = ItemCategory
        fields = '__all__'


class LostItemListSerializer(serializers.ModelSerializer):
    """失物信息列表序列化器"""
    category_name = serializers.CharField(source='category.description', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    
    class Meta:
        model = LostItem
        fields = [
            'id', 'title', 'category', 'category_name', 'category_icon',
            'lost_location', 'lost_time', 'status', 'status_display',
            'is_broadcasted', 'reported_by_username', 'created_at'
        ]


class LostItemDetailSerializer(serializers.ModelSerializer):
    """失物信息详情序列化器"""
    category_data = ItemCategorySerializer(source='category', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reported_by_data = CustomUserSimpleSerializer(source='reported_by', read_only=True)
    broadcasts = serializers.SerializerMethodField()
    
    class Meta:
        model = LostItem
        fields = '__all__'
    
    def get_broadcasts(self, obj):
        """获取广播记录"""
        broadcasts = obj.broadcasts.all()
        return ItemBroadcastSerializer(broadcasts, many=True).data


class LostItemCreateUpdateSerializer(serializers.ModelSerializer):
    """失物信息创建和更新序列化器"""
    
    class Meta:
        model = LostItem
        exclude = ['reported_by', 'is_broadcasted', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """创建时设置报失人"""
        request = self.context.get('request')
        validated_data['reported_by'] = request.user
        return super().create(validated_data)


class ItemBroadcastSerializer(serializers.ModelSerializer):
    """物品广播记录序列化器"""
    broadcast_by_username = serializers.CharField(source='broadcast_by.username', read_only=True)
    
    class Meta:
        model = ItemBroadcast
        fields = '__all__'


class ItemBroadcastCreateSerializer(serializers.Serializer):
    """物品广播创建序列化器"""
    lost_item_id = serializers.IntegerField()
    content = serializers.CharField(required=False, allow_blank=True)
    
    def validate_lost_item_id(self, value):
        """验证失物ID"""
        try:
            LostItem.objects.get(pk=value)
            return value
        except LostItem.DoesNotExist:
            raise serializers.ValidationError("失物信息不存在") 