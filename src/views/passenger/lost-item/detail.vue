<template>
  <div class="app-container">
    <el-card class="detail-card" v-loading="loading">
      <div slot="header" class="clearfix">
        <span>失物详情</span>
        <el-button type="text" @click="goBack" style="float: right">返回列表</el-button>
      </div>
      
      <div v-if="lostItem" class="lost-item-detail">
        <div class="detail-header">
          <div class="item-title">
            <h2>{{ lostItem.title }}</h2>
            <div class="item-tags">
              <el-tag type="primary">{{ categoryName }}</el-tag>
              <el-tag :type="getStatusTagType(lostItem.status)">{{ lostItem.status_display }}</el-tag>
              <el-tag v-if="lostItem.is_broadcasted" type="success">已广播</el-tag>
            </div>
          </div>
          
          <div class="item-meta">
            <div class="meta-item">
              <span class="meta-label">提交时间：</span>
              <span>{{ formatDateTime(lostItem.created_at) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">丢失时间：</span>
              <span>{{ formatDateTime(lostItem.lost_time) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">丢失地点：</span>
              <span>{{ lostItem.lost_location }}</span>
            </div>
          </div>
        </div>
        
        <div class="item-image" v-if="lostItem.image">
          <img :src="lostItem.image" alt="物品图片">
        </div>
        
        <div class="item-description">
          <div class="description-title">物品描述</div>
          <div class="description-content">{{ lostItem.description }}</div>
        </div>
        
        <div class="item-contact">
          <div class="contact-title">联系信息</div>
          <div class="contact-item">
            <span class="contact-label">联系人：</span>
            <span>{{ lostItem.contact_name }}</span>
          </div>
          <div class="contact-item">
            <span class="contact-label">联系电话：</span>
            <span>{{ lostItem.contact_phone }}</span>
          </div>
          <div class="contact-item" v-if="lostItem.contact_email">
            <span class="contact-label">联系邮箱：</span>
            <span>{{ lostItem.contact_email }}</span>
          </div>
        </div>
        
        <div class="item-status" v-if="lostItem.admin_notes">
          <div class="status-title">处理备注</div>
          <div class="status-content">{{ lostItem.admin_notes }}</div>
        </div>
        
        <div class="item-broadcasts" v-if="hasAnyBroadcasts">
          <div class="broadcasts-title">广播记录</div>
          <div class="broadcasts-list">
            <div v-for="(broadcast, index) in lostItem.broadcasts" :key="index" class="broadcast-item">
              <div class="broadcast-time">{{ formatDateTime(broadcast.broadcast_at) }}</div>
              <div class="broadcast-content">{{ broadcast.content }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else-if="!loading" class="no-data">
        <el-empty description="未找到失物信息"></el-empty>
        <el-button type="primary" @click="goBack">返回列表</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { getLostItemDetail } from '@/api/lost-item'

export default {
  name: 'PassengerLostItemDetail',
  data() {
    return {
      loading: false,
      lostItem: null,
      categoryName: ''
    }
  },
  created() {
    this.fetchLostItemDetail()
  },
  computed: {
    hasAnyBroadcasts() {
      return this.lostItem && this.lostItem.broadcasts && this.lostItem.broadcasts.length > 0
    }
  },
  methods: {
    fetchLostItemDetail() {
      const id = this.$route.params.id
      if (!id) {
        this.$message.error('参数错误')
        this.goBack()
        return
      }
      
      this.loading = true
      getLostItemDetail(id).then(response => {
        this.lostItem = response
        
        // 获取类别名称
        if (response.category_data) {
          this.categoryName = response.category_data.description
        }
        
        this.loading = false
      }).catch(error => {
        console.error('获取失物详情失败:', error)
        this.$message.error('获取失物详情失败，请重试')
        this.loading = false
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
    getStatusTagType(status) {
      const statusMap = {
        'lost': 'danger',
        'found': 'warning',
        'claimed': 'success',
        'closed': 'info'
      }
      return statusMap[status] || 'info'
    },
    goBack() {
      this.$router.push({ name: 'PassengerLostItemList' })
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
  
  .lost-item-detail {
    .detail-header {
      margin-bottom: 20px;
      
      .item-title {
        margin-bottom: 15px;
        
        h2 {
          margin-top: 0;
          margin-bottom: 10px;
          color: #303133;
        }
        
        .item-tags {
          .el-tag {
            margin-right: 8px;
          }
        }
      }
      
      .item-meta {
        background-color: #f5f7fa;
        padding: 15px;
        border-radius: 4px;
        
        .meta-item {
          margin-bottom: 8px;
          
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
    
    .item-image {
      margin-bottom: 20px;
      text-align: center;
      
      img {
        max-width: 100%;
        max-height: 300px;
        border-radius: 4px;
      }
    }
    
    .item-description, .item-contact, .item-status, .item-broadcasts {
      margin-bottom: 20px;
      
      .description-title, .contact-title, .status-title, .broadcasts-title {
        font-weight: bold;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px solid #ebeef5;
        color: #303133;
      }
      
      .description-content, .status-content {
        line-height: 1.6;
        color: #606266;
        white-space: pre-line;
      }
    }
    
    .item-contact {
      .contact-item {
        margin-bottom: 8px;
        
        .contact-label {
          font-weight: bold;
          color: #606266;
        }
      }
    }
    
    .item-broadcasts {
      .broadcasts-list {
        .broadcast-item {
          margin-bottom: 15px;
          padding-bottom: 15px;
          border-bottom: 1px dashed #ebeef5;
          
          &:last-child {
            margin-bottom: 0;
            padding-bottom: 0;
            border-bottom: none;
          }
          
          .broadcast-time {
            font-size: 13px;
            color: #909399;
            margin-bottom: 5px;
          }
          
          .broadcast-content {
            color: #606266;
            line-height: 1.6;
          }
        }
      }
    }
  }
  
  .no-data {
    text-align: center;
    padding: 30px 0;
    
    .el-button {
      margin-top: 15px;
    }
  }
}
</style> 