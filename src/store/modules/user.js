import { login, logout, getInfo, mobileLogin } from '@/api/user'
import { getToken, setToken, removeToken, getRefreshToken, setRefreshToken, removeRefreshToken } from '@/utils/auth'
import { resetRouter } from '@/router'

const getDefaultState = () => {
  return {
    token: getToken(),
    refreshToken: getRefreshToken(),
    name: '',
    avatar: '',
    roles: []
  }
}

const state = getDefaultState()

const mutations = {
  RESET_STATE: (state) => {
    Object.assign(state, getDefaultState())
  },
  SET_TOKEN: (state, token) => {
    state.token = token
  },
  SET_REFRESH_TOKEN: (state, refreshToken) => {
    state.refreshToken = refreshToken
  },
  SET_NAME: (state, name) => {
    state.name = name
  },
  SET_AVATAR: (state, avatar) => {
    state.avatar = avatar
  },
  SET_ROLES: (state, roles) => {
    state.roles = roles
  }
}

const actions = {
  // 账号密码登录
  login({ commit }, userInfo) {
    const { username, password } = userInfo
    return new Promise((resolve, reject) => {
      login({ username: username.trim(), password: password }).then(response => {
        // 处理响应数据
        console.log('登录响应:', response)
        
        // 从响应中获取token
        const token = response.access || (response.data && response.data.access)
        
        if (!token) {
          console.error('登录响应中未找到access token')
          reject(new Error('登录失败：未获取到token'))
          return
        }
        
        // 保存refresh token
        const refreshToken = response.refresh || (response.data && response.data.refresh)
        if (refreshToken) {
          commit('SET_REFRESH_TOKEN', refreshToken)
          setRefreshToken(refreshToken)
        }
        
        commit('SET_TOKEN', token)
        setToken(token)
        resolve()
      }).catch(error => {
        console.error('登录错误:', error)
        reject(error)
      })
    })
  },

  // 手机号登录
  mobileLogin({ commit }, mobileInfo) {
    const { phone, code } = mobileInfo
    return new Promise((resolve, reject) => {
      mobileLogin({ phone, code }).then(response => {
        // 处理响应数据
        console.log('手机登录响应:', response)
        
        // 从响应中获取token
        const token = response.access || (response.data && response.data.access)
        
        if (!token) {
          console.error('手机登录响应中未找到access token')
          reject(new Error('登录失败：未获取到token'))
          return
        }
        
        // 保存refresh token
        const refreshToken = response.refresh || (response.data && response.data.refresh)
        if (refreshToken) {
          commit('SET_REFRESH_TOKEN', refreshToken)
          setRefreshToken(refreshToken)
        }
        
        commit('SET_TOKEN', token)
        setToken(token)
        resolve()
      }).catch(error => {
        console.error('手机登录错误:', error)
        reject(error)
      })
    })
  },

  // 获取用户信息
  getInfo({ commit, state }) {
    return new Promise((resolve, reject) => {
      getInfo(state.token).then(response => {
        console.log('用户信息响应:', response)
        // 适配不同的响应格式
        let userData = response
        if (response.data) {
          userData = response.data
        }

        if (!userData) {
          reject('验证失败，请重新登录')
          return
        }

        // 解构用户数据
        let { name, avatar, roles } = userData
        console.log('解析的用户数据:', { name, avatar, roles })
        
        // 确保用户名存在
        if (!name && userData.username) {
          name = userData.username
        }
        
        // 确保头像存在
        // 直接使用后端返回的avatar URL，如果不存在则保持空
        if (!avatar && userData.user && userData.user.avatar) {
          avatar = userData.user.avatar
          console.log('从user对象获取头像:', avatar)
        }
        
        console.log('最终使用的头像URL:', avatar)
        
        // 处理角色信息
        if (!roles) {
          // 从用户信息中尝试获取角色
          if (userData.roles) {
            roles = userData.roles
          } else if (userData.user && userData.user.roles) {
            roles = userData.user.roles
          } else {
            roles = ['default'] // 默认角色
          }
        }
        // 确保roles是数组
        if (!Array.isArray(roles)) {
          if (typeof roles === 'string') {
            roles = [roles]
          } else {
            roles = ['default']
          }
        }

        if (roles.length <= 0) {
          roles = ['default']
        }

        commit('SET_ROLES', roles)
        commit('SET_NAME', name)
        commit('SET_AVATAR', avatar)
        console.log('已更新Vuex状态:', { name, avatar, roles })
        resolve({ name, avatar, roles })
      }).catch(error => {
        console.error('获取用户信息错误:', error)
        reject(error)
      })
    })
  },

  // 退出登录
  logout({ commit, state }) {
    return new Promise((resolve, reject) => {
      try {
        // 获取refresh token
        const refreshToken = getRefreshToken()
        
        // 尝试调用后端登出接口
        logout().then(() => {
          console.log('后端登出成功')
          // 清理本地存储
          removeToken()
          removeRefreshToken()
          resetRouter()
          commit('RESET_STATE')
          resolve()
        }).catch(error => {
          console.warn('后端登出接口调用失败:', error)
          // 即使后端接口失败，也要清理前端状态
          removeToken()
          removeRefreshToken()
          resetRouter()
          commit('RESET_STATE')
          resolve()
        })
      } catch (error) {
        console.error('登出过程出现异常:', error)
        // 确保无论如何都清理前端状态
        removeToken()
        removeRefreshToken()
        resetRouter()
        commit('RESET_STATE')
        resolve()
      }
    })
  },

  // 重置token
  resetToken({ commit }) {
    return new Promise(resolve => {
      removeToken()
      removeRefreshToken()
      commit('RESET_STATE')
      resolve()
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}

