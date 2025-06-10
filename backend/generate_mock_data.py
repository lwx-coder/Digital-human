#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
为数据库各表生成模拟数据
每个表生成200条数据
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# 导入Faker库
try:
    from faker import Faker
except ImportError:
    print("请先安装Faker库: pip install faker")
    sys.exit(1)

# 导入模型
from django.contrib.auth import get_user_model
from apps.users.models import Role, CustomUser
from apps.flight_management.models import Flight, FlightAnnouncement
from apps.passenger_management.models import PassengerNote, PassengerActivity, PassengerTag, PassengerProfile
from apps.items_management.models import ItemCategory, LostItem, ItemBroadcast
from apps.navigation_management.models import Location, NavigationRecord, TimeSchedule
from apps.informations.models import AnnouncementType, Announcement, AnnouncementBroadcast

# 创建Faker实例，使用中文
fake = Faker('zh_CN')

def clear_data():
    """清除现有数据"""
    print("正在清除现有数据...")
    # 保留系统用户和默认数据，只清除可能是模拟数据的部分
    CustomUser.objects.filter(is_superuser=False, is_staff=False).delete()
    Flight.objects.all().delete()
    FlightAnnouncement.objects.all().delete()
    PassengerNote.objects.all().delete()
    PassengerActivity.objects.all().delete()
    LostItem.objects.all().delete()
    ItemBroadcast.objects.all().delete()
    NavigationRecord.objects.all().delete()
    TimeSchedule.objects.all().delete()
    Announcement.objects.all().delete()
    AnnouncementBroadcast.objects.all().delete()
    print("数据清除完成")

def create_roles():
    """创建角色"""
    print("正在创建角色...")
    Role.get_or_create_default_roles()
    print("角色创建完成")

def create_item_categories():
    """创建物品类别"""
    print("正在创建物品类别...")
    ItemCategory.get_or_create_default_categories()
    print("物品类别创建完成")

def create_announcement_types():
    """创建公告类型"""
    print("正在创建公告类型...")
    AnnouncementType.get_or_create_default_types()
    print("公告类型创建完成")

def create_users(count=200):
    """创建用户"""
    print(f"正在创建{count}个用户...")
    
    # 获取角色
    passenger_role = Role.objects.get(name='passenger')
    admin_role = Role.objects.get(name='admin')
    
    users = []
    for i in range(count):
        username = f"user_{i+1}"
        email = f"user_{i+1}@example.com"
        
        # 检查用户是否已存在
        if CustomUser.objects.filter(username=username).exists():
            continue
            
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password="password123",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone=fake.phone_number(),
            address=fake.address(),
            bio=fake.text(max_nb_chars=200),
            birth_date=fake.date_of_birth(minimum_age=18, maximum_age=80)
        )
        
        # 添加角色
        user.roles.add(passenger_role)
        if i % 20 == 0:  # 每20个用户设置一个管理员
            user.roles.add(admin_role)
            user.is_staff = True
            user.save()
            
        users.append(user)
        
    print(f"创建了{len(users)}个用户")
    return users

def create_passenger_tags(count=10):
    """创建旅客标签"""
    print(f"正在创建{count}个旅客标签...")
    
    tags = []
    tag_names = ["VIP", "常旅客", "头等舱", "商务舱", "经济舱", "特殊需求", "老年人", "儿童", "残障人士", "外国人"]
    colors = ["#ecf5ff", "#f0f9eb", "#fef0f0", "#fdf6ec", "#f4f4f5", "#e6f7ff", "#fff0f6", "#f6ffed", "#fcffe6", "#f9f0ff"]
    
    for i in range(min(count, len(tag_names))):
        tag, created = PassengerTag.objects.get_or_create(
            name=tag_names[i],
            defaults={
                'description': fake.sentence(),
                'color': colors[i]
            }
        )
        tags.append(tag)
        
    print(f"创建了{len(tags)}个旅客标签")
    return tags

