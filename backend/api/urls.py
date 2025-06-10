from django.urls import path, include
from django.conf import settings

app_name = 'api'

urlpatterns = [
    # 在这里添加API路由
    path('users/', include(('apps.users.urls', 'apps.users'), namespace='users')),
    path('flight-management/', include(('apps.flight_management.urls', 'apps.flight_management'), namespace='flight_management')),
    path('informations/', include(('apps.informations.urls', 'apps.informations'), namespace='informations')),
    path('items-management/', include(('apps.items_management.urls', 'apps.items_management'), namespace='items_management')),
    path('passenger-management/', include(('apps.passenger_management.urls', 'apps.passenger_management'), namespace='passenger_management')),
    path('navigation-management/', include(('apps.navigation_management.urls', 'apps.navigation_management'), namespace='navigation_management')),
]

# 如果启用RBAC，则添加权限管理模块的URL
if getattr(settings, 'ENABLE_RBAC', False):
    urlpatterns.append(
        path('auth/', include(('apps.auth.urls', 'apps.auth'), namespace='rbac'))
    ) 