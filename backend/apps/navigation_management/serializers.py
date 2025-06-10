from rest_framework import serializers
from .models import Location, NavigationRecord, TimeSchedule


class LocationSerializer(serializers.ModelSerializer):
    """位置信息序列化器"""
    type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = ['id', 'name', 'description', 'floor', 'x_coordinate', 'y_coordinate', 'type', 'type_display', 'is_active']
    
    def get_type_display(self, obj):
        return obj.get_type_display()


class LocationListSerializer(serializers.ModelSerializer):
    """位置信息简略序列化器"""
    type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = ['id', 'name', 'floor', 'type', 'type_display']
    
    def get_type_display(self, obj):
        return obj.get_type_display()


class NavigationRecordSerializer(serializers.ModelSerializer):
    """导航记录序列化器"""
    start_location_detail = LocationSerializer(source='start_location', read_only=True)
    end_location_detail = LocationSerializer(source='end_location', read_only=True)
    passenger_name = serializers.SerializerMethodField()
    
    class Meta:
        model = NavigationRecord
        fields = ['id', 'passenger', 'passenger_name', 'start_location', 'start_location_detail', 
                  'end_location', 'end_location_detail', 'created_at', 'estimated_time', 
                  'distance', 'completed', 'completed_at']
        extra_kwargs = {
            'passenger': {'write_only': True},
            'start_location': {'write_only': True},
            'end_location': {'write_only': True}
        }
    
    def get_passenger_name(self, obj):
        return obj.passenger.username
    
    def create(self, validated_data):
        # 计算距离和预计时间（简化版）
        start = validated_data['start_location']
        end = validated_data['end_location']
        
        # 简单距离计算 - 实际项目中可能使用更复杂的算法
        import math
        if start.floor == end.floor:
            distance = math.sqrt((start.x_coordinate - end.x_coordinate) ** 2 + 
                                 (start.y_coordinate - end.y_coordinate) ** 2)
        else:
            # 不同楼层额外增加距离
            floor_diff = abs(start.floor - end.floor) * 50  # 每层楼增加50米
            direct_distance = math.sqrt((start.x_coordinate - end.x_coordinate) ** 2 + 
                                        (start.y_coordinate - end.y_coordinate) ** 2)
            distance = direct_distance + floor_diff
        
        # 四舍五入到整数米
        distance_meters = round(distance)
        
        # 假设平均行走速度为1米/秒，计算分钟数
        time_minutes = round(distance_meters / 60)  # 60米/分钟
        
        # 设置最小时间为1分钟
        if time_minutes < 1:
            time_minutes = 1
        
        validated_data['distance'] = distance_meters
        validated_data['estimated_time'] = time_minutes
        
        return super().create(validated_data)


class TimeScheduleSerializer(serializers.ModelSerializer):
    """时间安排序列化器"""
    location_detail = LocationSerializer(source='location', read_only=True)
    event_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeSchedule
        fields = ['id', 'passenger', 'flight_code', 'event_name', 'event_type', 'event_type_display',
                  'location', 'location_detail', 'start_time', 'end_time', 'notes', 
                  'is_completed', 'created_at', 'updated_at']
        extra_kwargs = {
            'passenger': {'write_only': True, 'required': False},
            'location': {'write_only': True}
        }
    
    def get_event_type_display(self, obj):
        return obj.get_event_type_display()
        
    def create(self, validated_data):
        # 如果没有提供passenger字段，使用当前请求用户
        request = self.context.get('request')
        if request and hasattr(request, 'user') and not validated_data.get('passenger'):
            validated_data['passenger'] = request.user
        return super().create(validated_data)


class NavigationQuerySerializer(serializers.Serializer):
    """导航查询序列化器"""
    current_location_id = serializers.IntegerField(required=True)
    destination_id = serializers.IntegerField(required=True)


class VoiceNavigationSerializer(serializers.Serializer):
    """语音导航序列化器"""
    navigation_id = serializers.IntegerField(required=False)
    current_location_id = serializers.IntegerField(required=False)
    destination_id = serializers.IntegerField(required=False)
    query_type = serializers.ChoiceField(choices=[
        ('direction', '方向导航'),
        ('time_to_destination', '到达时间'),
        ('schedule', '时间安排'),
        ('nearby', '附近设施')
    ])
    

class ScheduleQuerySerializer(serializers.Serializer):
    """时间安排查询序列化器"""
    flight_code = serializers.CharField(required=False, allow_blank=True)
    date = serializers.DateField(required=False)
    include_completed = serializers.BooleanField(default=False) 