def create_passenger_profiles(users, tags):
    """为用户创建旅客资料"""
    print("正在创建旅客资料...")
    
    profiles = []
    for user in users:
        # 检查是否已存在
        profile, created = PassengerProfile.objects.get_or_create(
            passenger=user,
            defaults={
                'frequent_flyer_number': f"FF{fake.random_number(digits=8)}",
                'passport_number': fake.random_number(digits=9),
                'id_card_number': fake.ssn(),
                'emergency_contact': fake.name(),
                'emergency_phone': fake.phone_number(),
                'last_login_ip': fake.ipv4(),
                'vip_level': random.randint(0, 5)
            }
        )
        
        if created:
            # 随机添加1-3个标签
            for tag in random.sample(list(tags), random.randint(1, min(3, len(tags)))):
                profile.tags.add(tag)
                
            profiles.append(profile)
    
    print(f"创建了{len(profiles)}个旅客资料")
    return profiles

def create_flights(count=200):
    """创建航班"""
    print(f"正在创建{count}个航班...")
    
    flights = []
    airlines = ["中国国际航空", "中国东方航空", "中国南方航空", "海南航空", "深圳航空", "厦门航空", "四川航空"]
    cities = ["北京", "上海", "广州", "深圳", "成都", "杭州", "西安", "重庆", "南京", "武汉"]
    airports = ["首都国际机场", "浦东国际机场", "白云国际机场", "宝安国际机场", "双流国际机场", "萧山国际机场", "咸阳国际机场", "江北国际机场", "禄口国际机场", "天河国际机场"]
    statuses = ["scheduled", "delayed", "boarding", "departed", "arrived", "cancelled"]
    
    # 生成未来30天内的航班
    now = timezone.now()
    
    for i in range(count):
        # 随机出发和到达城市，确保不同
        departure_idx = random.randint(0, len(cities) - 1)
        arrival_idx = (departure_idx + random.randint(1, len(cities) - 1)) % len(cities)
        
        # 随机出发时间（未来30天内）
        hours_offset = random.randint(1, 30*24)
        departure_time = now + timedelta(hours=hours_offset)
        
        # 随机飞行时间（1-5小时）
        flight_duration = random.randint(1, 5)
        arrival_time = departure_time + timedelta(hours=flight_duration)
        
        # 航班号
        airline_code = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(2))
        flight_number = f"{airline_code}{random.randint(1000, 9999)}"
        
        # 随机状态
        status = random.choice(statuses)
        
        # 实际时间（如果状态不是计划中）
        actual_departure_time = None
        actual_arrival_time = None
        if status != 'scheduled':
            if status in ['delayed']:
                actual_departure_time = departure_time + timedelta(minutes=random.randint(30, 180))
                actual_arrival_time = actual_departure_time + timedelta(hours=flight_duration)
            elif status in ['boarding', 'departed', 'arrived']:
                actual_departure_time = departure_time
                actual_arrival_time = arrival_time
        
        flight = Flight.objects.create(
            flight_number=flight_number,
            airline=random.choice(airlines),
            departure_city=cities[departure_idx],
            arrival_city=cities[arrival_idx],
            departure_airport=airports[departure_idx],
            arrival_airport=airports[arrival_idx],
            scheduled_departure_time=departure_time,
            scheduled_arrival_time=arrival_time,
            actual_departure_time=actual_departure_time,
            actual_arrival_time=actual_arrival_time,
            gate=f"G{random.randint(1, 50)}",
            terminal=f"T{random.randint(1, 3)}",
            status=status
        )
        flights.append(flight)
    
    print(f"创建了{len(flights)}个航班")
    return flights

def create_flight_announcements(flights, users, count=200):
    """创建航班播报记录"""
    print(f"正在创建{count}个航班播报记录...")
    
    announcements = []
    admin_users = [user for user in users if user.is_staff]
    
    for i in range(count):
        flight = random.choice(flights)
        
        announcement = FlightAnnouncement.objects.create(
            flight=flight,
            content=flight.get_status_display_for_voice()
        )
        announcements.append(announcement)
    
    print(f"创建了{len(announcements)}个航班播报记录")
    return announcements

def create_passenger_notes(users, count=200):
    """创建旅客备注"""
    print(f"正在创建{count}个旅客备注...")
    
    notes = []
    admin_users = [user for user in users if user.is_staff]
    
    if not admin_users:
        print("没有管理员用户，跳过创建旅客备注")
        return notes
    
    for i in range(count):
        passenger = random.choice(users)
        created_by = random.choice(admin_users)
        
        note = PassengerNote.objects.create(
            passenger=passenger,
            note=fake.paragraph(),
            created_by=created_by
        )
        notes.append(note)
    
    print(f"创建了{len(notes)}个旅客备注")
    return notes

