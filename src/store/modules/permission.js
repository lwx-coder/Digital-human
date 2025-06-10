import { asyncRoutes, constantRoutes } from '@/router'

/**
 * 使用meta.roles判断当前用户是否有权限访问路由
 * @param roles 用户角色
 * @param route 路由对象
 */
function hasPermission(roles, route) {
  if (route.meta && route.meta.roles) {
    return roles.some(role => route.meta.roles.includes(role))
  } else {
    return true
  }
}

/**
 * 根据角色过滤异步路由表
 * @param routes 异步路由表
 * @param roles 用户角色
 */
export function filterAsyncRoutes(routes, roles) {
  const res = []

  routes.forEach(route => {
    const tmp = { ...route }
    if (tmp.children) {
      // 先递归过滤子路由
      tmp.children = filterAsyncRoutes(tmp.children, roles)
      // 如果子路由被全部过滤掉了，且父路由没有组件，则不添加父路由
      if (tmp.children.length === 0 && !tmp.component) {
        return
      }
    }
    // 检查当前路由权限
    if (hasPermission(roles, tmp)) {
      res.push(tmp)
    }
  })

  return res
}

const state = {
  routes: [],
  addRoutes: []
}

const mutations = {
  SET_ROUTES: (state, routes) => {
    state.addRoutes = routes
    state.routes = constantRoutes.concat(routes)
  }
}

const actions = {
  generateRoutes({ commit }, roles) {
    return new Promise(resolve => {
      let accessedRoutes
      if (roles.includes('admin')) {
        // 管理员可以访问所有路由
        accessedRoutes = asyncRoutes || []
      } else {
        // 根据角色过滤路由
        accessedRoutes = filterAsyncRoutes(asyncRoutes, roles)
      }
      commit('SET_ROUTES', accessedRoutes)
      resolve(accessedRoutes)
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
