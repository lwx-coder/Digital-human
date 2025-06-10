from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
import random
import math

from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import Location, NavigationRecord, TimeSchedule
from .serializers import (
    LocationSerializer, LocationListSerializer, NavigationRecordSerializer,
    TimeScheduleSerializer, NavigationQuerySerializer, VoiceNavigationSerializer,
    ScheduleQuerySerializer
)

class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """位置信息视图集"""
    permission_classes = [IsAuthenticated]
    queryset = Location.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LocationListSerializer
        return LocationSerializer
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """按类型获取位置列表"""
        location_type = request.query_params.get('type')
        floor = request.query_params.get('floor')
        
        queryset = self.get_queryset()
        
        if location_type:
            queryset = queryset.filter(type=location_type)
        
        if floor:
            queryset = queryset.filter(floor=floor)
        
        serializer = LocationListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """获取附近设施"""
        current_x = float(request.query_params.get('x', 0))
        current_y = float(request.query_params.get('y', 0))
        floor = int(request.query_params.get('floor', 1))
        radius = float(request.query_params.get('radius', 100))  # 默认100米半径
        types = request.query_params.getlist('types', [])  # 设施类型列表
        
        # 基于当前楼层过滤
        queryset = self.get_queryset().filter(floor=floor)
        
        # 如果指定了类型，进一步过滤
        if types:
            queryset = queryset.filter(type__in=types)
        
        # 计算与当前位置的距离
        nearby_locations = []
        for location in queryset:
            distance = math.sqrt((location.x_coordinate - current_x) ** 2 + 
                                (location.y_coordinate - current_y) ** 2)
            
            if distance <= radius:
                location_data = LocationSerializer(location).data
                location_data['distance'] = round(distance)
                nearby_locations.append(location_data)
        
        # 按距离排序
        nearby_locations.sort(key=lambda x: x['distance'])
        
        return Response(nearby_locations)


