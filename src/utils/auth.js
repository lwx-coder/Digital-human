import Cookies from 'js-cookie'

const TokenKey = 'vue_admin_template_token'
const RefreshTokenKey = 'vue_admin_template_refresh_token'

/**
 * 获取Access Token
 */
export function getToken() {
  return Cookies.get(TokenKey)
}

/**
 * 设置Access Token
 * @param {String} token - JWT access token
 */
export function setToken(token) {
  return Cookies.set(TokenKey, token)
}

/**
 * 移除Access Token
 */
export function removeToken() {
  return Cookies.remove(TokenKey)
}

/**
 * 获取Refresh Token
 */
export function getRefreshToken() {
  return Cookies.get(RefreshTokenKey)
}

/**
 * 设置Refresh Token
 * @param {String} token - JWT refresh token
 */
export function setRefreshToken(token) {
  return Cookies.set(RefreshTokenKey, token)
}

/**
 * 移除Refresh Token
 */
export function removeRefreshToken() {
  return Cookies.remove(RefreshTokenKey)
}
