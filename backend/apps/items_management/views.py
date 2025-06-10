from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination

from .models import ItemCategory, LostItem, ItemBroadcast
from .serializers import (
    ItemCategorySerializer,
    LostItemListSerializer,
    LostItemDetailSerializer,
    LostItemCreateUpdateSerializer,
    ItemBroadcastSerializer,
    ItemBroadcastCreateSerializer
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


class ItemCategoryViewSet(viewsets.ModelViewSet):
    """
    物品类别视图集
    提供物品类别的CRUD操作
    """
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    pagination_class = StandardResultsSetPagination


class LostItemViewSet(viewsets.ModelViewSet):
    """
    失物信息视图集
    提供失物信息的CRUD操作
    """
    queryset = LostItem.objects.all()
    serializer_class = LostItemDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_broadcasted']
    search_fields = ['title', 'description', 'lost_location', 'contact_name']
    ordering_fields = ['lost_time', 'created_at', 'updated_at']
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """根据操作类型选择合适的序列化器"""
        if self.action == 'list':
            return LostItemListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return LostItemCreateUpdateSerializer
        return LostItemDetailSerializer
    
    def get_queryset(self):
        """
        根据用户角色获取不同的查询集
        管理员可以看到所有失物信息
        旅客只能看到自己报失的物品
        """
        queryset = super().get_queryset()
        
        # 管理员可以看到所有失物信息
        if 'admin' in self.request.user.get_roles():
            return queryset
        
        # 旅客只能看到自己报失的物品
        return queryset.filter(reported_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def broadcast_content(self, request, pk=None):
        """获取失物广播内容"""
        lost_item = self.get_object()
        return Response({
            'id': lost_item.id,
            'title': lost_item.title,
            'broadcast_content': lost_item.get_broadcast_content()
        })
    
    @action(detail=False, methods=['get'])
    def my_items(self, request):
        """获取用户自己报失的物品"""
        queryset = self.get_queryset().filter(reported_by=request.user)
        
        # 应用筛选和排序
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = LostItemListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = LostItemListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """获取待处理的失物信息（管理员使用）"""
        if 'admin' not in request.user.get_roles():
            return Response({"error": "权限不足，仅管理员可访问"}, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset().filter(
            status='lost',
            is_broadcasted=False
        )
        
        # 应用筛选和排序
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = LostItemListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = LostItemListSerializer(queryset, many=True)
        return Response(serializer.data)


class ItemBroadcastViewSet(viewsets.ModelViewSet):
    """
    物品广播记录视图集
    提供物品广播记录的操作
    """
    queryset = ItemBroadcast.objects.all()
    serializer_class = ItemBroadcastSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['lost_item']
    ordering_fields = ['broadcast_at']
    pagination_class = StandardResultsSetPagination
    
    @action(detail=False, methods=['post'])
    def broadcast(self, request):
        """创建广播记录并返回广播内容"""
        # 仅管理员可以广播
        if 'admin' not in request.user.get_roles():
            return Response({"error": "权限不足，仅管理员可广播"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ItemBroadcastCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        lost_item_id = serializer.validated_data.get('lost_item_id')
        lost_item = LostItem.objects.get(pk=lost_item_id)
        
        # 如果未提供广播内容，则使用默认内容
        content = serializer.validated_data.get('content')
        if not content:
            content = lost_item.get_broadcast_content()
        
        # 创建广播记录
        broadcast = ItemBroadcast.objects.create(
            lost_item=lost_item,
            content=content,
            broadcast_by=request.user
        )
        
        # 更新失物信息为已广播
        lost_item.is_broadcasted = True
        lost_item.save()
        
        return Response({
            'id': broadcast.id,
            'lost_item_title': lost_item.title,
            'content': content
        }, status=status.HTTP_201_CREATED)
