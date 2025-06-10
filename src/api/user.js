import request from '@/utils/request'
import { getToken, getRefreshToken } from '@/utils/auth'

/**
 * 账号密码登录
 * @param {Object} data - 包含username和password
 */
export function login(data) {
  return request({
    url: '/api/users/login/',
    method: 'post',
    data
  })
}

/**
 * 获取用户信息
 * @param {String} token - JWT令牌
 */
export function getInfo(token) {
  return request({
    url: '/api/users/info/',
    method: 'get',
    headers: { Authorization: `Bearer ${token}` }
  })
}

/**
 * 退出登录
 */
export function logout() {
  return request({
    url: '/api/users/logout/',
    method: 'post',
    headers: { Authorization: `Bearer ${getToken()}` },
    data: {
      refresh: getRefreshToken() // 发送refresh token到后端使其失效
    }
  })
}

/**
 * 用户注册
 * @param {Object} data - 包含username, email, phone, password等信息
 */
export function register(data) {
  return request({
    url: '/api/users/register/',
    method: 'post',
    data
  })
}

/**
 * 手机号验证码登录
 * @param {Object} data - 包含phone和code
 */
export function mobileLogin(data) {
  return request({
    url: '/api/users/phone-login/',
    method: 'post',
    data
  })
}

/**
 * 发送手机验证码
 * @param {String} phone - 手机号
 */
export function sendPhoneCode(phone) {
  return request({
    url: '/api/users/send-phone-code/',
    method: 'post',
    data: { phone }
  })
}

/**
 * 请求重置密码（发送验证码）
 * @param {Object} data - 包含email的对象
 */
export function resetPasswordRequest(data) {
  return request({
    url: '/api/users/reset-password-request/',
    method: 'post',
    data
  })
}

/**
 * 确认重置密码
 * @param {Object} data - 包含email, code, new_password, new_password_confirm
 */
export function resetPasswordConfirm(data) {
  return request({
    url: '/api/users/reset-password-confirm/',
    method: 'post',
    data
  })
}

/**
 * 更新用户信息
 * @param {Object} data - 用户信息数据
 */
export function updateUserInfo(data) {
  return request({
    url: '/api/users/update_me/',
    method: 'put',
    headers: { Authorization: `Bearer ${getToken()}` },
    data
  })
}

/**
 * 获取当前用户详细信息
 */
export function getUserDetail() {
  return request({
    url: '/api/users/me/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` }
  })
}

/**
 * 修改密码
 * @param {Object} data - 包含old_password, new_password
 */
export function changePassword(data) {
  return request({
    url: '/api/users/change-password/',
    method: 'post',
    headers: { Authorization: `Bearer ${getToken()}` },
    data
  })
}

/**
 * 上传用户头像
 * @param {File} file - 头像文件
 */
export function uploadAvatar(file) {
  const formData = new FormData()
  formData.append('avatar', file)
  
  return request({
    url: '/api/users/upload_avatar/',
    method: 'post',
    headers: { 
      Authorization: `Bearer ${getToken()}`,
      'Content-Type': 'multipart/form-data'
    },
    data: formData
  })
}