class NavigationRecordViewSet(viewsets.ModelViewSet):
    """导航记录视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = NavigationRecordSerializer
    
    def get_queryset(self):
        # 旅客只能查看自己的导航记录
        return NavigationRecord.objects.filter(passenger=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(passenger=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """标记导航完成"""
        navigation = self.get_object()
        navigation.completed = True
        navigation.completed_at = timezone.now()
        navigation.save()
        
        serializer = self.get_serializer(navigation)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def navigate(self, request):
        """创建新的导航记录"""
        serializer = NavigationQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 获取位置信息
        current_location = get_object_or_404(
            Location, id=serializer.validated_data['current_location_id'], is_active=True
        )
        destination = get_object_or_404(
            Location, id=serializer.validated_data['destination_id'], is_active=True
        )
        
        # 创建导航记录
        navigation_record = NavigationRecord.objects.create(
            passenger=request.user,
            start_location=current_location,
            end_location=destination
        )
        
        response_serializer = self.get_serializer(navigation_record)
        return Response(response_serializer.data)
    
    @action(detail=False, methods=['post'])
    def voice_query(self, request):
        """语音导航查询"""
        serializer = VoiceNavigationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        query_type = serializer.validated_data['query_type']
        navigation_id = serializer.validated_data.get('navigation_id')
        current_location_id = serializer.validated_data.get('current_location_id')
        destination_id = serializer.validated_data.get('destination_id')
        
        navigation = None
        
        # 如果提供了导航ID，获取该导航记录
        if navigation_id:
            try:
                navigation = NavigationRecord.objects.get(id=navigation_id, passenger=request.user)
            except NavigationRecord.DoesNotExist:
                return Response({'error': '导航记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 如果提供了当前位置和目的地，但没有导航ID，创建一个新的导航
        elif current_location_id and destination_id:
            current_location = get_object_or_404(Location, id=current_location_id, is_active=True)
            destination = get_object_or_404(Location, id=destination_id, is_active=True)
            
            navigation = NavigationRecord.objects.create(
                passenger=request.user,
                start_location=current_location,
                end_location=destination
            )
        else:
            return Response(
                {'error': '请提供导航ID或当前位置和目的地ID'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 根据查询类型返回不同的响应
        response_data = {
            'navigation_id': navigation.id,
            'query_type': query_type,
        }
        
        if query_type == 'direction':
            # 方向导航
            response_data['voice_text'] = self._generate_direction_text(navigation)
        elif query_type == 'time_to_destination':
            # 到达时间
            response_data['voice_text'] = self._generate_time_text(navigation)
        elif query_type == 'schedule':
            # 时间安排
            response_data['voice_text'] = self._generate_schedule_text(request.user)
        elif query_type == 'nearby':
            # 附近设施
            response_data['voice_text'] = self._generate_nearby_text(navigation.start_location)
        
        return Response(response_data)
    
    def _generate_direction_text(self, navigation):
        """生成方向导航文本"""
        start = navigation.start_location
        end = navigation.end_location
        
        # 简单的方向文本生成
        text = f"从{start.name}前往{end.name}的导航已开始。"
        
        # 同一楼层
        if start.floor == end.floor:
            text += f"请在{start.floor}楼层，"
            
            # 根据坐标判断大致方向
            if end.x_coordinate > start.x_coordinate:
                text += "向东"
            else:
                text += "向西"
                
            if end.y_coordinate > start.y_coordinate:
                text += "南"
            else:
                text += "北"
                
            text += f"方向走约{navigation.distance}米。"
        else:
            # 不同楼层
            if end.floor > start.floor:
                text += f"请先乘坐电梯或扶梯上楼至{end.floor}楼，"
            else:
                text += f"请先乘坐电梯或扶梯下楼至{end.floor}楼，"
                
            text += f"然后按照指示牌寻找{end.name}位置。总距离约{navigation.distance}米。"
        
        text += f"预计需要{navigation.estimated_time}分钟到达。"
        return text
    
    def _generate_time_text(self, navigation):
        """生成到达时间文本"""
        now = timezone.now()
        arrival_time = now + timedelta(minutes=navigation.estimated_time)
        
        text = f"从{navigation.start_location.name}到{navigation.end_location.name}，"
        text += f"估计距离{navigation.distance}米，步行约需{navigation.estimated_time}分钟。"
        text += f"预计到达时间为{arrival_time.strftime('%H:%M')}。"
        
        return text
    
    def _generate_schedule_text(self, user):
        """生成时间安排文本"""
        # 获取未来24小时的安排
        now = timezone.now()
        end_time = now + timedelta(hours=24)
        
        schedules = TimeSchedule.objects.filter(
            passenger=user,
            start_time__gte=now,
            start_time__lte=end_time,
            is_completed=False
        ).order_by('start_time')
        
        if not schedules:
            return "您未来24小时内没有安排。"
        
        text = "您未来24小时的安排如下："
        
        for i, schedule in enumerate(schedules, 1):
            event_time = schedule.start_time.strftime('%H:%M')
            location_name = schedule.location.name if schedule.location else "未指定位置"
            
            text += f"\n{i}. {event_time}, {schedule.event_name}，在{location_name}。"
        
        return text
    
    def _generate_nearby_text(self, location):
        """生成附近设施文本"""
        # 获取当前位置附近的设施
        nearby_facilities = Location.objects.filter(
            floor=location.floor,
            is_active=True
        ).exclude(id=location.id)
        
        # 计算距离并筛选最近的5个设施
        facilities_with_distance = []
        for facility in nearby_facilities:
            distance = math.sqrt(
                (facility.x_coordinate - location.x_coordinate) ** 2 + 
                (facility.y_coordinate - location.y_coordinate) ** 2
            )
            facilities_with_distance.append((facility, distance))
        
        # 按距离排序并取前5个
        facilities_with_distance.sort(key=lambda x: x[1])
        nearest_facilities = facilities_with_distance[:5]
        
        if not nearest_facilities:
            return f"在{location.floor}楼层没有找到其他设施。"
        
        text = f"在{location.name}附近的设施有："
        
        for i, (facility, distance) in enumerate(nearest_facilities, 1):
            text += f"\n{i}. {facility.name}，距离约{round(distance)}米，{facility.get_type_display()}。"
        
        return text


class TimeScheduleViewSet(viewsets.ModelViewSet):
    """时间安排视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = TimeScheduleSerializer
    
    def get_queryset(self):
        # 默认只显示未完成的和未来的安排
        user = self.request.user
        now = timezone.now()
        
        # 获取查询参数
        flight_code = self.request.query_params.get('flight_code')
        date_str = self.request.query_params.get('date')
        include_completed = self.request.query_params.get('include_completed', 'false').lower() == 'true'
        
        # 基础查询集 - 只包含自己的安排
        queryset = TimeSchedule.objects.filter(passenger=user)
        
        # 如果不包含已完成的，添加过滤
        if not include_completed:
            queryset = queryset.filter(is_completed=False)
        
        # 如果指定了航班号，添加过滤
        if flight_code:
            queryset = queryset.filter(flight_code=flight_code)
        
        # 如果指定了日期，添加过滤
        if date_str:
            try:
                filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(
                    Q(start_time__date=filter_date) | 
                    Q(end_time__date=filter_date)
                )
            except ValueError:
                # 如果日期格式不正确，忽略此过滤器
                pass
        
        return queryset.order_by('start_time')
    
    def perform_create(self, serializer):
        # 确保passenger字段被设置为当前用户
        serializer.save(passenger=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """标记时间安排完成"""
        schedule = self.get_object()
        schedule.is_completed = True
        schedule.save()
        
        serializer = self.get_serializer(schedule)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """获取今日安排"""
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        schedules = TimeSchedule.objects.filter(
            passenger=request.user,
            start_time__gte=today,
            start_time__lt=tomorrow
        ).order_by('start_time')
        
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """获取即将到来的安排"""
        now = timezone.now()
        later = now + timedelta(hours=4)  # 未来4小时
        
        schedules = TimeSchedule.objects.filter(
            passenger=request.user,
            start_time__gte=now,
            start_time__lte=later,
            is_completed=False
        ).order_by('start_time')
        
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
