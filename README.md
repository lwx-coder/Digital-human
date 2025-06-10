# 智能数字人服务系统

## 项目介绍

本系统是一个面向机场环境的智能数字人服务平台，主要用于在机场繁忙情况下为旅客提供智能化服务。系统结合了数字人技术、自然语言处理和航班信息管理，为旅客提供实时航班信息、登机指引、服务咨询等功能。

## 主要功能

### 用户管理
- 用户注册、登录（支持账号密码和手机验证码两种方式）
- 个人信息管理（包括头像上传、基本信息修改等）
- 密码修改和找回功能
- 多角色权限管理（管理员、普通旅客等）

### 航班服务
- 航班状态实时展示（准点、延误、取消）
- 登机信息提示
- 航班查询功能
- 航班播报记录管理

### 数字人交互
- 智能数字人语音播报
- 欢迎信息和航班信息语音播报
- 通过数字人进行服务引导
- 多场景语音播报（航班信息、失物招领、公告通知）

### 旅客服务
- 旅客信息管理
- 旅客活动记录
- 旅客标签分类
- 旅客资料扩展

### 失物招领
- 失物信息登记
- 失物广播服务
- 失物状态跟踪
- 物品分类管理

### 导航服务
- 机场位置信息管理
- 导航路线规划
- 时间安排管理
- 位置导航记录

### 信息公告
- 公告分类管理
- 紧急通知发布
- 公告播报服务
- 公告有效期管理

### 系统管理
- 用户数据统计
- 访问量和数据量展示
- 数据可视化

## 技术栈

### 前端
- **Vue.js 2.x**：前端核心框架，实现单页面应用
- **Element UI**：UI组件库，提供丰富的组件和统一的设计风格
- **Vuex**：状态管理，集中管理应用的状态数据
- **Vue Router**：路由管理，实现页面导航和组件切换
- **Axios**：HTTP客户端，处理API请求
- **SCSS**：CSS预处理器，提升样式编写效率
- **Lottie**：动画库，实现高质量的矢量动画
- **ECharts**：数据可视化图表库，展示统计数据

### 后端
- **Django 4.2.5**：Python Web框架，提供稳定可靠的后端服务
- **Django REST Framework 3.14.0**：RESTful API框架，简化API开发
- **JWT认证**：使用djangorestframework-simplejwt实现安全的用户认证
- **MySQL**：关系型数据库，存储系统数据
- **Django SimpleUI**：美观的后台管理界面
- **django-filter**：提供高级过滤功能
- **django-cors-headers**：处理跨域资源共享
- **drf-yasg**：API文档生成工具
- **Pillow**：图像处理库，处理用户头像等图片资源

## 安装和使用

### 环境要求
- Node.js 16.13.x 或更高版本
- Python 3.8 或更高版本
- MySQL 5.7 或更高版本

### 前端安装
```bash
# 配置好本地node环境
可参考doc文件夹中nvm安装指引安装nvm管理node版本
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产环境
npm run build
```

### 后端安装
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
或者通过其他虚拟环境管理工具管理虚拟环境

# 配置本地配置信息
在backend/config目录下创建local_settings.py文件，并配置数据库连接信息等
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "your_db_name",
        "USER": "your_db_user",
        "PASSWORD": "your_db_password",
        "HOST": "localhost",
        "PORT": "3306",
    }
}

# 安装依赖
pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 创建MySQL数据库
python backend/create_database.py

# 初始化数据库
python backend/manage.py migrate

# 创建超级用户
python backend/manage.py createsuperuser

# 生成测试数据（可选）
python backend/generate_mock_data.py

# 启动服务
python backend/manage.py runserver
```

## 目录结构
```
├── backend/               # 后端代码
│   ├── apps/              # 应用模块
│   │   ├── users/         # 用户管理模块
│   │   ├── flight_management/  # 航班管理模块
│   │   ├── passenger_management/  # 旅客管理模块
│   │   ├── items_management/  # 失物招领模块
│   │   ├── navigation_management/  # 导航管理模块
│   │   ├── informations/  # 信息公告模块
│   │   └── projects/      # 项目管理模块
│   ├── config/            # 项目配置
│   ├── media/             # 媒体文件目录
│   │   └── avatars/       # 用户头像
│   └── api/               # API接口
├── src/                   # 前端代码
│   ├── api/               # API请求模块
│   ├── assets/            # 静态资源
│   ├── components/        # 公共组件
│   ├── layout/            # 布局组件
│   ├── router/            # 路由配置
│   ├── store/             # Vuex状态管理
│   ├── styles/            # 全局样式
│   └── views/             # 页面组件
│       ├── dashboard/     # 首页
│       ├── login/         # 登录页
│       ├── register/      # 注册页
│       └── profile/       # 个人中心
├── public/                # 公共静态资源
└── build/                 # 构建配置
```







