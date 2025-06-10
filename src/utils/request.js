import axios from 'axios'
import { MessageBox, Message } from 'element-ui'
import store from '@/store'
import { getToken } from '@/utils/auth'

// create an axios instance
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API, // url = base url + request url
  // withCredentials: true, // send cookies when cross-domain requests
  timeout: 15000 // request timeout
})

// request interceptor
service.interceptors.request.use(
  config => {
    // do something before request is sent

    if (store.getters.token) {
      // 将token添加到请求头，使用Bearer认证方案
      config.headers['Authorization'] = `Bearer ${getToken()}`
    }
    return config
  },
  error => {
    // do something with request error
    console.log(error) // for debug
    return Promise.reject(error)
  }
)

// response interceptor
service.interceptors.response.use(
  /**
   * If you want to get http information such as headers or status
   * Please return  response => response
  */

  /**
   * Determine the request status by custom code
   * Here is just an example
   * You can also judge the status by HTTP Status Code
   */
  response => {
    const res = response.data
    console.log('API响应数据:', res)
    
    // 检查是否是Django后端返回的成功响应
    // Django后端返回的数据可能没有code字段，但会有HTTP状态码
    if (response.status === 200 || response.status === 201) {
      return res
    }
    
    // 兼容原来的响应格式
    // if the custom code is not 20000, it is judged as an error.
    if (res.code && res.code !== 20000) {
      Message({
        message: res.message || 'Error',
        type: 'error',
        duration: 5 * 1000
      })

      // 50008: Illegal token; 50012: Other clients logged in; 50014: Token expired;
      if (res.code === 50008 || res.code === 50012 || res.code === 50014) {
        // to re-login
        MessageBox.confirm('您已登出，请重新登录', '确认登出', {
          confirmButtonText: '重新登录',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          store.dispatch('user/resetToken').then(() => {
            location.reload()
          })
        })
      }
      return Promise.reject(new Error(res.message || 'Error'))
    } else {
      return res
    }
  },
  error => {
    console.log('请求错误:', error) // for debug
    let errorMsg = '请求错误'
    
    if (error.response) {
      // 服务器返回了错误状态码
      const { data, status } = error.response
      
      if (status === 401) {
        // 未授权，跳转到登录页
        errorMsg = '登录已过期，请重新登录'
        store.dispatch('user/resetToken').then(() => {
          location.reload()
        })
      } else if (status === 403) {
        errorMsg = '没有权限访问'
      } else if (status === 404) {
        errorMsg = '请求的资源不存在'
      } else if (status === 500) {
        errorMsg = '服务器内部错误'
      } else if (data && data.error) {
        // Django REST framework 通常在错误响应中包含error字段
        errorMsg = data.error || data.detail || '请求失败'
      }
    } else if (error.request) {
      // 请求发送了但没有收到响应
      errorMsg = '服务器无响应'
    } else {
      // 请求配置出错
      errorMsg = error.message
    }
    
    Message({
      message: errorMsg,
      type: 'error',
      duration: 5 * 1000
    })
    return Promise.reject(error)
  }
)

export default service
