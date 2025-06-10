from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'navigation_management'

router = DefaultRouter()
router.register('locations', views.LocationViewSet, basename='location')
router.register('navigations', views.NavigationRecordViewSet, basename='navigation')
router.register('schedules', views.TimeScheduleViewSet, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
] 