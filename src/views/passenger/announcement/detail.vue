<template>
  <div class="app-container">
    <el-card class="detail-card" v-loading="loading">
      <div slot="header" class="clearfix">
        <span>公告详情</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="goBack">返回列表</el-button>
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
            </div>
          </div>
          <div class="announcement-meta">
            <div class="meta-item">
              <span class="meta-label">发布时间：</span>
              <span>{{ formatDateTime(announcement.created_at) }}</span>
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
          <div class="content-title">公告内容：</div>
          <div class="content-text">{{ announcement.content }}</div>
        </div>
        
        <div class="digital-human-container">
          <div class="section-title">语音播报</div>
          <digital-human ref="digitalHuman"></digital-human>
          <div class="action-buttons">
            <el-button type="primary" @click="handleAnnounce">开始播报</el-button>
          </div>
        </div>
      </div>
      
      <div v-else-if="!loading" class="no-data">
        <i class="el-icon-warning-outline"></i>
        <p>未找到公告信息或公告已过期</p>
        <el-button type="primary" @click="goBack">返回列表</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { getAnnouncementDetail, getAnnouncementVoiceContent, createAnnouncementBroadcast } from '@/api/announcement'
import DigitalHuman from '@/components/DigitalHuman'

export default {
  name: 'PassengerAnnouncementDetail',
  components: {
    DigitalHuman
  },
  data() {
    return {
      loading: false,
      announcement: null,
      announcementId: null,
      typeName: '',
      typeColor: '#909399',
      typeIcon: 'el-icon-message'
    }
  },
  created() {
    this.announcementId = this.$route.params.id
    this.fetchAnnouncementDetail()
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
    goBack() {
      this.$router.push({ name: 'PassengerAnnouncementList' })
    },
    handleAnnounce() {
      getAnnouncementVoiceContent(this.announcementId).then(response => {
        const voiceContent = response.voice_content
        
        // 创建播报记录
        createAnnouncementBroadcast({
          announcement_id: this.announcementId,
          content: voiceContent
        }).then(() => {
          // 调用数字人播报
          this.$refs.digitalHuman.speak(voiceContent)
        }).catch(error => {
          console.error('创建播报记录失败:', error)
        })
      }).catch(error => {
        console.error('获取播报内容失败:', error)
        this.$message.error('获取播报内容失败，请重试')
      })
    },
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return '-'
      const date = new Date(dateTimeStr)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
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
    max-width: 800px;
    margin: 0 auto;
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