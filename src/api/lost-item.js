import request from '@/utils/request'
import { getToken } from '@/utils/auth'

/**
 * 获取物品类别列表
 * @param {Object} params - 查询参数
 */
export function getItemCategoryList(params) {
  return request({
    url: '/api/items-management/categories/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` },
    params
  })
}

/**
 * 获取失物列表
 * @param {Object} params - 查询参数
 */
export function getLostItemList(params) {
  return request({
    url: '/api/items-management/lost-items/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` },
    params
  })
}

/**
 * 获取当前用户报失的物品
 * @param {Object} params - 查询参数
 */
export function getMyLostItems(params) {
  return request({
    url: '/api/items-management/lost-items/my_items/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` },
    params
  })
}

/**
 * 获取待处理的失物信息（管理员使用）
 * @param {Object} params - 查询参数
 */
export function getPendingLostItems(params) {
  return request({
    url: '/api/items-management/lost-items/pending/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` },
    params
  })
}

/**
 * 获取失物详情
 * @param {String} id - 失物ID
 */
export function getLostItemDetail(id) {
  return request({
    url: `/api/items-management/lost-items/${id}/`,
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` }
  })
}

/**
 * 添加失物信息
 * @param {Object} data - 失物信息
 */
export function addLostItem(data) {
  return request({
    url: '/api/items-management/lost-items/',
    method: 'post',
    headers: { Authorization: `Bearer ${getToken()}` },
    data
  })
}

/**
 * 更新失物信息
 * @param {String} id - 失物ID
 * @param {Object} data - 失物信息
 */
export function updateLostItem(id, data) {
  return request({
    url: `/api/items-management/lost-items/${id}/`,
    method: 'put',
    headers: { Authorization: `Bearer ${getToken()}` },
    data
  })
}

/**
 * 删除失物信息
 * @param {String} id - 失物ID
 */
export function deleteLostItem(id) {
  return request({
    url: `/api/items-management/lost-items/${id}/`,
    method: 'delete',
    headers: { Authorization: `Bearer ${getToken()}` }
  })
}

/**
 * 获取失物广播内容
 * @param {String} id - 失物ID
 */
export function getLostItemBroadcastContent(id) {
  return request({
    url: `/api/items-management/lost-items/${id}/broadcast_content/`,
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` }
  })
}

/**
 * 创建失物广播
 * @param {Object} data - 包含lost_item_id和content
 */
export function createLostItemBroadcast(data) {
  return request({
    url: '/api/items-management/broadcasts/broadcast/',
    method: 'post',
    headers: { Authorization: `Bearer ${getToken()}` },
    data
  })
}

/**
 * 获取广播历史
 * @param {Object} params - 查询参数，如lost_item等
 */
export function getBroadcastHistory(params) {
  return request({
    url: '/api/items-management/broadcasts/',
    method: 'get',
    headers: { Authorization: `Bearer ${getToken()}` },
    params
  })
} 