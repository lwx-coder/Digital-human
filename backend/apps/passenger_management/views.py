from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination

from .models import PassengerNote, PassengerActivity, PassengerTag, PassengerProfile
from .serializers import (
    PassengerListSerializer,
    PassengerDetailSerializer,
    PassengerNoteSerializer,
    PassengerNoteCreateSerializer,
    PassengerActivitySerializer,
    PassengerTagSerializer,
    PassengerProfileSerializer,
    PassengerProfileUpdateSerializer
)
from apps.items_management.models import LostItem
from apps.items_management.serializers import LostItemListSerializer


User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class IsAdminUser(permissions.BasePermission):
    """仅管理员可访问"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and 'admin' in request.user.get_roles()


class PassengerViewSet(viewsets.ReadOnlyModelViewSet):
    """旅客视图集，提供旅客列表和详情查看功能"""
    queryset = User.objects.filter(roles__name='passenger')
    serializer_class = PassengerListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'phone', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined', 'last_login']
    ordering = ['-date_joined']

    def get_queryset(self):
        """根据查询参数筛选旅客"""
        queryset = User.objects.filter(roles__name='passenger').distinct()
        
        # 根据标签筛选
        tag_id = self.request.query_params.get('tag', None)
        if tag_id:
            queryset = queryset.filter(passenger_profile__tags__id=tag_id)
        
        # 根据VIP等级筛选
        vip_level = self.request.query_params.get('vip_level', None)
        if vip_level:
            queryset = queryset.filter(passenger_profile__vip_level=vip_level)
        
        # 根据活跃状态筛选
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        
        # 根据最近登录时间筛选
        last_login_days = self.request.query_params.get('last_login_days', None)
        if last_login_days:
            try:
                days = int(last_login_days)
                threshold_date = timezone.now() - timezone.timedelta(days=days)
                queryset = queryset.filter(last_login__gte=threshold_date)
            except (ValueError, TypeError):
                pass
        
        return queryset

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'retrieve':
            return PassengerDetailSerializer
        return PassengerListSerializer

    @action(detail=True, methods=['get'])
    def lost_items(self, request, pk=None):
        """获取旅客的失物列表"""
        passenger = self.get_object()
        lost_items = LostItem.objects.filter(reported_by=passenger)
        
        # 分页
        page = self.paginate_queryset(lost_items)
        if page is not None:
            serializer = LostItemListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = LostItemListSerializer(lost_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        """获取旅客的备注列表"""
        passenger = self.get_object()
        notes = PassengerNote.objects.filter(passenger=passenger)
        
        # 分页
        page = self.paginate_queryset(notes)
        if page is not None:
            serializer = PassengerNoteSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PassengerNoteSerializer(notes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """为旅客添加备注"""
        passenger = self.get_object()
        serializer = PassengerNoteCreateSerializer(data={
            'passenger': passenger.id,
            'note': request.data.get('note', '')
        }, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """获取旅客的活动记录"""
        # 当id为空或为'all'时，返回所有旅客的活动记录
        if pk is None or pk == 'all':
            activities = PassengerActivity.objects.all()
        else:
            try:
                passenger = self.get_object()
                activities = PassengerActivity.objects.filter(passenger=passenger)
            except Exception:
                # 如果找不到旅客，也返回所有活动记录
                activities = PassengerActivity.objects.all()
        
        # 根据活动类型筛选
        activity_type = request.query_params.get('type', None)
        if activity_type:
            activities = activities.filter(activity_type=activity_type)
        
        # 排序
        activities = activities.order_by('-created_at')
        
        # 分页
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = PassengerActivitySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PassengerActivitySerializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'put', 'patch'])
    def profile(self, request, pk=None):
        """获取或更新旅客资料"""
        passenger = self.get_object()
        
        # 获取或创建旅客资料
        profile, created = PassengerProfile.objects.get_or_create(passenger=passenger)
        
        if request.method == 'GET':
            serializer = PassengerProfileSerializer(profile)
            return Response(serializer.data)
        
        # 更新资料
        serializer = PassengerProfileUpdateSerializer(profile, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            
            # 记录活动
            PassengerActivity.objects.create(
                passenger=passenger,
                activity_type='profile_update',
                description='管理员更新了旅客资料',
                ip_address=self.get_client_ip(request)
            )
            
            # 返回完整的资料信息
            return Response(PassengerProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PassengerTagViewSet(viewsets.ModelViewSet):
    """旅客标签视图集"""
    queryset = PassengerTag.objects.all()
    serializer_class = PassengerTagSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    @action(detail=True, methods=['get'])
    def passengers(self, request, pk=None):
        """获取使用此标签的旅客列表"""
        tag = self.get_object()
        passengers = User.objects.filter(passenger_profile__tags=tag)
        
        # 分页
        page = self.paginate_queryset(passengers)
        if page is not None:
            serializer = PassengerListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PassengerListSerializer(passengers, many=True)
        return Response(serializer.data)


class PassengerNoteViewSet(viewsets.ModelViewSet):
    """旅客备注视图集"""
    queryset = PassengerNote.objects.all()
    serializer_class = PassengerNoteSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['passenger']
    search_fields = ['note']

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return PassengerNoteCreateSerializer
        return PassengerNoteSerializer

    def perform_create(self, serializer):
        """创建备注时设置创建者"""
        serializer.save(created_by=self.request.user)


class PassengerActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """旅客活动视图集，只读"""
    queryset = PassengerActivity.objects.all()
    serializer_class = PassengerActivitySerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['passenger', 'activity_type']
    search_fields = ['description']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取活动统计信息"""
        # 按类型统计活动数量
        type_stats = PassengerActivity.objects.values('activity_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 按日期统计活动数量
        today = timezone.now().date()
        date_stats = {}
        for i in range(7):
            date = today - timezone.timedelta(days=i)
            count = PassengerActivity.objects.filter(
                created_at__date=date
            ).count()
            date_stats[date.strftime('%Y-%m-%d')] = count
        
        return Response({
            'type_stats': type_stats,
            'date_stats': date_stats
        })
        
    @action(detail=False, methods=['get'], url_path='all/activities')
    def all_activities(self, request):
        """获取所有旅客的活动记录"""
        queryset = self.get_queryset()
        
        # 筛选条件
        passenger_id = request.query_params.get('passenger', None)
        if passenger_id:
            queryset = queryset.filter(passenger_id=passenger_id)
            
        activity_type = request.query_params.get('activity_type', None)
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
            
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(description__icontains=search)
            
        start_date = request.query_params.get('start_date', None)
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
            
        end_date = request.query_params.get('end_date', None)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        # 排序
        queryset = queryset.order_by('-created_at')
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
