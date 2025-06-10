from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from .models import Flight, FlightAnnouncement
from .serializers import (
    FlightSerializer, 
    FlightListSerializer, 
    FlightAnnouncementSerializer,
    FlightAnnouncementCreateSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    自定义权限：仅管理员可以编辑，其他角色只读
    """
    def has_permission(self, request, view):
        # 所有角色可以读取
        if request.method in permissions.SAFE_METHODS:
            return True
        # 只有管理员可以修改
        return 'admin' in request.user.get_roles()


class FlightViewSet(viewsets.ModelViewSet):
    """
    航班信息视图集，提供航班信息的CRUD操作
    仅管理员可以添加、修改、删除航班
    所有已登录用户可以查看航班信息
    """
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['flight_number', 'airline', 'departure_city', 'arrival_city', 'status']
    search_fields = ['flight_number', 'airline', 'departure_city', 'arrival_city']
    ordering_fields = ['scheduled_departure_time', 'scheduled_arrival_time', 'created_at', 'updated_at']
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """根据操作类型选择合适的序列化器"""
        if self.action == 'list':
            return FlightListSerializer
        return FlightSerializer
    
    @action(detail=True, methods=['get'])
    def voice_status(self, request, pk=None):
        """获取航班状态的语音播报信息"""
        flight = self.get_object()
        return Response({
            'flight_number': flight.flight_number,
            'voice_content': flight.get_status_display_for_voice()
        })
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """搜索航班信息"""
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "请提供搜索关键字"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 全文搜索航班信息
        queryset = self.get_queryset().filter(
            Q(flight_number__icontains=query) |
            Q(airline__icontains=query) |
            Q(departure_city__icontains=query) |
            Q(arrival_city__icontains=query) |
            Q(departure_airport__icontains=query) |
            Q(arrival_airport__icontains=query)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FlightListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = FlightListSerializer(queryset, many=True)
        return Response(serializer.data)


class PassengerFlightViewSet(viewsets.GenericViewSet):
    """
    旅客航班视图集
    提供旅客选择航班、查看选择航班等功能
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    @action(detail=True, methods=['post'])
    def select(self, request, pk=None):
        """旅客选择航班"""
        try:
            flight = Flight.objects.get(pk=pk)
        except Flight.DoesNotExist:
            return Response({"error": "航班不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        # 获取当前用户和关联的旅客信息
        user = request.user
        
        # 将航班与用户关联 (保存到用户元数据中)
        user_meta = []
        if hasattr(user, 'selected_flights') and isinstance(user.selected_flights, list):
            user_meta = user.selected_flights
        
        # 检查是否已经选择
        flight_id = str(flight.id)
        if flight_id not in user_meta:
            user_meta.append(flight_id)
            
            # 更新用户元数据
            user.selected_flights = user_meta
            
            # 保存更新
            user.save()
        
        return Response({"message": f"已成功选择航班 {flight.flight_number}"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def unselect(self, request, pk=None):
        """旅客取消选择航班"""
        try:
            flight = Flight.objects.get(pk=pk)
        except Flight.DoesNotExist:
            return Response({"error": "航班不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        # 获取当前用户
        user = request.user
        
        # 从用户元数据中移除航班
        user_meta = []
        if hasattr(user, 'selected_flights') and isinstance(user.selected_flights, list):
            user_meta = user.selected_flights
            flight_id = str(flight.id)
            
            if flight_id in user_meta:
                user_meta.remove(flight_id)
                user.selected_flights = user_meta
                user.save()
        
        return Response({"message": f"已取消选择航班 {flight.flight_number}"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def my_flights(self, request):
        """获取旅客选择的航班列表"""
        user = request.user
        
        if not hasattr(user, 'selected_flights') or not user.selected_flights or not isinstance(user.selected_flights, list):
            return Response([])
        
        # 获取已选择的航班
        flight_ids = user.selected_flights
        flights = Flight.objects.filter(id__in=flight_ids)
        
        # 分页
        page = self.paginate_queryset(flights)
        if page is not None:
            serializer = FlightListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = FlightListSerializer(flights, many=True)
        return Response(serializer.data)


class FlightAnnouncementViewSet(viewsets.ModelViewSet):
    """
    航班播报视图集
    提供航班播报的CRUD操作
    """
    queryset = FlightAnnouncement.objects.all()
    serializer_class = FlightAnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['flight']
    ordering_fields = ['created_at']
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """根据操作类型选择合适的序列化器"""
        if self.action == 'create':
            return FlightAnnouncementCreateSerializer
        return FlightAnnouncementSerializer
    
    @action(detail=False, methods=['post'])
    def announce(self, request):
        """创建航班播报记录并返回播报内容"""
        serializer = FlightAnnouncementCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        flight_number = serializer.validated_data.get('flight_number')
        flight = Flight.objects.get(flight_number=flight_number)
        
        # 如果未提供播报内容，则使用默认的状态播报
        content = serializer.validated_data.get('content')
        if not content:
            content = flight.get_status_display_for_voice()
        
        # 创建播报记录
        announcement = FlightAnnouncement.objects.create(
            flight=flight,
            content=content
        )
        
        return Response({
            'flight_number': flight.flight_number,
            'content': content,
            'id': announcement.id
        }, status=status.HTTP_201_CREATED)
