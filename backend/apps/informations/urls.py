from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'informations'

router = DefaultRouter()
router.register('announcement-types', views.AnnouncementTypeViewSet, basename='announcement-types')
router.register('announcements', views.AnnouncementViewSet, basename='announcements')
router.register('broadcasts', views.AnnouncementBroadcastViewSet, basename='broadcasts')

urlpatterns = [
    # 其他自定义路由可以在这里添加
]

urlpatterns += router.urls
