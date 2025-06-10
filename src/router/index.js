import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'/'el-icon-x' the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * 所有路由配置，通过meta.roles控制权限
 */
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },
  {
    path: '/register',
    component: () => import('@/views/register/index'),
    hidden: true
  },
  {
    path: '/forget-password',
    component: () => import('@/views/forget-password/index'),
    hidden: true
  },
  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },
  {
    path: '/401',
    component: () => import('@/views/401'),
    hidden: true
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [{
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index'),
      meta: { title: '首页', icon: 'dashboard', roles: ['admin', 'passenger'] }
    }]
  },
  {
    path: '/profile',
    component: Layout,
    hidden: true,
    children: [
      {
        path: '',
        name: 'Profile',
        component: () => import('@/views/profile/index'),
        meta: { title: '个人中心', icon: 'user', roles: ['admin', 'passenger'] }
      }
    ]
  },
  {
    path: '/flight-management',
    component: Layout,
    meta: { title: '航班管理', icon: 'link' },
    children: [
      {
        path: 'admin/flight',
        name: 'AdminFlightManagement',
        component: () => import('@/views/admin/flight/index'),
        meta: { title: '航班信息管理', icon: 'plane', roles: ['admin'] }
      },
      {
        path: 'passenger/flight',
        name: 'PassengerFlightQuery',
        component: () => import('@/views/passenger/flight/index'),
        meta: { title: '航班信息查询', icon: 'search', roles: ['passenger'] }
      },
      {
        path: 'passenger/my-flights',
        name: 'MyFlights',
        component: () => import('@/views/passenger/flight/my-flights'),
        meta: { title: '我的航班', icon: 'ticket', roles: ['passenger'] }
      },
      {
        path: 'admin/flight/add',
        name: 'AddFlight',
        component: () => import('@/views/admin/flight/add'),
        meta: { title: '添加航班', icon: 'add', roles: ['admin'] },
        hidden: true
      },
      {
        path: 'admin/flight/edit/:id',
        name: 'EditFlight',
        component: () => import('@/views/admin/flight/edit'),
        meta: { title: '编辑航班', icon: 'edit', roles: ['admin'] },
        hidden: true
      },
      {
        path: 'admin/flight/detail/:id',
        name: 'FlightDetail',
        component: () => import('@/views/admin/flight/detail'),
        meta: { title: '航班详情', icon: 'detail', roles: ['admin'] },
        hidden: true
      },
      {
        path: 'passenger/flight/detail/:id',
        name: 'PassengerFlightDetail',
        component: () => import('@/views/passenger/flight/detail'),
        meta: { title: '航班详情', icon: 'detail', roles: ['passenger'] },
        hidden: true
      }
    ]
  },
  {
    path: '/announcement',
    component: Layout,
    meta: { title: '信息公告', icon: 'el-icon-bell' },
    children: [
      {
        path: 'admin/list',
        name: 'AdminAnnouncementList',
        component: () => import('@/views/admin/announcement/index'),
        meta: { title: '公告管理', icon: 'el-icon-message', roles: ['admin'] }
      },
      {
        path: 'admin/add',
        name: 'AddAnnouncement',
        component: () => import('@/views/admin/announcement/add'),
        meta: { title: '添加公告', icon: 'el-icon-plus', roles: ['admin'] },
        hidden: true
      },
      {
        path: 'admin/edit/:id',
        name: 'EditAnnouncement',
        component: () => import('@/views/admin/announcement/edit'),
        meta: { title: '编辑公告', icon: 'el-icon-edit', roles: ['admin'] },
        hidden: true
      },
      {
        path: 'admin/detail/:id',
        name: 'AdminAnnouncementDetail',
        component: () => import('@/views/admin/announcement/detail'),
        meta: { title: '公告详情', icon: 'el-icon-document', roles: ['admin'] },
        hidden: true
      },
      {
        path: 'passenger/list',
        name: 'PassengerAnnouncementList',
        component: () => import('@/views/passenger/announcement/index'),
        meta: { title: '公告信息', icon: 'el-icon-bell', roles: ['passenger'] }
      },
      {
        path: 'passenger/detail/:id',
        name: 'PassengerAnnouncementDetail',
        component: () => import('@/views/passenger/announcement/detail'),
        meta: { title: '公告详情', icon: 'el-icon-document', roles: ['passenger'] },
        hidden: true
      }
    ]
  },
  {
    path: '/lost-item',
    component: Layout,
    meta: { title: '失物招领', icon: 'el-icon-suitcase' },
    children: [
      {
        path: 'admin/list',
        name: 'AdminLostItemList',
        component: () => import('@/views/admin/lost-item/index'),
        meta: { title: '失物管理', icon: 'el-icon-collection', roles: ['admin'] }
      },
      {
        path: 'admin/detail/:id',
        name: 'AdminLostItemDetail',
        component: () => import('@/views/admin/lost-item/detail'),
        meta: { title: '失物详情', icon: 'el-icon-document', roles: ['admin'] },
        hidden: true
      },
      {
        path: 'admin/edit/:id',
        name: 'EditLostItem',
        component: () => import('@/views/admin/lost-item/edit'),
        meta: { title: '处理失物', icon: 'el-icon-edit', roles: ['admin'] },
        hidden: true
      },
      {
        path: 'passenger/list',
        name: 'PassengerLostItemList',
        component: () => import('@/views/passenger/lost-item/index'),
        meta: { title: '我的失物', icon: 'el-icon-goods', roles: ['passenger'] }
      },
      {
        path: 'passenger/add',
        name: 'AddLostItem',
        component: () => import('@/views/passenger/lost-item/add'),
        meta: { title: '报失物品', icon: 'el-icon-plus', roles: ['passenger'] },
        hidden: true
      },
      {
        path: 'passenger/detail/:id',
        name: 'PassengerLostItemDetail',
        component: () => import('@/views/passenger/lost-item/detail'),
        meta: { title: '失物详情', icon: 'el-icon-document', roles: ['passenger'] },
        hidden: true
      }
    ]
  },
  {
    path: '/passenger-management',
    component: Layout,
    meta: { title: '旅客管理', icon: 'el-icon-user' },
    children: [
      {
        path: 'list',
        name: 'PassengerList',
        component: () => import('@/views/admin/passenger/index'),
        meta: { title: '旅客列表', icon: 'el-icon-user', roles: ['admin'] }
      },
      {
        path: 'tags',
        name: 'PassengerTags',
        component: () => import('@/views/admin/passenger/tags'),
        meta: { title: '旅客标签', icon: 'el-icon-collection-tag', roles: ['admin'] }
      },
      {
        path: 'detail/:id',
        name: 'PassengerDetail',
        component: () => import('@/views/admin/passenger/detail'),
        meta: { title: '旅客详情', icon: 'el-icon-document', roles: ['admin'] },
        hidden: true
      },
      {
        path: 'activities',
        name: 'PassengerActivities',
        component: () => import('@/views/admin/passenger/activities'),
        meta: { title: '活动记录', icon: 'el-icon-data-analysis', roles: ['admin'] }
      }
    ]
  },
  // 添加系统管理模块路由
  {
    path: '/system-management',
    component: Layout,
    meta: { title: '系统管理', icon: 'el-icon-setting' },
    children: [
      {
        path: 'digital-human-config',
        name: 'DigitalHumanConfig',
        component: () => import('@/views/admin/system/digital-human-config'),
        meta: { title: '数字人配置', icon: 'el-icon-user', roles: ['admin'] }
      }
    ]
  },
  // 导航管理模块
  {
    path: '/passenger-navigation',
    component: Layout,
    redirect: '/passenger-navigation/index',
    meta: { title: '位置导航', icon: 'el-icon-map-location', roles: ['passenger'] },
    hidden: true,
    children: [
      {
        path: 'index',
        name: 'Navigation',
        component: () => import('@/views/passenger/navigation/index'),
        meta: { title: '位置导航', icon: 'el-icon-guide', roles: ['passenger'] }
      },
      {
        path: 'schedule',
        name: 'TimeSchedule',
        component: () => import('@/views/passenger/navigation/schedule'),
        meta: { title: '时间安排', icon: 'el-icon-date', roles: ['passenger'] }
      }
    ]
  },
  // 404页面必须放在最后 !!!
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // 需要服务端支持
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// 详情见: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // 重置路由
}

export default router
