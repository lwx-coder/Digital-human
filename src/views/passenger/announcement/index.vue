<template>
  <div class="app-container">
    <!-- 紧急通知部分 -->
    <div class="emergency-section" v-if="emergencyAnnouncements.length > 0">
      <el-alert
        title="紧急通知"
        type="error"
        :closable="false"
        show-icon
      >
        <template>
          <div class="emergency-content">
            <div v-for="announcement in emergencyAnnouncements" :key="announcement.id" class="emergency-item">
              <div class="emergency-title">
                <i :class="announcement.type_icon"></i> {{ announcement.title }}
              </div>
              <div class="emergency-actions">
                <el-button type="danger" size="mini" @click="handleAnnounce(announcement)">紧急播报</el-button>
                <el-button type="text" @click="handleDetail(announcement)">查看详情</el-button>
              </div>
            </div>
          </div>
        </template>
      </el-alert>
    </div>

    <!-- 搜索部分 -->
    <div class="search-section">
      <el-card class="search-card">
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="搜索公告标题、内容或相关位置"
            prefix-icon="el-icon-search"
            clearable
            @keyup.enter.native="handleSearch"
            @clear="getList"
          />
          <el-button type="primary" @click="handleSearch">搜索</el-button>
        </div>
        <div class="filter-box">
          <el-select v-model="filterType" placeholder="公告类型" clearable @change="getList">
            <el-option v-for="item in typeOptions" :key="item.id" :label="item.description" :value="item.id" />
          </el-select>
        </div>
      </el-card>
    </div>

    <!-- 数字人部分 -->
    <div class="digital-human-section">
      <el-card class="digital-human-card">
        <div class="digital-human-container">
          <digital-human ref="digitalHuman"></digital-human>
          <el-button type="primary" @click="speakWelcomeMessage">欢迎信息</el-button>
        </div>
      </el-card>
    </div>

    <!-- 公告列表部分 -->
    <div class="announcement-list" v-loading="loading">
      <el-card v-for="announcement in announcements" :key="announcement.id" class="announcement-card">
        <div class="announcement-header">
          <div class="announcement-type">
            <el-tag :style="{backgroundColor: announcement.type_color || '#909399', color: '#ffffff'}">
              <i :class="announcement.type_icon"></i> {{ announcement.type_name }}
            </el-tag>
            <el-tag v-if="announcement.priority === 3" type="danger" style="margin-left: 5px;">重要</el-tag>
          </div>
          <div class="announcement-time">{{ formatDateTime(announcement.created_at) }}</div>
        </div>
        <div class="announcement-title" @click="handleDetail(announcement)">
          {{ announcement.title }}
        </div>
        <div class="announcement-content">
          {{ announcement.content.substring(0, 100) }}{{ announcement.content.length > 100 ? '...' : '' }}
        </div>
        <div class="announcement-footer">
          <div class="announcement-location" v-if="announcement.location">
            <i class="el-icon-location"></i> {{ announcement.location }}
          </div>
          <div class="announcement-actions">
            <el-button type="text" @click="handleDetail(announcement)">查看详情</el-button>
            <el-button type="text" @click="handleAnnounce(announcement)">
              <i class="el-icon-message"></i> 语音播报
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 无数据提示 -->
      <el-empty v-if="announcements.length === 0 && !loading" description="暂无公告信息"></el-empty>

      <!-- 分页 -->
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

    <!-- 播报对话框 -->
    <el-dialog :visible.sync="dialogAnnouncementVisible" title="公告播报" width="500px">
      <div class="dialog-content">
        <digital-human ref="announcementDigitalHuman"></digital-human>
      </div>
      <div style="margin-top: 20px; text-align: center;">
        <el-button type="primary" @click="playAnnouncement">开始播报</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getActiveAnnouncements, getEmergencyAnnouncements, getAnnouncementTypeList, getAnnouncementVoiceContent, createAnnouncementBroadcast } from '@/api/announcement'
import DigitalHuman from '@/components/DigitalHuman'

