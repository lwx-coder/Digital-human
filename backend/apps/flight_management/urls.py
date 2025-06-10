from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'flight_management'

router = DefaultRouter()
router.register('flights', views.FlightViewSet, basename='flights')
router.register('announcements', views.FlightAnnouncementViewSet, basename='announcements')
router.register('passenger', views.PassengerFlightViewSet, basename='passenger')

urlpatterns = [
    # 其他自定义路由可以在这里添加
]

urlpatterns += router.urls
