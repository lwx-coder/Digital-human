from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemCategoryViewSet, LostItemViewSet, ItemBroadcastViewSet

# 创建路由器
router = DefaultRouter()
router.register(r'categories', ItemCategoryViewSet)
router.register(r'lost-items', LostItemViewSet)
router.register(r'broadcasts', ItemBroadcastViewSet)

# API URL配置
urlpatterns = [
    path('', include(router.urls)),
]
