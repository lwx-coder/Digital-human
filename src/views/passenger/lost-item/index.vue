<template>
  <div class="app-container">
    <div class="header-container">
      <div class="title">我的失物信息</div>
      <el-button type="primary" icon="el-icon-plus" @click="handleAdd">报失物品</el-button>
    </div>

    <!-- 失物信息卡片列表 -->
    <div class="lost-items-container" v-loading="loading">
      <div v-if="lostItems.length === 0 && !loading" class="no-data">
        <el-empty description="您暂无失物信息，请点击"报失物品"按钮添加"></el-empty>
      </div>

      <el-card 
        v-for="item in lostItems" 
        :key="item.id" 
        class="lost-item-card"
        :class="{'broadcasted': item.is_broadcasted}"
      >
        <div class="card-header">
          <div class="item-title">
            <i :class="item.category_icon"></i> {{ item.title }}
            <el-tag v-if="item.is_broadcasted" type="success" size="mini">已广播</el-tag>
          </div>
          <div class="item-category">{{ item.category_name }}</div>
        </div>
        
        <div class="item-details">
          <div class="detail-item">
            <span class="label">丢失时间：</span>
            <span>{{ formatDateTime(item.lost_time) }}</span>
          </div>
          <div class="detail-item">
            <span class="label">丢失地点：</span>
            <span>{{ item.lost_location }}</span>
          </div>
          <div class="detail-item">
            <span class="label">处理状态：</span>
            <el-tag :type="getStatusTagType(item.status)">{{ item.status_display }}</el-tag>
          </div>
        </div>
        
        <div class="item-actions">
          <el-button type="primary" size="mini" @click="viewDetail(item)">查看详情</el-button>
        </div>
      </el-card>
    </div>

    <!-- 分页 -->
    <div class="pagination-container" v-if="total > 0">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next, jumper"
        :current-page.sync="listQuery.page"
        :page-sizes="[5, 10, 20]"
        :page-size.sync="listQuery.limit"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script>
import { getMyLostItems } from '@/api/lost-item'

export default {
  name: 'PassengerLostItemList',
  data() {
    return {
      loading: false,
      lostItems: [],
      total: 0,
      listQuery: {
        page: 1,
        limit: 10
      }
    }
  },
  created() {
    this.fetchLostItems()
  },
  methods: {
    fetchLostItems() {
      this.loading = true
      getMyLostItems({
        page: this.listQuery.page,
        page_size: this.listQuery.limit
      }).then(response => {
        this.lostItems = response.results || []
        this.total = response.count || 0
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    handleSizeChange(val) {
      this.listQuery.limit = val
      this.fetchLostItems()
    },
    handleCurrentChange(val) {
      this.listQuery.page = val
      this.fetchLostItems()
    },
    handleAdd() {
      this.$router.push({ name: 'AddLostItem' })
    },
    viewDetail(item) {
      this.$router.push({ 
        name: 'PassengerLostItemDetail', 
        params: { id: item.id } 
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
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    .title {
      font-size: 20px;
      font-weight: bold;
    }
  }
  
  .lost-items-container {
    margin-bottom: 20px;
    
    .no-data {
      padding: 30px 0;
    }
    
    .lost-item-card {
      margin-bottom: 15px;
      transition: all 0.3s;
      
      &.broadcasted {
        border-left: 4px solid #67C23A;
      }
      
      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        
        .item-title {
          font-size: 16px;
          font-weight: bold;
          
          .el-tag {
            margin-left: 5px;
          }
        }
        
        .item-category {
          color: #909399;
        }
      }
      
      .item-details {
        margin-bottom: 15px;
        
        .detail-item {
          margin-bottom: 5px;
          
          .label {
            color: #606266;
            margin-right: 5px;
          }
        }
      }
      
      .item-actions {
        display: flex;
        justify-content: flex-end;
      }
    }
  }
  
  .pagination-container {
    text-align: center;
  }
}
</style> 