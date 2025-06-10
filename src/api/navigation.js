import request from '@/utils/request'
import { getToken } from '@/utils/auth'

/**
 * 获取所有位置列表
 */
export function getLocationList(params) {
  console.log('请求参数:', params)
  return request({
    url: '/api/navigation-management/locations/',
    method: 'get',
    params
  })
}

/**
 * 按类型获取位置列表
 * @param {String} type - 位置类型
 * @param {Number} floor - 楼层
 */
export function getLocationsByType(type, floor) {
  const params = {}
  if (type) params.type = type
  if (floor) params.floor = floor

  return request({
    url: '/api/navigation-management/locations/by_type/',
    method: 'get',
    params
  })
}

/**
 * 获取位置详情
 * @param {Number} id - 位置ID
 */
export function getLocationDetail(id) {
  return request({
    url: `/api/navigation-management/locations/${id}/`,
    method: 'get'
  })
}

/**
 * 获取附近设施
 * @param {Number} x - 当前X坐标
 * @param {Number} y - 当前Y坐标
 * @param {Number} floor - 当前楼层
 * @param {Number} radius - 搜索半径
 * @param {Array} types - 设施类型数组
 */
export function getNearbyLocations(x, y, floor, radius = 100, types = []) {
  const params = { x, y, floor, radius }
  if (types && types.length > 0) {
    // 将types转换为多个types参数，符合Django REST Framework规范
    types.forEach(type => {
      params[`types[]`] = type
    })
  }

  return request({
    url: '/api/navigation-management/locations/nearby/',
    method: 'get',
    params
  })
}

/**
 * 获取导航记录列表
 */
export function getNavigationList(params) {
  return request({
    url: '/api/navigation-management/navigations/',
    method: 'get',
    params
  })
}

/**
 * 获取导航详情
 * @param {Number} id - 导航ID
 */
export function getNavigationDetail(id) {
  return request({
    url: `/api/navigation-management/navigations/${id}/`,
    method: 'get'
  })
}

/**
 * 创建导航
 * @param {Object} data - 包含起点和终点ID的对象
 */
export function createNavigation(data) {
  return request({
    url: '/api/navigation-management/navigations/navigate/',
    method: 'post',
    data
  })
}

/**
 * 完成导航
 * @param {Number} id - 导航ID
 */
export function completeNavigation(id) {
  return request({
    url: `/api/navigation-management/navigations/${id}/complete/`,
    method: 'post'
  })
}

/**
 * 获取语音导航指令
 * @param {Object} data - 查询参数 
 */
export function getVoiceNavigation(data) {
  return request({
    url: '/api/navigation-management/navigations/voice_query/',
    method: 'post',
    data
  })
}

/**
 * 获取时间安排列表
 */
export function getScheduleList(params) {
  return request({
    url: '/api/navigation-management/schedules/',
    method: 'get',
    params
  })
}

/**
 * 获取今日时间安排
 */
export function getTodaySchedules() {
  console.log('正在请求今日安排')
  return request({
    url: '/api/navigation-management/schedules/today/',
    method: 'get'
  })
}

/**
 * 获取即将到来的时间安排
 */
export function getUpcomingSchedules() {
  return request({
    url: '/api/navigation-management/schedules/upcoming/',
    method: 'get'
  })
}

/**
 * 创建时间安排
 * @param {Object} data - 时间安排数据
 */
export function createSchedule(data) {
  return request({
    url: '/api/navigation-management/schedules/',
    method: 'post',
    data
  })
}

/**
 * 更新时间安排
 * @param {Number} id - 时间安排ID
 * @param {Object} data - 时间安排数据
 */
export function updateSchedule(id, data) {
  return request({
    url: `/api/navigation-management/schedules/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 完成时间安排
 * @param {Number} id - 时间安排ID
 */
export function completeSchedule(id) {
  return request({
    url: `/api/navigation-management/schedules/${id}/complete/`,
    method: 'post'
  })
}

/**
 * 删除时间安排
 * @param {Number} id - 时间安排ID
 */
export function deleteSchedule(id) {
  return request({
    url: `/api/navigation-management/schedules/${id}/`,
    method: 'delete'
  })
} 