export default {
  name: 'PassengerAnnouncementList',
  components: {
    DigitalHuman
  },
  data() {
    return {
      loading: false,
      announcements: [],
      emergencyAnnouncements: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      searchQuery: '',
      filterType: '',
      typeOptions: [],
      dialogAnnouncementVisible: false,
      currentAnnouncement: null,
      welcomeMessages: [
        '欢迎使用机场信息服务系统，我是您的数字助手。您可以通过我了解最新的机场公告信息。',
        '您好，这里是机场公告信息服务。如需了解紧急通知或获取重要信息，可以点击对应公告的语音播报按钮。',
        '欢迎来到机场信息服务平台，我是您的数字助理。今天有什么可以帮到您的吗？'
      ]
    }
  },
  created() {
    this.getTypeList()
    this.getEmergencyList()
    this.getList()
  },
  methods: {
    getTypeList() {
      getAnnouncementTypeList().then(response => {
        this.typeOptions = response.results || []
      })
    },
    getEmergencyList() {
      getEmergencyAnnouncements().then(response => {
        this.emergencyAnnouncements = response.results || []
      })
    },
    getList() {
      this.loading = true
      const params = {
        page: this.currentPage,
        page_size: this.pageSize
      }
      
      if (this.searchQuery) {
        params.search = this.searchQuery
      }
      
      if (this.filterType) {
        params.type = this.filterType
      }
      
      getActiveAnnouncements(params).then(response => {
        this.announcements = response.results || []
        this.total = response.count || 0
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.getList()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.getList()
    },
    handleSearch() {
      this.currentPage = 1
      this.getList()
    },
    handleDetail(announcement) {
      this.$router.push({ 
        name: 'PassengerAnnouncementDetail', 
        params: { id: announcement.id }
      })
    },
    handleAnnounce(announcement) {
      this.currentAnnouncement = announcement
      this.dialogAnnouncementVisible = true
    },
    playAnnouncement() {
      if (!this.currentAnnouncement) return
      
      getAnnouncementVoiceContent(this.currentAnnouncement.id).then(response => {
        const voiceContent = response.voice_content
        
        // 创建播报记录
        createAnnouncementBroadcast({
          announcement_id: this.currentAnnouncement.id,
          content: voiceContent
        }).then(() => {
          // 调用数字人播报
          this.$refs.announcementDigitalHuman.speak(voiceContent)
        }).catch(error => {
          console.error('创建播报记录失败:', error)
        })
      }).catch(error => {
        console.error('获取播报内容失败:', error)
        this.$message.error('获取播报内容失败，请重试')
      })
    },
    speakWelcomeMessage() {
      const randomIndex = Math.floor(Math.random() * this.welcomeMessages.length)
      const message = this.welcomeMessages[randomIndex]
      this.$refs.digitalHuman.speak(message)
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
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  .emergency-section {
    margin-bottom: 20px;
    
    .emergency-content {
      margin-top: 10px;
      
      .emergency-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px dashed rgba(255, 100, 100, 0.3);
        
        &:last-child {
          border-bottom: none;
        }
        
        .emergency-title {
          font-weight: bold;
        }
      }
    }
  }
  
  .search-section {
    margin-bottom: 20px;
    
    .search-card {
      display: flex;
      flex-direction: column;
      gap: 10px;
      
      .search-box {
        display: flex;
        gap: 10px;
      }
      
      .filter-box {
        display: flex;
        gap: 10px;
      }
    }
  }
  
  .digital-human-section {
    margin-bottom: 20px;
    
    .digital-human-card {
      .digital-human-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        
        .el-button {
          margin-top: 15px;
        }
      }
    }
  }
  
  .announcement-list {
    .announcement-card {
      margin-bottom: 20px;
      
      .announcement-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
      }
      
      .announcement-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
        cursor: pointer;
        color: #303133;
        
        &:hover {
          color: #409EFF;
        }
      }
      
      .announcement-content {
        color: #606266;
        margin-bottom: 15px;
        line-height: 1.5;
      }
      
      .announcement-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #909399;
        
        .announcement-location {
          font-size: 14px;
        }
        
        .announcement-actions {
          display: flex;
          gap: 10px;
        }
      }
    }
  }
  
  .pagination-container {
    text-align: center;
    margin-top: 20px;
  }
  
  .dialog-content {
    display: flex;
    justify-content: center;
  }
}
</style> 