def create_passenger_activities(users, count=200):
    """创建旅客活动记录"""
    print(f"正在创建{count}个旅客活动记录...")
    
    activities = []
    activity_types = ['login', 'logout', 'profile_update', 'flight_booking', 'flight_checkin', 'lost_item_report', 'other']
    
    for i in range(count):
        passenger = random.choice(users)
        activity_type = random.choice(activity_types)
        
        activity = PassengerActivity.objects.create(
            passenger=passenger,
            activity_type=activity_type,
            description=fake.sentence(),
            ip_address=fake.ipv4(),
            user_agent=fake.user_agent()
        )
        activities.append(activity)
    
    print(f"创建了{len(activities)}个旅客活动记录")
    return activities

def create_locations(count=50):
    """创建位置信息"""
    print(f"正在创建{count}个位置信息...")
    
    locations = []
    location_types = ['gate', 'shop', 'restaurant', 'toilet', 'security', 'check_in', 'luggage', 'exit', 'entrance', 'lounge', 'other']
    
    for i in range(count):
        location_type = random.choice(location_types)
        
        # 根据类型生成名称
        if location_type == 'gate':
            name = f"登机口 {random.choice('ABCDEFG')}{random.randint(1, 30)}"
        elif location_type == 'shop':
            shops = ["免税店", "书店", "便利店", "服装店", "化妆品店", "电子产品店", "纪念品店"]
            name = f"{random.choice(shops)} {random.randint(1, 10)}号"
        elif location_type == 'restaurant':
            restaurants = ["咖啡厅", "快餐店", "中餐厅", "西餐厅", "日料店", "面包店"]
            name = f"{random.choice(restaurants)} {random.randint(1, 10)}号"
        elif location_type == 'toilet':
            name = f"{random.randint(1, 5)}层 {random.choice(['男', '女', '无障碍'])}卫生间 {random.randint(1, 10)}号"
        elif location_type == 'security':
            name = f"安检口 {random.randint(1, 10)}号"
        elif location_type == 'check_in':
            name = f"值机柜台 {random.choice('ABCDEFG')}{random.randint(1, 50)}"
        else:
            name = f"{location_type} {random.randint(1, 20)}号"
        
        location = Location.objects.create(
            name=name,
            description=fake.sentence(),
            floor=random.randint(1, 5),
            x_coordinate=random.uniform(0, 1000),
            y_coordinate=random.uniform(0, 1000),
            type=location_type,
            is_active=random.choice([True, True, True, False])  # 75%概率为活跃状态
        )
        locations.append(location)
    
    print(f"创建了{len(locations)}个位置信息")
    return locations

def create_navigation_records(users, locations, count=200):
    """创建导航记录"""
    print(f"正在创建{count}个导航记录...")
    
    records = []
    
    for i in range(count):
        passenger = random.choice(users)
        
        # 随机选择两个不同的位置
        loc_indices = random.sample(range(len(locations)), 2)
        start_location = locations[loc_indices[0]]
        end_location = locations[loc_indices[1]]
        
        # 创建时间（过去30天内）
        created_at = timezone.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        
        # 随机距离和时间
        distance = random.randint(50, 2000)  # 50-2000米
        estimated_time = distance // 50  # 粗略估计：每50米1分钟
        
        # 是否完成
        completed = random.choice([True, True, False])  # 2/3概率已完成
        completed_at = None
        if completed:
            completed_at = created_at + timedelta(minutes=random.randint(1, estimated_time*2))
        
        record = NavigationRecord.objects.create(
            passenger=passenger,
            start_location=start_location,
            end_location=end_location,
            created_at=created_at,
            estimated_time=estimated_time,
            distance=distance,
            completed=completed,
            completed_at=completed_at
        )
        records.append(record)
    
    print(f"创建了{len(records)}个导航记录")
    return records

