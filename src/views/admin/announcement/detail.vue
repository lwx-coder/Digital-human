<template>
  <div class="app-container">
    <el-card class="detail-card" v-loading="loading">
      <div slot="header" class="clearfix">
        <span>公告详情</span>
        <div class="header-actions">
          <el-button type="warning" size="small" @click="handleEdit">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDelete">删除</el-button>
          <el-button type="text" @click="goBack">返回列表</el-button>
        </div>
      </div>
      
      <div v-if="announcement" class="announcement-detail">
        <div class="announcement-header">
          <div class="announcement-title">
            <h2>{{ announcement.title }}</h2>
            <div class="announcement-tags">
              <el-tag :style="{backgroundColor: typeColor, color: '#ffffff'}" class="tag-item">
                <i :class="typeIcon"></i> {{ typeName }}
              </el-tag>
              <el-tag :type="getPriorityTagType(announcement.priority)" class="tag-item">
                {{ announcement.priority_display }}
              </el-tag>
              <el-tag :type="announcement.is_active ? 'success' : 'info'" class="tag-item">
                {{ announcement.is_active ? '已激活' : '已停用' }}
              </el-tag>
            </div>
          </div>
          <div class="announcement-meta">
            <div class="meta-item">
              <span class="meta-label">创建者：</span>
              <span>{{ announcement.created_by_username }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">创建时间：</span>
              <span>{{ formatDateTime(announcement.created_at) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">更新时间：</span>
              <span>{{ formatDateTime(announcement.updated_at) }}</span>
            </div>
            <div class="meta-item" v-if="announcement.location">
              <span class="meta-label">相关位置：</span>
              <span>{{ announcement.location }}</span>
            </div>
            <div class="meta-item" v-if="announcement.start_time">
              <span class="meta-label">生效时间：</span>
              <span>{{ formatDateTime(announcement.start_time) }}</span>
            </div>
            <div class="meta-item" v-if="announcement.end_time">
              <span class="meta-label">失效时间：</span>
              <span>{{ formatDateTime(announcement.end_time) }}</span>
            </div>
          </div>
        </div>
        
        <div class="announcement-content">
          <div class="content-title">公告内容</div>
          <div class="content-text">{{ announcement.content }}</div>
        </div>
        
        <div class="digital-human-container">
          <div class="section-title">语音播报</div>
          <digital-human ref="digitalHuman"></digital-human>
          <div class="action-buttons">
            <el-button type="primary" @click="handleAnnounce">开始播报</el-button>
          </div>
        </div>
        
        <div class="broadcast-history">
          <div class="section-title">播报历史</div>
          <el-table
            v-loading="historyLoading"
            :data="broadcastHistory"
            border
            fit
            style="width: 100%"
          >
            <el-table-column prop="broadcast_at" label="播报时间" width="180">
              <template slot-scope="{row}">
                {{ formatDateTime(row.broadcast_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="broadcast_by_username" label="播报者" width="120"></el-table-column>
            <el-table-column prop="content" label="播报内容">
              <template slot-scope="{row}">
                <el-tooltip 
                  :content="row.content" 
                  effect="dark" 
                  placement="top" 
                  :disabled="row.content.length <= 50"
                >
                  <span>{{ row.content.substring(0, 50) }}{{ row.content.length > 50 ? '...' : '' }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center">
              <template slot-scope="{row}">
                <el-button type="text" @click="replayAnnouncement(row)">
                  <i class="el-icon-video-play"></i> 重播
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination-container">
            <el-pagination
              background
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              :current-page.sync="currentPage"
              :page-sizes="[5, 10, 20]"
              :page-size="pageSize"
              layout="total, sizes, prev, pager, next, jumper"
              :total="total">
            </el-pagination>
          </div>
        </div>
      </div>
      
      <div v-else-if="!loading" class="no-data">
        <i class="el-icon-warning-outline"></i>
        <p>未找到公告信息</p>
        <el-button type="primary" @click="goBack">返回列表</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { getAnnouncementDetail, getAnnouncementVoiceContent, getBroadcastHistory, createAnnouncementBroadcast, deleteAnnouncement } from '@/api/announcement'
import DigitalHuman from '@/components/DigitalHuman'

export default {
  name: 'AdminAnnouncementDetail',
  components: {
    DigitalHuman
  },
  data() {
    return {
      loading: false,
      historyLoading: false,
      announcement: null,
      announcementId: null,
      typeName: '',
      typeColor: '#909399',
      typeIcon: 'el-icon-message',
      broadcastHistory: [],
      currentPage: 1,
      pageSize: 10,
      total: 0
    }
  },
  created() {
    this.announcementId = this.$route.params.id
    this.fetchAnnouncementDetail()
    this.fetchBroadcastHistory()
  },
  methods: {
    fetchAnnouncementDetail() {
      this.loading = true
      getAnnouncementDetail(this.announcementId).then(response => {
        this.announcement = response
        
        // 提取类型信息
        if (response.type_data) {
          this.typeName = response.type_data.description
          this.typeColor = response.type_data.color || '#909399'
          this.typeIcon = response.type_data.icon || 'el-icon-message'
        }
        
        this.loading = false
      }).catch(error => {
        console.error('获取公告详情失败:', error)
        this.$message.error('获取公告详情失败，请重试')
        this.loading = false
      })
    },
    fetchBroadcastHistory() {
      this.historyLoading = true
      getBroadcastHistory({
        announcement: this.announcementId,
        page: this.currentPage,
        page_size: this.pageSize
      }).then(response => {
        this.broadcastHistory = response.results || []
        this.total = response.count || 0
        this.historyLoading = false
      }).catch(error => {
        console.error('获取播报历史失败:', error)
        this.historyLoading = false
      })
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.fetchBroadcastHistory()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchBroadcastHistory()
    },
    goBack() {
      this.$router.push({ name: 'AdminAnnouncementList' })
    },
    handleEdit() {
      this.$router.push({ name: 'EditAnnouncement', params: { id: this.announcementId }})
    },
    handleDelete() {
      this.$confirm('确定要删除该公告吗?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteAnnouncement(this.announcementId).then(() => {
          this.$message({
            type: 'success',
            message: '删除成功!'
          })
          this.goBack()
        }).catch(error => {
          console.error('删除公告失败:', error)
          this.$message.error('删除公告失败，请重试')
        })
      }).catch(() => {
        // 取消删除
      })
    },
    handleAnnounce() {
      getAnnouncementVoiceContent(this.announcementId).then(response => {
        const voiceContent = response.voice_content
        
        // 创建播报记录
        createAnnouncementBroadcast({
          announcement_id: this.announcementId,
          content: voiceContent
        }).then(response => {
          // 调用数字人播报
          this.$refs.digitalHuman.speak(voiceContent)
          
          // 刷新播报历史
          this.fetchBroadcastHistory()
        }).catch(error => {
          console.error('创建播报记录失败:', error)
        })
      }).catch(error => {
        console.error('获取播报内容失败:', error)
        this.$message.error('获取播报内容失败，请重试')
      })
    },
    replayAnnouncement(record) {
      this.$refs.digitalHuman.speak(record.content)
    },
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return '-'
      const date = new Date(dateTimeStr)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    getPriorityTagType(priority) {
      const priorityMap = {
        1: 'info',
        2: 'warning',
        3: 'danger'
      }
      return priorityMap[priority] || 'info'
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  .detail-card {
    max-width: 900px;
    margin: 0 auto;
    
    .header-actions {
      float: right;
      
      .el-button {
        margin-left: 10px;
      }
    }
  }
  
  .announcement-detail {
    .announcement-header {
      margin-bottom: 30px;
      
      .announcement-title {
        margin-bottom: 20px;
        
        h2 {
          margin-top: 0;
          margin-bottom: 15px;
          font-size: 24px;
          color: #303133;
        }
        
        .announcement-tags {
          .tag-item {
            margin-right: 10px;
          }
        }
      }
      
      .announcement-meta {
        background-color: #f5f7fa;
        padding: 15px;
        border-radius: 4px;
        
        .meta-item {
          margin-bottom: 10px;
          
          &:last-child {
            margin-bottom: 0;
          }
          
          .meta-label {
            font-weight: bold;
            color: #606266;
          }
        }
      }
    }
    
    .announcement-content {
      margin-bottom: 30px;
      
      .content-title {
        font-weight: bold;
        margin-bottom: 10px;
        color: #303133;
      }
      
      .content-text {
        line-height: 1.8;
        color: #606266;
        white-space: pre-line;
        padding: 15px;
        background-color: #fff;
        border: 1px solid #ebeef5;
        border-radius: 4px;
      }
    }
    
    .digital-human-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: 30px;
      
      .section-title {
        align-self: flex-start;
        font-weight: bold;
        margin-bottom: 15px;
        color: #303133;
      }
      
      .action-buttons {
        margin-top: 15px;
      }
    }
    
    .broadcast-history {
      .section-title {
        font-weight: bold;
        margin-bottom: 15px;
        color: #303133;
      }
      
      .pagination-container {
        margin-top: 20px;
        text-align: center;
      }
    }
  }
  
  .no-data {
    text-align: center;
    padding: 50px 0;
    
    i {
      font-size: 60px;
      color: #909399;
      margin-bottom: 15px;
    }
    
    p {
      margin-bottom: 20px;
      color: #606266;
    }
  }
}
</style> 