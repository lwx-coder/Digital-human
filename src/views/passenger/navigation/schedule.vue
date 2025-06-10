<template>
  <div class="schedule-container">
    <el-card class="schedule-header-card">
      <div class="header-top">
        <div class="page-title">
          <h2>我的时间安排</h2>
          <div class="sub-title">管理您的飞行旅程和活动安排</div>
        </div>
        <div class="action-buttons">
          <el-button type="primary" icon="el-icon-plus" @click="showAddScheduleDialog">
            添加安排
          </el-button>
          <el-button plain icon="el-icon-refresh" @click="refreshData">
            刷新
          </el-button>
        </div>
      </div>
      
      <div class="filter-bar">
        <el-date-picker
          v-model="dateFilter"
          type="date"
          placeholder="选择日期"
          format="yyyy-MM-dd"
          value-format="yyyy-MM-dd"
          @change="handleDateChange"
          style="width: 150px;">
        </el-date-picker>
        
        <el-input
          v-model="flightCodeFilter"
          placeholder="航班号"
          clearable
          @clear="handleFilterChange"
          @keyup.enter.native="handleFilterChange"
          style="width: 150px; margin-left: 15px;">
          <el-button slot="append" icon="el-icon-search" @click="handleFilterChange"></el-button>
        </el-input>
        
        <el-checkbox 
          v-model="includeCompleted" 
          style="margin-left: 15px;"
          @change="handleFilterChange">
          显示已完成
        </el-checkbox>
      </div>
    </el-card>
    
    <el-row :gutter="20" class="schedule-content">
      <el-col :span="24">
        <el-card shadow="hover" class="schedule-timeline-card">
          <div class="timeline-header">
            <h3>时间安排</h3>
          </div>
          
          <el-timeline v-if="schedules.length > 0">
            <el-timeline-item
              v-for="schedule in schedules"
              :key="schedule.id"
              :timestamp="formatTime(schedule.start_time)"
              :type="getScheduleStatusType(schedule)"
              :icon="getScheduleIcon(schedule)">
              <el-card shadow="hover" class="schedule-item">
                <div class="schedule-item-header">
                  <div class="schedule-title">
                    <span class="event-name">{{ schedule.event_name }}</span>
                    <el-tag 
                      v-if="schedule.event_type" 
                      size="small" 
                      :type="getEventTypeTag(schedule.event_type)">
                      {{ schedule.event_type_display }}
                    </el-tag>
                    <el-tag 
                      v-if="schedule.flight_code" 
                      size="small" 
                      type="info">
                      {{ schedule.flight_code }}
                    </el-tag>
                  </div>
                  <div class="schedule-actions">
                    <el-tooltip content="编辑安排" placement="top">
                      <el-button 
                        type="text" 
                        icon="el-icon-edit" 
                        @click="editSchedule(schedule)">
                      </el-button>
                    </el-tooltip>
                    <el-tooltip 
                      :content="schedule.is_completed ? '取消完成' : '标记为完成'" 
                      placement="top">
                      <el-button 
                        type="text" 
                        :icon="schedule.is_completed ? 'el-icon-remove-outline' : 'el-icon-check'" 
                        @click="toggleComplete(schedule)">
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="删除安排" placement="top">
                      <el-button 
                        type="text" 
                        icon="el-icon-delete" 
                        @click="confirmDelete(schedule)">
                      </el-button>
                    </el-tooltip>
                  </div>
                </div>
                
                <div class="schedule-time">
                  <i class="el-icon-time"></i>
                  {{ formatTime(schedule.start_time) }}
                  <template v-if="schedule.end_time">
                    - {{ formatTime(schedule.end_time) }}
                  </template>
                </div>
                
                <div v-if="schedule.location_detail" class="schedule-location">
                  <i class="el-icon-location"></i>
                  {{ schedule.location_detail.name }}
                  <template v-if="schedule.location_detail.floor">
                    ({{ schedule.location_detail.floor }}楼)
                  </template>
                </div>
                
                <div v-if="schedule.notes" class="schedule-notes">
                  <i class="el-icon-document"></i>
                  {{ schedule.notes }}
                </div>
                
                <div class="schedule-navigate" v-if="schedule.location_detail && schedule.location && !schedule.is_completed">
                  <el-button 
                    type="success" 
                    size="small" 
                    icon="el-icon-position" 
                    @click="navigateTo(schedule)">
                    导航到此处
                  </el-button>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          
          <div v-else class="empty-schedule">
            <i class="el-icon-date"></i>
            <p>暂无时间安排</p>
            <el-button type="primary" plain @click="showAddScheduleDialog">添加安排</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 添加/编辑安排对话框 -->
    <el-dialog 
      :title="dialogType === 'add' ? '添加时间安排' : '编辑时间安排'" 
      :visible.sync="scheduleDialogVisible"
      width="500px">
      <el-form ref="scheduleForm" :model="scheduleForm" :rules="scheduleRules" label-width="100px">
        <el-form-item label="事件名称" prop="event_name">
          <el-input v-model="scheduleForm.event_name" placeholder="请输入事件名称"></el-input>
        </el-form-item>
        
        <el-form-item label="事件类型" prop="event_type">
          <el-select v-model="scheduleForm.event_type" placeholder="请选择事件类型" style="width: 100%">
            <el-option
              v-for="item in eventTypes"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="航班号" prop="flight_code">
          <el-input v-model="scheduleForm.flight_code" placeholder="如有相关航班，请输入航班号"></el-input>
        </el-form-item>
        
        <el-form-item label="地点" prop="location">
          <el-select v-model="scheduleForm.location" filterable placeholder="请选择地点" style="width: 100%">
            <el-option
              v-for="location in locations"
              :key="location.id"
              :label="`${location.name} (${location.floor}楼)`"
              :value="location.id">
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker
            v-model="scheduleForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 100%">
          </el-date-picker>
        </el-form-item>
        
        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker
            v-model="scheduleForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
            style="width: 100%">
          </el-date-picker>
        </el-form-item>
        
        <el-form-item label="备注" prop="notes">
          <el-input
            type="textarea"
            v-model="scheduleForm.notes"
            placeholder="请输入备注信息"
            :rows="3">
          </el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="scheduleDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitScheduleForm">确 定</el-button>
      </span>
    </el-dialog>
    
    <!-- 确认删除对话框 -->
    <el-dialog
      title="确认删除"
      :visible.sync="deleteDialogVisible"
      width="400px">
      <p>确定要删除这个时间安排吗？此操作不可逆。</p>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deleteDialogVisible = false">取 消</el-button>
        <el-button type="danger" @click="confirmDeleteSchedule">确定删除</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { 
  getScheduleList, createSchedule, updateSchedule,
  completeSchedule, deleteSchedule 
} from '@/api/navigation'
import { getLocationList } from '@/api/navigation'
import { parseTime } from '@/utils'

