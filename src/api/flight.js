import request from '@/utils/request'
import { getToken } from '@/utils/auth'

/**
 * 获取航班列表
 * @param {Object} params - 查询参数
 */
export function getFlightList(params) {
  return request({
    url: '/api/flight-management/flights/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` },
    params
  })
}

/**
 * 获取航班详情
 * @param {String} id - 航班ID
 */
export function getFlightDetail(id) {
  return request({
    url: `/api/flight-management/flights/${id}/`,
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` }
  })
}

/**
 * 添加航班信息（仅管理员）
 * @param {Object} data - 航班信息
 */
export function addFlight(data) {
  return request({
    url: '/api/flight-management/flights/',
    method: 'post',
    headers: { Authorization: `Bearer ${getToken()}` },
    data
  })
}

/**
 * 更新航班信息（仅管理员）
 * @param {String} id - 航班ID
 * @param {Object} data - 航班信息
 */
export function updateFlight(id, data) {
  return request({
    url: `/api/flight-management/flights/${id}/`,
    method: 'put',
    headers: { Authorization: `Bearer ${getToken()}` },
    data
  })
}

/**
 * 删除航班信息（仅管理员）
 * @param {String} id - 航班ID
 */
export function deleteFlight(id) {
  return request({
    url: `/api/flight-management/flights/${id}/`,
    method: 'delete',
    headers: { Authorization: `Bearer ${getToken()}` }
  })
}

/**
 * 搜索航班信息
 * @param {String} query - 搜索关键词
 */
export function searchFlights(query) {
  return request({
    url: '/api/flight-management/flights/search/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` },
    params: { q: query }
  })
}

/**
 * 获取航班语音播报内容
 * @param {String} id - 航班ID
 */
export function getFlightVoiceStatus(id) {
  return request({
    url: `/api/flight-management/flights/${id}/voice_status/`,
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` }
  })
}

/**
 * 创建航班播报
 * @param {Object} data - 包含flight_number和content
 */
export function createFlightAnnouncement(data) {
  return request({
    url: '/api/flight-management/announcements/announce/',
    method: 'post',
    headers: { Authorization: `Bearer ${getToken()}` },
    data
  })
}

/**
 * 获取航班播报历史
 * @param {Object} params - 查询参数，如flight等
 */
export function getAnnouncementHistory(params) {
  return request({
    url: '/api/flight-management/announcements/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` },
    params
  })
}

/**
 * 旅客选择航班
 * @param {String} id - 航班ID
 */
export function selectFlight(id) {
  return request({
    url: `/api/flight-management/passenger/${id}/select/`,
    method: 'post',
    headers: { Authorization: `Bearer ${getToken()}` }
  })
}

/**
 * 旅客取消选择航班
 * @param {String} id - 航班ID
 */
export function unselectFlight(id) {
  return request({
    url: `/api/flight-management/passenger/${id}/unselect/`,
    method: 'post',
    headers: { Authorization: `Bearer ${getToken()}` }
  })
}

/**
 * 获取旅客已选择的航班
 * @param {Object} params - 分页参数
 */
export function getMyFlights(params) {
  return request({
    url: '/api/flight-management/passenger/my_flights/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` },
    params
  })
} 