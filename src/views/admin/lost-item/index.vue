<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.search"
        placeholder="搜索物品名称、描述、丢失地点等"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select v-model="listQuery.category" placeholder="物品类别" clearable style="width: 150px" class="filter-item">
        <el-option v-for="item in categoryOptions" :key="item.id" :label="item.description" :value="item.id" />
      </el-select>
      <el-select v-model="listQuery.status" placeholder="处理状态" clearable style="width: 120px" class="filter-item">
        <el-option label="寻物中" value="lost" />
        <el-option label="已找到" value="found" />
        <el-option label="已认领" value="claimed" />
        <el-option label="已关闭" value="closed" />
      </el-select>
      <el-select v-model="listQuery.is_broadcasted" placeholder="广播状态" clearable style="width: 120px" class="filter-item">
        <el-option label="已广播" :value="true" />
        <el-option label="未广播" :value="false" />
      </el-select>
      <el-button v-wave class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" style="margin-left: 10px;" type="warning" icon="el-icon-bell" @click="handlePendingItems">
        待处理 <el-badge v-if="pendingCount > 0" :value="pendingCount" class="item" />
      </el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%"
    >
      <el-table-column prop="title" label="物品名称" min-width="150">
        <template slot-scope="{row}">
          <span class="link-type" @click="handleDetail(row)">{{ row.title }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="category_name" label="类别" width="120">
        <template slot-scope="{row}">
          <el-tag>
            <i :class="row.category_icon"></i> {{ row.category_name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="lost_location" label="丢失地点" min-width="150" />
      <el-table-column prop="lost_time" label="丢失时间" width="150">
        <template slot-scope="{row}">
          {{ formatDateTime(row.lost_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="contact_name" label="联系人" width="100" />
      <el-table-column prop="status_display" label="状态" width="100">
        <template slot-scope="{row}">
          <el-tag :type="getStatusTagType(row.status)">{{ row.status_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_broadcasted" label="广播" width="80" align="center">
        <template slot-scope="{row}">
          <el-tag v-if="row.is_broadcasted" type="success">已广播</el-tag>
          <el-tag v-else type="info">未广播</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="报失时间" width="150">
        <template slot-scope="{row}">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="230" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="primary" size="mini" @click="handleDetail(row)">
            详情
          </el-button>
          <el-button 
            v-if="!row.is_broadcasted" 
            type="success" 
            size="mini" 
            @click="handleBroadcast(row)"
          >
            广播
          </el-button>
          <el-button type="warning" size="mini" @click="handleUpdate(row)">
            处理
          </el-button>
          <el-button type="danger" size="mini" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total > 0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <!-- 广播对话框 -->
    <el-dialog :visible.sync="dialogBroadcastVisible" title="失物广播" width="600px">
      <digital-human ref="digitalHuman"></digital-human>
      <div class="broadcast-content" v-if="currentItem">
        <div class="content-title">广播内容预览</div>
        <div class="content-text">{{ broadcastContent }}</div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogBroadcastVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBroadcast">确认广播</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getLostItemList, getItemCategoryList, getPendingLostItems, getLostItemBroadcastContent, createLostItemBroadcast, deleteLostItem } from '@/api/lost-item'
import Pagination from '@/components/Pagination'
import waves from '@/directive/waves'
import DigitalHuman from '@/components/DigitalHuman'

export default {
  name: 'AdminLostItemList',
  components: { Pagination, DigitalHuman },
  directives: { wave: waves },
  data() {
    return {
      loading: true,
      list: [],
      total: 0,
      listQuery: {
        page: 1,
        limit: 10,
        search: '',
        category: '',
        status: '',
        is_broadcasted: ''
      },
      categoryOptions: [],
      pendingCount: 0,
      // 广播相关
      dialogBroadcastVisible: false,
      currentItem: null,
      broadcastContent: ''
    }
  },
  created() {
    this.getCategoryList()
    this.getList()
    this.getPendingCount()
  },
  methods: {
    getCategoryList() {
      getItemCategoryList().then(response => {
        this.categoryOptions = response.results || []
      })
    },
    getList() {
      this.loading = true
      const params = {
        page: this.listQuery.page,
        page_size: this.listQuery.limit
      }

      // 添加筛选条件
      if (this.listQuery.category) {
        params.category = this.listQuery.category
      }
      if (this.listQuery.status) {
        params.status = this.listQuery.status
      }
      if (this.listQuery.is_broadcasted !== '') {
        params.is_broadcasted = this.listQuery.is_broadcasted
      }
      if (this.listQuery.search) {
        params.search = this.listQuery.search
      }

      getLostItemList(params).then(response => {
        this.list = response.results || []
        this.total = response.count || 0
        this.loading = false
        
        // 刷新待处理数量
        this.getPendingCount()
      }).catch(() => {
        this.loading = false
      })
    },
    getPendingCount() {
      getPendingLostItems({ page_size: 1 }).then(response => {
        this.pendingCount = response.count || 0
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handlePendingItems() {
      this.listQuery.status = 'lost'
      this.listQuery.is_broadcasted = false
      this.listQuery.page = 1
      this.getList()
    },
    handleDetail(row) {
      this.$router.push({ name: 'AdminLostItemDetail', params: { id: row.id }})
    },
    handleUpdate(row) {
      this.$router.push({ name: 'EditLostItem', params: { id: row.id }})
    },
    handleBroadcast(row) {
      this.currentItem = row
      this.dialogBroadcastVisible = true
      
      // 获取广播内容
      getLostItemBroadcastContent(row.id).then(response => {
        this.broadcastContent = response.broadcast_content
      })
    },
    confirmBroadcast() {
      if (!this.currentItem || !this.broadcastContent) {
        this.$message.error('广播内容不能为空')
        return
      }
      
      createLostItemBroadcast({
        lost_item_id: this.currentItem.id,
        content: this.broadcastContent
      }).then(response => {
        // 播放语音
        this.$refs.digitalHuman.speak(this.broadcastContent)
        
        // 更新状态
        this.$message.success('广播成功')
        
        // 关闭对话框并刷新列表
        setTimeout(() => {
          this.dialogBroadcastVisible = false
          this.getList()
        }, 500)
      }).catch(error => {
        console.error('广播失败:', error)
        this.$message.error('广播失败，请重试')
      })
    },
    handleDelete(row) {
      this.$confirm('确定要删除该失物信息吗?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteLostItem(row.id).then(() => {
          this.$message({
            type: 'success',
            message: '删除成功!'
          })
          this.getList()
        })
      }).catch(() => {
        // 取消删除
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
.filter-container {
  padding-bottom: 10px;
  .filter-item {
    margin-right: 10px;
    margin-bottom: 10px;
  }
}

.link-type {
  color: #409EFF;
  cursor: pointer;
  text-decoration: none;
  &:hover {
    text-decoration: underline;
  }
}

.broadcast-content {
  margin-top: 20px;
  
  .content-title {
    font-weight: bold;
    margin-bottom: 10px;
  }
  
  .content-text {
    background-color: #f5f7fa;
    padding: 10px;
    border-radius: 4px;
    line-height: 1.6;
  }
}
</style> 