export default {
  name: 'TimeScheduleManagement',
  data() {
    return {
      schedules: [],
      locations: [],
      loading: false,
      
      // 筛选条件
      dateFilter: '',
      flightCodeFilter: '',
      includeCompleted: false,
      
      // 对话框控制
      scheduleDialogVisible: false,
      deleteDialogVisible: false,
      dialogType: 'add', // 'add' 或 'edit'
      
      // 表单数据
      scheduleForm: {
        event_name: '',
        event_type: '',
        flight_code: '',
        location: null,
        start_time: '',
        end_time: '',
        notes: ''
      },
      
      // 表单验证规则
      scheduleRules: {
        event_name: [
          { required: true, message: '请输入事件名称', trigger: 'blur' },
          { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
        ],
        event_type: [
          { required: true, message: '请选择事件类型', trigger: 'change' }
        ],
        start_time: [
          { required: true, message: '请选择开始时间', trigger: 'change' }
        ],
        location: [
          { required: true, message: '请选择地点', trigger: 'change' }
        ]
      },
      
      // 事件类型选项
      eventTypes: [
        { value: 'check_in', label: '办理登机' },
        { value: 'security', label: '安检' },
        { value: 'boarding', label: '登机' },
        { value: 'shopping', label: '购物' },
        { value: 'dining', label: '用餐' },
        { value: 'resting', label: '休息' },
        { value: 'other', label: '其他' }
      ],
      
      // 当前操作的行项目
      currentSchedule: null
    }
  },
  created() {
    this.fetchData()
    this.fetchLocations()
  },
  methods: {
    // 格式化时间
    formatTime(time) {
      return parseTime(time, '{y}-{m}-{d} {h}:{i}')
    },
    
    // 获取时间安排列表数据
    fetchData() {
      this.loading = true
      
      // 构建查询参数
      const params = {}
      if (this.dateFilter) {
        params.date = this.dateFilter
      }
      if (this.flightCodeFilter) {
        params.flight_code = this.flightCodeFilter
      }
      params.include_completed = this.includeCompleted
      
      getScheduleList(params).then(response => {
        this.schedules = Array.isArray(response) ? response : []
        this.loading = false
      }).catch(error => {
        console.error('获取时间安排列表失败:', error)
        this.$message.error('获取时间安排列表失败')
        this.loading = false
      })
    },
    
    // 获取位置列表
    fetchLocations() {
      getLocationList().then(response => {
        console.log('获取位置列表响应:', response)
        // 确保locations是数组
        this.locations = Array.isArray(response) ? response : (response.results || [])
      }).catch(error => {
        console.error('获取位置列表失败:', error)
        this.$message.error('获取位置列表失败')
      })
    },
    
    // 刷新数据
    refreshData() {
      this.fetchData()
      this.$message.success('数据已刷新')
    },
    
    // 获取安排状态类型（用于Timeline组件）
    getScheduleStatusType(schedule) {
      if (schedule.is_completed) {
        return 'success'
      }
      
      // 判断是否已过期
      const now = new Date()
      const startTime = new Date(schedule.start_time)
      
      if (startTime < now && !schedule.is_completed) {
        return 'danger'
      }
      
      return 'primary'
    },
    
    // 获取安排图标
    getScheduleIcon(schedule) {
      switch (schedule.event_type) {
        case 'check_in':
          return 'el-icon-s-claim'
        case 'security':
          return 'el-icon-s-check'
        case 'boarding':
          return 'el-icon-s-cooperation'
        case 'shopping':
          return 'el-icon-shopping-cart-2'
        case 'dining':
          return 'el-icon-dish'
        case 'resting':
          return 'el-icon-s-home'
        default:
          return 'el-icon-date'
      }
    },
    
    // 获取事件类型标签样式
    getEventTypeTag(type) {
      const tagMap = {
        check_in: 'info',
        security: 'warning',
        boarding: 'success',
        shopping: '',
        dining: 'danger',
        resting: '',
        other: 'info'
      }
      return tagMap[type] || 'info'
    },
    
    // 处理日期变化
    handleDateChange() {
      this.fetchData()
    },
    
    // 处理筛选条件变化
    handleFilterChange() {
      this.fetchData()
    },
    
    // 显示添加安排对话框
    showAddScheduleDialog() {
      this.dialogType = 'add'
      this.resetForm()
      this.scheduleDialogVisible = true
    },
    
    // 编辑安排
    editSchedule(schedule) {
      this.dialogType = 'edit'
      this.currentSchedule = schedule
      
      // 填充表单数据
      this.scheduleForm = {
        event_name: schedule.event_name,
        event_type: schedule.event_type,
        flight_code: schedule.flight_code || '',
        location: schedule.location,
        start_time: schedule.start_time,
        end_time: schedule.end_time || '',
        notes: schedule.notes || ''
      }
      
      this.scheduleDialogVisible = true
    },
    
    // 切换完成状态
    toggleComplete(schedule) {
      completeSchedule(schedule.id).then(() => {
        this.$message.success(schedule.is_completed ? '已取消完成状态' : '已标记为完成')
        this.fetchData()
      }).catch(error => {
        console.error('更新完成状态失败:', error)
        this.$message.error('更新完成状态失败')
      })
    },
    
    // 确认删除对话框
    confirmDelete(schedule) {
      this.currentSchedule = schedule
      this.deleteDialogVisible = true
    },
    
    // 确认删除安排
    confirmDeleteSchedule() {
      if (!this.currentSchedule) return
      
      deleteSchedule(this.currentSchedule.id).then(() => {
        this.$message.success('时间安排已删除')
        this.deleteDialogVisible = false
        this.fetchData()
      }).catch(error => {
        console.error('删除时间安排失败:', error)
        this.$message.error('删除时间安排失败')
      })
    },
    
    // 重置表单
    resetForm() {
      this.scheduleForm = {
        event_name: '',
        event_type: '',
        flight_code: '',
        location: null,
        start_time: new Date(),
        end_time: '',
        notes: ''
      }
      
      // 重置表单验证
      if (this.$refs.scheduleForm) {
        this.$refs.scheduleForm.resetFields()
      }
    },
    
    // 提交表单
    submitScheduleForm() {
      this.$refs.scheduleForm.validate(valid => {
        if (!valid) {
          return false
        }
        
        // 准备提交的数据，不需要包含passenger字段，后端会自动处理
        const submitData = {
          ...this.scheduleForm,
          // 确保字段符合后端要求
          event_name: this.scheduleForm.event_name.trim(),
          event_type: this.scheduleForm.event_type,
          location: this.scheduleForm.location,
          start_time: this.scheduleForm.start_time,
          end_time: this.scheduleForm.end_time || null,
          flight_code: this.scheduleForm.flight_code || '',
          notes: this.scheduleForm.notes || ''
        }
        
        console.log('提交的时间安排数据:', submitData)
        
        // 提交数据
        if (this.dialogType === 'add') {
          // 创建新安排
          createSchedule(submitData).then(() => {
            this.$message.success('时间安排已创建')
            this.scheduleDialogVisible = false
            this.fetchData()
          }).catch(error => {
            console.error('创建时间安排失败:', error, error.response?.data)
            this.$message.error('创建时间安排失败: ' + (error.response?.data?.passenger?.[0] || error.message || '未知错误'))
          })
        } else {
          // 更新现有安排
          updateSchedule(this.currentSchedule.id, submitData).then(() => {
            this.$message.success('时间安排已更新')
            this.scheduleDialogVisible = false
            this.fetchData()
          }).catch(error => {
            console.error('更新时间安排失败:', error, error.response?.data)
            this.$message.error('更新时间安排失败: ' + (error.response?.data?.passenger?.[0] || error.message || '未知错误'))
          })
        }
      })
    },
    
    // 导航到地点
    navigateTo(schedule) {
      if (!schedule.location_detail || !schedule.location) {
        this.$message.warning('该时间安排没有关联的位置信息')
        return
      }
      
      console.log('导航到位置:', schedule.location_detail.name, '位置ID:', schedule.location)
      
      // 跳转到导航页面并传递目的地信息
      this.$router.push({
        path: '/passenger-navigation/index',
        query: { destination: schedule.location }
      })
    }
  }
}
</script>

<style scoped>
.schedule-container {
  padding: 20px;
}

.schedule-header-card {
  margin-bottom: 20px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
}

.page-title h2 {
  margin: 0 0 5px 0;
}

.sub-title {
  color: #909399;
  font-size: 14px;
}

.filter-bar {
  display: flex;
  align-items: center;
}

.schedule-content {
  margin-bottom: 20px;
}

.schedule-timeline-card {
  min-height: 400px;
}

.timeline-header {
  margin-bottom: 20px;
}

.timeline-header h3 {
  margin: 0;
  color: #303133;
}

.schedule-item {
  margin-bottom: 10px;
}

.schedule-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.schedule-title {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.event-name {
  font-weight: bold;
  font-size: 16px;
  margin-right: 10px;
}

.schedule-time, .schedule-location, .schedule-notes {
  margin-bottom: 8px;
  color: #606266;
}

.schedule-time i, .schedule-location i, .schedule-notes i {
  margin-right: 5px;
  color: #909399;
}

.schedule-navigate {
  margin-top: 15px;
}

.empty-schedule {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 0;
  color: #909399;
}

.empty-schedule i {
  font-size: 48px;
  margin-bottom: 15px;
}

.empty-schedule p {
  margin-bottom: 20px;
}
</style> 