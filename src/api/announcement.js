import request from '@/utils/request'
import { getToken } from '@/utils/auth'

/**
 * 获取公告类型列表
 * @param {Object} params - 查询参数
 */
export function getAnnouncementTypeList(params) {
  return request({
    url: '/api/informations/announcement-types/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` },
    params
  })
}

/**
 * 获取公告列表
 * @param {Object} params - 查询参数
 */
export function getAnnouncementList(params) {
  return request({
    url: '/api/informations/announcements/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` },
    params
  })
}

/**
 * 获取当前有效的公告
 * @param {Object} params - 查询参数
 */
export function getActiveAnnouncements(params) {
  return request({
    url: '/api/informations/announcements/active/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` },
    params
  })
}

/**
 * 获取紧急通知
 * @param {Object} params - 查询参数
 */
export function getEmergencyAnnouncements(params) {
  return request({
    url: '/api/informations/announcements/emergency/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` },
    params
  })
}

/**
 * 获取公告详情
 * @param {String} id - 公告ID
 */
export function getAnnouncementDetail(id) {
  return request({
    url: `/api/informations/announcements/${id}/`,
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` }
  })
}

/**
 * 添加公告信息（仅管理员）
 * @param {Object} data - 公告信息
 */
export function addAnnouncement(data) {
  return request({
    url: '/api/informations/announcements/',
    method: 'post',
    headers: { Authorization: `Bearer ${getToken()}` },
    data
  })
}

/**
 * 更新公告信息（仅管理员）
 * @param {String} id - 公告ID
 * @param {Object} data - 公告信息
 */
export function updateAnnouncement(id, data) {
  return request({
    url: `/api/informations/announcements/${id}/`,
    method: 'put',
    headers: { Authorization: `Bearer ${getToken()}` },
    data
  })
}

/**
 * 删除公告信息（仅管理员）
 * @param {String} id - 公告ID
 */
export function deleteAnnouncement(id) {
  return request({
    url: `/api/informations/announcements/${id}/`,
    method: 'delete',
    headers: { Authorization: `Bearer ${getToken()}` }
  })
}

/**
 * 获取公告语音播报内容
 * @param {String} id - 公告ID
 */
export function getAnnouncementVoiceContent(id) {
  return request({
    url: `/api/informations/announcements/${id}/voice_content/`,
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` }
  })
}

/**
 * 创建公告播报
 * @param {Object} data - 包含announcement_id和content
 */
export function createAnnouncementBroadcast(data) {
  return request({
    url: '/api/informations/broadcasts/broadcast/',
    method: 'post',
    headers: { Authorization: `Bearer ${getToken()}` },
    data
  })
}

/**
 * 获取公告播报历史
 * @param {Object} params - 查询参数，如announcement等
 */
export function getBroadcastHistory(params) {
  return request({
    url: '/api/informations/broadcasts/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` },
    params
  })
} 