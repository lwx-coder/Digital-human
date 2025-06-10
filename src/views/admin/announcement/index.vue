<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.search"
        placeholder="请输入标题或内容关键词"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select v-model="listQuery.type" placeholder="公告类型" clearable style="width: 150px" class="filter-item">
        <el-option v-for="item in typeOptions" :key="item.id" :label="item.description" :value="item.id" />
      </el-select>
      <el-select v-model="listQuery.priority" placeholder="优先级" clearable style="width: 120px" class="filter-item">
        <el-option label="低" :value="1" />
        <el-option label="中" :value="2" />
        <el-option label="高" :value="3" />
      </el-select>
      <el-select v-model="listQuery.is_active" placeholder="状态" clearable style="width: 120px" class="filter-item">
        <el-option label="激活" :value="true" />
        <el-option label="停用" :value="false" />
      </el-select>
      <el-button v-wave class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" style="margin-left: 10px;" type="success" icon="el-icon-plus" @click="handleCreate">
        添加公告
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
      <el-table-column prop="title" label="标题" min-width="180">
        <template slot-scope="{row}">
          <span class="link-type" @click="handleDetail(row)">{{ row.title }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="type_name" label="类型" width="120">
        <template slot-scope="{row}">
          <el-tag :style="{backgroundColor: row.type_color || '#909399', color: '#ffffff'}">
            <i :class="row.type_icon"></i> {{ row.type_name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="content" label="内容" min-width="200">
        <template slot-scope="{row}">
          <el-tooltip :content="row.content" effect="dark" placement="top">
            <span>{{ row.content.substring(0, 30) }}{{ row.content.length > 30 ? '...' : '' }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="priority_display" label="优先级" width="100">
        <template slot-scope="{row}">
          <el-tag :type="getPriorityTagType(row.priority)">{{ row.priority_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="100">
        <template slot-scope="{row}">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '激活' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="150">
        <template slot-scope="{row}">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="location" label="相关位置" width="120">
        <template slot-scope="{row}">
          <span>{{ row.location || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_by_username" label="创建者" width="100">
        <template slot-scope="{row}">
          <span>{{ row.created_by_username }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="250" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="primary" size="mini" @click="handleDetail(row)">
            详情
          </el-button>
          <el-button type="success" size="mini" @click="handleAnnounce(row)">
            播报
          </el-button>
          <el-button type="warning" size="mini" @click="handleUpdate(row)">
            编辑
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

    <!-- 播报对话框 -->
    <el-dialog :visible.sync="dialogAnnouncementVisible" title="公告播报">
      <digital-human ref="digitalHuman"></digital-human>
      <div style="margin-top: 20px; text-align: center;">
        <el-button type="primary" @click="playAnnouncement">开始播报</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getAnnouncementList, getAnnouncementTypeList, getAnnouncementVoiceContent, createAnnouncementBroadcast, deleteAnnouncement } from '@/api/announcement'
import Pagination from '@/components/Pagination'
import waves from '@/directive/waves'
import DigitalHuman from '@/components/DigitalHuman'

export default {
  name: 'AnnouncementList',
  components: { Pagination, DigitalHuman },
  directives: { wave: waves },
  data() {
    return {
      list: [],
      total: 0,
      loading: true,
      listQuery: {
        page: 1,
        limit: 10,
        search: '',
        type: '',
        priority: '',
        is_active: ''
      },
      typeOptions: [],
      dialogAnnouncementVisible: false,
      currentAnnouncement: null
    }
  },
  created() {
    this.getTypeList()
    this.getList()
  },
  methods: {
    getTypeList() {
      getAnnouncementTypeList().then(response => {
        this.typeOptions = response.results || []
      })
    },
    getList() {
      this.loading = true
      const params = {
        page: this.listQuery.page,
        page_size: this.listQuery.limit
      }

      // 添加筛选条件
      if (this.listQuery.type) {
        params.type = this.listQuery.type
      }
      if (this.listQuery.priority !== '') {
        params.priority = this.listQuery.priority
      }
      if (this.listQuery.is_active !== '') {
        params.is_active = this.listQuery.is_active
      }
      if (this.listQuery.search) {
        params.search = this.listQuery.search
      }

      getAnnouncementList(params).then(response => {
        this.list = response.results || []
        this.total = response.count || 0
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleCreate() {
      this.$router.push({ name: 'AddAnnouncement' })
    },
    handleUpdate(row) {
      this.$router.push({ name: 'EditAnnouncement', params: { id: row.id }})
    },
    handleDetail(row) {
      this.$router.push({ name: 'AdminAnnouncementDetail', params: { id: row.id }})
    },
    handleDelete(row) {
      this.$confirm('确定要删除该公告吗?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteAnnouncement(row.id).then(() => {
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
    handleAnnounce(row) {
      this.currentAnnouncement = row
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
</style> 