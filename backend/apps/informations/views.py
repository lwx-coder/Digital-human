from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination

from .models import AnnouncementType, Announcement, AnnouncementBroadcast
from .serializers import (
    AnnouncementTypeSerializer,
    AnnouncementListSerializer,
    AnnouncementDetailSerializer,
    AnnouncementCreateUpdateSerializer,
    AnnouncementBroadcastSerializer,
    AnnouncementBroadcastCreateSerializer
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


class AnnouncementTypeViewSet(viewsets.ModelViewSet):
    """
    公告类型视图集
    提供公告类型的CRUD操作
    """
    queryset = AnnouncementType.objects.all()
    serializer_class = AnnouncementTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    pagination_class = StandardResultsSetPagination


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    公告视图集
    提供公告的CRUD操作
    """
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'priority', 'is_active']
    search_fields = ['title', 'content', 'location']
    ordering_fields = ['priority', 'created_at', 'updated_at', 'start_time', 'end_time']
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """根据操作类型选择合适的序列化器"""
        if self.action == 'list':
            return AnnouncementListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AnnouncementCreateUpdateSerializer
        return AnnouncementDetailSerializer
    
    def get_queryset(self):
        """
        根据用户角色和查询参数，返回不同的queryset
        管理员可以看到所有公告
        旅客只能看到激活状态且在有效期内的公告
        """
        queryset = super().get_queryset()
        
        # 管理员可以看到所有公告
        if 'admin' in self.request.user.get_roles():
            return queryset
        
        # 旅客只能看到激活且在有效期内的公告
        now = timezone.now()
        return queryset.filter(
            is_active=True
        ).filter(
            Q(start_time__isnull=True) | Q(start_time__lte=now)
        ).filter(
            Q(end_time__isnull=True) | Q(end_time__gte=now)
        )
    
    @action(detail=True, methods=['get'])
    def voice_content(self, request, pk=None):
        """获取公告的语音播报内容"""
        announcement = self.get_object()
        return Response({
            'id': announcement.id,
            'title': announcement.title,
            'voice_content': announcement.get_voice_content()
        })
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取当前有效的公告"""
        now = timezone.now()
        queryset = self.get_queryset().filter(
            is_active=True
        ).filter(
            Q(start_time__isnull=True) | Q(start_time__lte=now)
        ).filter(
            Q(end_time__isnull=True) | Q(end_time__gte=now)
        )
        
        # 应用筛选和排序
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AnnouncementListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = AnnouncementListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def emergency(self, request):
        """获取当前紧急通知"""
        now = timezone.now()
        
        # 获取紧急类型ID
        try:
            emergency_type = AnnouncementType.objects.get(name='emergency')
            
            queryset = self.get_queryset().filter(
                type=emergency_type,
                is_active=True,
                priority=3  # 高优先级
            ).filter(
                Q(start_time__isnull=True) | Q(start_time__lte=now)
            ).filter(
                Q(end_time__isnull=True) | Q(end_time__gte=now)
            )
            
            # 应用排序
            queryset = self.filter_queryset(queryset)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = AnnouncementListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
                
            serializer = AnnouncementListSerializer(queryset, many=True)
            return Response(serializer.data)
        except AnnouncementType.DoesNotExist:
            return Response([])


class AnnouncementBroadcastViewSet(viewsets.ModelViewSet):
    """
    公告播报记录视图集
    提供公告播报记录的操作
    """
    queryset = AnnouncementBroadcast.objects.all()
    serializer_class = AnnouncementBroadcastSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['announcement']
    ordering_fields = ['broadcast_at']
    pagination_class = StandardResultsSetPagination
    
    @action(detail=False, methods=['post'])
    def broadcast(self, request):
        """创建公告播报记录并返回播报内容"""
        serializer = AnnouncementBroadcastCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        announcement_id = serializer.validated_data.get('announcement_id')
        announcement = Announcement.objects.get(pk=announcement_id)
        
        # 如果未提供播报内容，则使用公告默认内容
        content = serializer.validated_data.get('content')
        if not content:
            content = announcement.get_voice_content()
        
        # 创建播报记录
        broadcast = AnnouncementBroadcast.objects.create(
            announcement=announcement,
            content=content,
            broadcast_by=request.user
        )
        
        return Response({
            'id': broadcast.id,
            'announcement_title': announcement.title,
            'content': content
        }, status=status.HTTP_201_CREATED)
