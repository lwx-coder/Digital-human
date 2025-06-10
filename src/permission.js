import router from './router'
import store from './store'
import { Message } from 'element-ui'
import NProgress from 'nprogress' // progress bar
import 'nprogress/nprogress.css' // progress bar style
import { getToken } from '@/utils/auth' // get token from cookie
import getPageTitle from '@/utils/get-page-title'

NProgress.configure({ showSpinner: false }) // NProgress Configuration

const whiteList = ['/login', '/register', '/forget-password'] // no redirect whitelist

router.beforeEach(async(to, from, next) => {
  // start progress bar
  NProgress.start()

  // set page title
  document.title = getPageTitle(to.meta.title)

  // determine whether the user has logged in
  const hasToken = getToken()

  if (hasToken) {
    if (to.path === '/login') {
      // if is logged in, redirect to the home page
      next({ path: '/' })
      NProgress.done()
    } else {
      // 确定用户是否已获取角色权限
      const hasRoles = store.getters.roles && store.getters.roles.length > 0
      if (hasRoles) {
        // 检查用户是否有访问该路由的权限
        if (hasPermission(store.getters.roles, to)) {
          next()
        } else {
          next({ path: '/401', replace: true })
        }
      } else {
        try {
          // 获取用户信息，包括角色
          const { roles } = await store.dispatch('user/getInfo')
          // 检查用户是否有访问该路由的权限
          if (hasPermission(roles, to)) {
            next()
          } else {
            next({ path: '/401', replace: true })
          }
        } catch (error) {
          // 移除 token 并转到登录页面重新登录
          await store.dispatch('user/resetToken')
          Message.error(error || '验证失败，请重新登录')
          next(`/login?redirect=${to.path}`)
          NProgress.done()
        }
      }
    }
  } else {
    /* 没有token*/
    if (whiteList.indexOf(to.path) !== -1) {
      // 在免登录白名单，直接进入
      next()
    } else {
      // 其他没有访问权限的页面将重定向到登录页面
      next(`/login?redirect=${to.path}`)
      NProgress.done()
    }
  }
})

/**
 * 检查用户是否有访问某个路由的权限
 * @param {Array} roles 用户角色
 * @param {Route} route 路由对象
 * @returns {boolean}
 */
function hasPermission(roles, route) {
  if (route.meta && route.meta.roles) {
    return roles.some(role => route.meta.roles.includes(role))
  } else {
    // 如果路由没有设置权限控制，则默认可以访问
    return true
  }
}

router.afterEach(() => {
  // finish progress bar
  NProgress.done()
})
