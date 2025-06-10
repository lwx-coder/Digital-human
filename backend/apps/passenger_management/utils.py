from .models import PassengerActivity
from django.contrib.auth import get_user_model

User = get_user_model()


def record_passenger_activity(passenger, activity_type, description='', request=None):
    """
    记录旅客活动
    
    Args:
        passenger: 旅客用户对象
        activity_type: 活动类型，必须是PassengerActivity.ACTIVITY_TYPES中的一种
        description: 活动描述
        request: HTTP请求对象，用于获取IP地址和用户代理
    
    Returns:
        创建的活动记录对象
    """
    # 验证用户是旅客
    if not isinstance(passenger, User) or 'passenger' not in passenger.get_roles():
        return None
    
    # 创建活动记录
    activity_data = {
        'passenger': passenger,
        'activity_type': activity_type,
        'description': description
    }
    
    # 如果有请求对象，添加IP和用户代理
    if request:
        activity_data['ip_address'] = get_client_ip(request)
        activity_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
    
    # 创建并返回活动记录
    return PassengerActivity.objects.create(**activity_data)


def get_client_ip(request):
    """
    获取客户端IP地址
    
    Args:
        request: HTTP请求对象
    
    Returns:
        客户端IP地址字符串
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_passenger_profile_if_not_exists(user):
    """
    如果用户没有旅客资料，则创建一个
    
    Args:
        user: 用户对象
    
    Returns:
        旅客资料对象
    """
    from .models import PassengerProfile
    
    if not isinstance(user, User) or 'passenger' not in user.get_roles():
        return None
        
    profile, created = PassengerProfile.objects.get_or_create(passenger=user)
    return profile 