def create_time_schedules(users, locations, count=200):
    """创建时间安排"""
    print(f"正在创建{count}个时间安排...")
    
    schedules = []
    event_types = ['check_in', 'security', 'boarding', 'shopping', 'dining', 'resting', 'other']
    
    for i in range(count):
        passenger = random.choice(users)
        location = random.choice(locations)
        event_type = random.choice(event_types)
        
        # 事件名称
        if event_type == 'check_in':
            event_name = "办理登机手续"
        elif event_type == 'security':
            event_name = "通过安检"
        elif event_type == 'boarding':
            event_name = "登机"
        elif event_type == 'shopping':
            event_name = f"在{location.name}购物"
        elif event_type == 'dining':
            event_name = f"在{location.name}用餐"
        elif event_type == 'resting':
            event_name = "休息"
        else:
            event_name = fake.sentence(nb_words=3)
        
        # 随机时间（未来7天内）
        start_time = timezone.now() + timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
        end_time = start_time + timedelta(minutes=random.randint(15, 120))
        
        # 是否完成
        is_completed = start_time < timezone.now()
        
        schedule = TimeSchedule.objects.create(
            passenger=passenger,
            flight_code=f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1000, 9999)}",
            event_name=event_name,
            event_type=event_type,
            location=location,
            start_time=start_time,
            end_time=end_time,
            notes=fake.sentence() if random.choice([True, False]) else None,
            is_completed=is_completed
        )
        schedules.append(schedule)
    
    print(f"创建了{len(schedules)}个时间安排")
    return schedules

def create_lost_items(users, count=200):
    """创建失物信息"""
    print(f"正在创建{count}个失物信息...")
    
    lost_items = []
    statuses = ['lost', 'found', 'claimed', 'closed']
    
    # 获取所有物品类别
    categories = list(ItemCategory.objects.all())
    if not categories:
        print("没有物品类别，跳过创建失物信息")
        return lost_items
    
    for i in range(count):
        reporter = random.choice(users)
        category = random.choice(categories)
        
        # 根据类别生成物品名称
        if category.name == 'electronic':
            items = ["手机", "笔记本电脑", "平板电脑", "耳机", "充电器", "相机", "智能手表"]
            title = random.choice(items)
        elif category.name == 'luggage':
            items = ["行李箱", "背包", "手提包", "钱包", "公文包", "化妆包"]
            title = random.choice(items)
        elif category.name == 'document':
            items = ["护照", "身份证", "驾驶证", "登机牌", "信用卡", "现金"]
            title = random.choice(items)
        elif category.name == 'clothing':
            items = ["外套", "帽子", "围巾", "手套", "鞋子", "眼镜"]
            title = random.choice(items)
        elif category.name == 'accessories':
            items = ["手表", "项链", "戒指", "耳环", "手链", "领带"]
            title = random.choice(items)
        else:
            title = fake.word() + random.choice(["", "包", "盒", "套"])
        
        # 随机丢失时间（过去30天内）
        lost_time = timezone.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        
        # 随机状态
        status = random.choice(statuses)
        
        lost_item = LostItem.objects.create(
            title=title,
            category=category,
            description=fake.paragraph(),
            lost_time=lost_time,
            lost_location=fake.word() + random.choice(["候机厅", "登机口", "安检处", "行李提取处", "卫生间", "商店", "餐厅"]),
            contact_name=fake.name(),
            contact_phone=fake.phone_number(),
            contact_email=fake.email() if random.choice([True, False]) else None,
            image=f"https://picsum.photos/id/{random.randint(1, 1000)}/200/200" if random.choice([True, False]) else None,
            reported_by=reporter,
            status=status,
            is_broadcasted=random.choice([True, False]),
            admin_notes=fake.paragraph() if random.choice([True, False]) else None
        )
        lost_items.append(lost_item)
    
    print(f"创建了{len(lost_items)}个失物信息")
    return lost_items

def create_item_broadcasts(lost_items, users, count=200):
    """创建物品广播记录"""
    print(f"正在创建{count}个物品广播记录...")
    
    broadcasts = []
    admin_users = [user for user in users if user.is_staff]
    
    if not admin_users or not lost_items:
        print("没有管理员用户或失物信息，跳过创建物品广播记录")
        return broadcasts
    
    for i in range(min(count, len(lost_items))):
        lost_item = lost_items[i]
        broadcast_by = random.choice(admin_users)
        
        broadcast = ItemBroadcast.objects.create(
            lost_item=lost_item,
            content=lost_item.get_broadcast_content(),
            broadcast_by=broadcast_by
        )
        broadcasts.append(broadcast)
    
    print(f"创建了{len(broadcasts)}个物品广播记录")
    return broadcasts

