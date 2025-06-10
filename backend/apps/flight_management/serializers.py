from rest_framework import serializers
from .models import Flight, FlightAnnouncement


class FlightSerializer(serializers.ModelSerializer):
    """航班信息序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    voice_status = serializers.CharField(source='get_status_display_for_voice', read_only=True)
    
    class Meta:
        model = Flight
        fields = [
            'id', 'flight_number', 'airline', 
            'departure_city', 'arrival_city', 
            'departure_airport', 'arrival_airport',
            'scheduled_departure_time', 'scheduled_arrival_time',
            'actual_departure_time', 'actual_arrival_time',
            'gate', 'terminal', 'status', 'status_display', 'voice_status',
            'created_at', 'updated_at'
        ]


class FlightListSerializer(serializers.ModelSerializer):
    """航班列表序列化器，用于列表展示减少数据量"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Flight
        fields = [
            'id', 'flight_number', 'airline', 
            'departure_city', 'arrival_city',
            'scheduled_departure_time', 'scheduled_arrival_time',
            'status', 'status_display'
        ]


class FlightAnnouncementSerializer(serializers.ModelSerializer):
    """航班播报序列化器"""
    flight_number = serializers.CharField(source='flight.flight_number', read_only=True)
    
    class Meta:
        model = FlightAnnouncement
        fields = ['id', 'flight', 'flight_number', 'content', 'created_at']
        read_only_fields = ['created_at']


class FlightAnnouncementCreateSerializer(serializers.ModelSerializer):
    """航班播报创建序列化器"""
    flight_number = serializers.CharField(write_only=True)
    
    class Meta:
        model = FlightAnnouncement
        fields = ['flight_number', 'content']
    
    def validate_flight_number(self, value):
        """验证航班号是否存在"""
        try:
            Flight.objects.get(flight_number=value)
        except Flight.DoesNotExist:
            raise serializers.ValidationError("未找到该航班号")
        return value
    
    def create(self, validated_data):
        flight_number = validated_data.pop('flight_number')
        flight = Flight.objects.get(flight_number=flight_number)
        return FlightAnnouncement.objects.create(flight=flight, **validated_data) 