## API接口说明

### 用户认证接口
- `/api/users/login/` - 用户登录（POST）
- `/api/users/logout/` - 用户登出（POST）
- `/api/users/register/` - 用户注册（POST）
- `/api/users/info/` - 获取用户信息（GET）
- `/api/users/me/` - 获取当前用户详情（GET）
- `/api/users/update_me/` - 更新当前用户信息（PUT/PATCH）

### 航班相关接口
- `/api/flight-management/flights/` - 航班列表（GET）和创建（POST）
- `/api/flight-management/flights/{id}/` - 航班详情、更新和删除
- `/api/flight-management/announcements/` - 航班播报记录

### 旅客相关接口
- `/api/passenger-management/passengers/` - 旅客列表
- `/api/passenger-management/passengers/{id}/` - 旅客详情
- `/api/passenger-management/passengers/{id}/activities/` - 旅客活动记录
- `/api/passenger-management/passengers/all/activities/` - 所有旅客活动记录
- `/api/passenger-management/tags/` - 旅客标签管理

### 失物招领接口
- `/api/items-management/categories/` - 物品类别管理
- `/api/items-management/lost-items/` - 失物信息管理
- `/api/items-management/broadcasts/` - 失物广播记录

### 导航相关接口
- `/api/navigation-management/locations/` - 位置信息管理
- `/api/navigation-management/records/` - 导航记录管理
- `/api/navigation-management/schedules/` - 时间安排管理

### 信息公告接口
- `/api/informations/types/` - 公告类型管理
- `/api/informations/announcements/` - 公告信息管理
- `/api/informations/broadcasts/` - 公告播报记录

## 数据模型关系

### 用户模型
- `CustomUser` - 扩展Django用户模型，添加手机号、地址、头像等字段
- `Role` - 用户角色模型，如旅客、管理员等

### 航班模型
- `Flight` - 航班信息模型，包含航班号、航空公司、出发/到达城市等信息
- `FlightAnnouncement` - 航班播报记录模型，记录数字人播报内容

### 旅客模型
- `PassengerProfile` - 旅客资料模型，存储旅客扩展信息
- `PassengerActivity` - 旅客活动记录模型
- `PassengerNote` - 旅客备注模型
- `PassengerTag` - 旅客标签模型

### 失物招领模型
- `ItemCategory` - 物品类别模型
- `LostItem` - 失物信息模型
- `ItemBroadcast` - 物品广播记录模型

### 导航模型
- `Location` - 位置信息模型
- `NavigationRecord` - 导航记录模型
- `TimeSchedule` - 时间安排模型

### 信息公告模型
- `AnnouncementType` - 公告类型模型
- `Announcement` - 公告信息模型
- `AnnouncementBroadcast` - 公告播报记录模型