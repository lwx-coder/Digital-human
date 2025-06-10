from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PassengerViewSet,
    PassengerTagViewSet,
    PassengerNoteViewSet,
    PassengerActivityViewSet
)

# 创建路由器
router = DefaultRouter()
router.register(r'passengers', PassengerViewSet)
router.register(r'tags', PassengerTagViewSet)
router.register(r'notes', PassengerNoteViewSet)
router.register(r'activities', PassengerActivityViewSet)

# API URL配置
urlpatterns = [
    # 添加特殊路径 - 必须放在router.urls之前，以确保优先匹配
    path('passengers/all/activities/', PassengerViewSet.as_view({'get': 'activities'}), name='passenger-all-activities'),
    # 包含路由器生成的URL
    path('', include(router.urls)),
]
