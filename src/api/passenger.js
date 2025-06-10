import request from '@/utils/request'

// 获取乘客列表
export function getPassengerList(query) {
  return request({
    url: '/api/passenger-management/passengers/',
    method: 'get',
    params: query
  })
}

// 获取乘客详情
export function getPassengerDetail(id) {
  return request({
    url: `/api/passenger-management/passengers/${id}/`,
    method: 'get'
  })
}

// 获取乘客备注列表
export function getPassengerNotes(id, query) {
  return request({
    url: `/api/passenger-management/passengers/${id}/notes/`,
    method: 'get',
    params: query
  })
}

// 添加乘客备注
export function addPassengerNote(id, data) {
  return request({
    url: `/api/passenger-management/passengers/${id}/add_note/`,
    method: 'post',
    data
  })
}

// 获取乘客活动记录
export function getPassengerActivities(id, query) {
  console.log(id, query,1111)
  return request({
    url: `/api/passenger-management/passengers/${id}/activities/`,
    method: 'get',
    params: query
  })
}

// 获取乘客失物列表
export function getPassengerLostItems(id, query) {
  return request({
    url: `/api/passenger-management/passengers/${id}/lost_items/`,
    method: 'get',
    params: query
  })
}

// 获取或更新乘客资料
export function getPassengerProfile(id) {
  return request({
    url: `/api/passenger-management/passengers/${id}/profile/`,
    method: 'get'
  })
}

// 更新乘客资料
export function updatePassengerProfile(id, data) {
  return request({
    url: `/api/passenger-management/passengers/${id}/profile/`,
    method: 'put',
    data
  })
}

// 获取乘客标签列表
export function getPassengerTags(query) {
  return request({
    url: '/api/passenger-management/tags/',
    method: 'get',
    params: query
  })
}

// 创建乘客标签
export function createPassengerTag(data) {
  return request({
    url: '/api/passenger-management/tags/',
    method: 'post',
    data
  })
}

// 更新乘客标签
export function updatePassengerTag(id, data) {
  return request({
    url: `/api/passenger-management/tags/${id}/`,
    method: 'put',
    data
  })
}

// 删除乘客标签
export function deletePassengerTag(id) {
  return request({
    url: `/api/passenger-management/tags/${id}/`,
    method: 'delete'
  })
}

// 获取标签下的乘客列表
export function getTagPassengers(id, query) {
  return request({
    url: `/api/passenger-management/tags/${id}/passengers/`,
    method: 'get',
    params: query
  })
}

// 获取活动统计数据
export function getActivityStats(query) {
  return request({
    url: '/api/passenger-management/activities/stats/',
    method: 'get',
    params: query
  })
}

