from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PassengerNote, PassengerActivity, PassengerTag, PassengerProfile
from apps.items_management.models import LostItem
from apps.items_management.serializers import LostItemListSerializer
from apps.users.serializers import CustomUserSimpleSerializer

User = get_user_model()


class PassengerTagSerializer(serializers.ModelSerializer):
    """旅客标签序列化器"""
    class Meta:
        model = PassengerTag
        fields = '__all__'


class PassengerNoteSerializer(serializers.ModelSerializer):
    """旅客备注序列化器"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = PassengerNote
        fields = ['id', 'passenger', 'note', 'created_by', 'created_by_username', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class PassengerNoteCreateSerializer(serializers.ModelSerializer):
    """旅客备注创建序列化器"""
    class Meta:
        model = PassengerNote
        fields = ['passenger', 'note']
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['created_by'] = request.user
        return super().create(validated_data)


class PassengerActivitySerializer(serializers.ModelSerializer):
    """旅客活动序列化器"""
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    
    class Meta:
        model = PassengerActivity
        fields = ['id', 'passenger', 'activity_type', 'activity_type_display', 'description', 
                 'ip_address', 'user_agent', 'created_at']
        read_only_fields = ['created_at']


class PassengerProfileSerializer(serializers.ModelSerializer):
    """旅客资料序列化器"""
    tags = PassengerTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=PassengerTag.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='tags'
    )
    
    class Meta:
        model = PassengerProfile
        fields = ['id', 'passenger', 'tags', 'tag_ids', 'frequent_flyer_number', 
                 'passport_number', 'id_card_number', 'emergency_contact', 
                 'emergency_phone', 'last_login_ip', 'vip_level', 
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'last_login_ip']


class PassengerProfileUpdateSerializer(serializers.ModelSerializer):
    """旅客资料更新序列化器"""
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=PassengerTag.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='tags'
    )
    
    class Meta:
        model = PassengerProfile
        fields = ['tag_ids', 'frequent_flyer_number', 
                 'passport_number', 'id_card_number', 'emergency_contact', 
                 'emergency_phone', 'vip_level']


class PassengerDetailSerializer(serializers.ModelSerializer):
    """旅客详情序列化器"""
    profile = PassengerProfileSerializer(source='passenger_profile', read_only=True)
    recent_notes = serializers.SerializerMethodField()
    recent_activities = serializers.SerializerMethodField()
    recent_lost_items = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'first_name', 'last_name', 
                  'address', 'avatar', 'bio', 'birth_date', 'is_active', 
                  'date_joined', 'last_login', 'profile', 'roles',
                  'recent_notes', 'recent_activities', 'recent_lost_items']
    
    def get_roles(self, obj):
        return obj.get_roles()
    
    def get_recent_notes(self, obj):
        notes = obj.notes.all()[:5]
        return PassengerNoteSerializer(notes, many=True).data
    
    def get_recent_activities(self, obj):
        activities = obj.activities.all()[:10]
        return PassengerActivitySerializer(activities, many=True).data
    
    def get_recent_lost_items(self, obj):
        lost_items = LostItem.objects.filter(reported_by=obj)[:5]
        return LostItemListSerializer(lost_items, many=True).data


class PassengerListSerializer(serializers.ModelSerializer):
    """旅客列表序列化器"""
    tags = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    lost_items_count = serializers.SerializerMethodField()
    vip_level = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'first_name', 'last_name', 
                 'avatar', 'is_active', 'date_joined', 'last_login', 
                 'roles', 'tags', 'lost_items_count', 'vip_level']
    
    def get_roles(self, obj):
        return obj.get_roles()
    
    def get_tags(self, obj):
        try:
            profile = obj.passenger_profile
            return PassengerTagSerializer(profile.tags.all(), many=True).data
        except PassengerProfile.DoesNotExist:
            return []
    
    def get_lost_items_count(self, obj):
        return LostItem.objects.filter(reported_by=obj).count()
    
    def get_vip_level(self, obj):
        try:
            return obj.passenger_profile.vip_level
        except PassengerProfile.DoesNotExist:
            return 0 