def create_announcements(users, count=200):
    """创建公告信息"""
    print(f"正在创建{count}个公告信息...")
    
    announcements = []
    priorities = [1, 2, 2, 3]  # 更多的中等优先级
    
    # 获取所有公告类型
    types = list(AnnouncementType.objects.all())
    if not types:
        print("没有公告类型，跳过创建公告信息")
        return announcements
    
    admin_users = [user for user in users if user.is_staff]
    if not admin_users:
        print("没有管理员用户，跳过创建公告信息")
        return announcements
    
    for i in range(count):
        announcement_type = random.choice(types)
        created_by = random.choice(admin_users)
        
        # 根据类型生成标题和内容
        if announcement_type.name == 'emergency':
            titles = ["紧急通知", "安全警告", "紧急疏散", "紧急情况"]
            title = random.choice(titles)
            content = fake.paragraph()
        elif announcement_type.name == 'regular':
            titles = ["日常通知", "服务信息", "航班信息", "机场通知"]
            title = random.choice(titles)
            content = fake.paragraph()
        elif announcement_type.name == 'congestion':
            titles = ["拥堵预警", "人流密集", "排队提醒"]
            title = random.choice(titles)
            content = f"{fake.word()}区域人流密集，请旅客避开高峰时段。" + fake.sentence()
        elif announcement_type.name == 'gate_change':
            titles = ["登机口变更", "航站楼变更", "值机柜台变更"]
            title = random.choice(titles)
            content = f"航班{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1000, 9999)}的{title}为{random.choice('ABCDEFG')}{random.randint(1, 30)}。" + fake.sentence()
        else:
            title = fake.sentence(nb_words=4)
            content = fake.paragraph()
        
        # 随机时间范围（过去7天到未来30天）
        now = timezone.now()
        start_time = now - timedelta(days=random.randint(0, 7))
        end_time = now + timedelta(days=random.randint(1, 30))
        
        announcement = Announcement.objects.create(
            title=title,
            content=content,
            type=announcement_type,
            priority=random.choice(priorities),
            is_active=random.choice([True, True, True, False]),  # 75%概率为活跃状态
            start_time=start_time,
            end_time=end_time,
            location=fake.word() + random.choice(["候机厅", "登机口", "安检处", "行李提取处", "卫生间", "商店", "餐厅"]) if random.choice([True, False]) else None,
            created_by=created_by
        )
        announcements.append(announcement)
    
    print(f"创建了{len(announcements)}个公告信息")
    return announcements

def create_announcement_broadcasts(announcements, users, count=200):
    """创建公告播报记录"""
    print(f"正在创建{count}个公告播报记录...")
    
    broadcasts = []
    admin_users = [user for user in users if user.is_staff]
    
    if not admin_users or not announcements:
        print("没有管理员用户或公告信息，跳过创建公告播报记录")
        return broadcasts
    
    for i in range(min(count, len(announcements))):
        announcement = announcements[i]
        broadcast_by = random.choice(admin_users)
        
        broadcast = AnnouncementBroadcast.objects.create(
            announcement=announcement,
            content=announcement.get_voice_content(),
            broadcast_by=broadcast_by
        )
        broadcasts.append(broadcast)
    
    print(f"创建了{len(broadcasts)}个公告播报记录")
    return broadcasts

def main():
    """主函数"""
    print("开始生成模拟数据...")
    
    # 清除现有数据
    clear_data()
    
    # 创建默认数据
    create_roles()
    create_item_categories()
    create_announcement_types()
    
    # 创建用户和相关数据
    users = create_users(count=200)
    tags = create_passenger_tags()
    profiles = create_passenger_profiles(users, tags)
    
    # 创建航班和相关数据
    flights = create_flights(count=200)
    flight_announcements = create_flight_announcements(flights, users, count=200)
    
    # 创建旅客相关数据
    passenger_notes = create_passenger_notes(users, count=200)
    passenger_activities = create_passenger_activities(users, count=200)
    
    # 创建位置和导航相关数据
    locations = create_locations(count=50)
    navigation_records = create_navigation_records(users, locations, count=200)
    time_schedules = create_time_schedules(users, locations, count=200)
    
    # 创建失物和公告相关数据
    lost_items = create_lost_items(users, count=200)
    item_broadcasts = create_item_broadcasts(lost_items, users, count=200)
    announcements = create_announcements(users, count=200)
    announcement_broadcasts = create_announcement_broadcasts(announcements, users, count=200)
    
    print("模拟数据生成完成！")

if __name__ == "__main__":
    main() 