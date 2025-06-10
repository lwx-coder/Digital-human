<template>
  <div class="app-container">
    <!-- 搜索和操作栏 -->
    <div class="filter-container">
      <el-input
        v-model="listQuery.search"
        placeholder="请输入标签名称"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" style="margin-left: 10px;" type="success" icon="el-icon-plus" @click="handleCreate">
        添加标签
      </el-button>
    </div>

    <!-- 标签卡片列表 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="tag in list" :key="tag.id" :xs="24" :sm="12" :md="8" :lg="6" :xl="6">
        <el-card :body-style="{ padding: '0px' }" shadow="hover" class="tag-card">
          <div class="tag-header" :style="{ backgroundColor: tag.color }">
            <span class="tag-name">{{ tag.name }}</span>
          </div>
          <div class="tag-content">
            <div class="tag-description">{{ tag.description || '无描述' }}</div>
            <div class="tag-info">
              <span>创建时间: {{ tag.created_at | parseTime('{y}-{m}-{d}') }}</span>
            </div>
            <div class="tag-actions">
              <el-tooltip content="查看包含此标签的旅客" placement="top">
                <el-button type="text" size="mini" icon="el-icon-user" @click="handleViewTagPassengers(tag)">
                  旅客列表
                </el-button>
              </el-tooltip>
              <el-tooltip content="编辑标签" placement="top">
                <el-button type="text" size="mini" icon="el-icon-edit" @click="handleEdit(tag)">
                  编辑
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除标签" placement="top">
                <el-button type="text" size="mini" icon="el-icon-delete" @click="handleDelete(tag)">
                  删除
                </el-button>
              </el-tooltip>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分页 -->
    <pagination
      v-show="total > 0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <!-- 添加/编辑标签对话框 -->
    <el-dialog :title="dialogStatus === 'create' ? '添加标签' : '编辑标签'" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="80px" style="width: 400px; margin-left:50px;">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="temp.name" placeholder="请输入标签名称" />
        </el-form-item>
        <el-form-item label="标签颜色" prop="color">
          <el-color-picker v-model="temp.color" show-alpha />
        </el-form-item>
        <el-form-item label="标签描述" prop="description">
          <el-input
            v-model="temp.description"
            type="textarea"
            :rows="3"
            placeholder="请输入标签描述"
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="dialogStatus === 'create' ? createData() : updateData()">
          确认
        </el-button>
      </div>
    </el-dialog>

    <!-- 标签删除确认框 -->
    <el-dialog title="确认删除" :visible.sync="deleteDialogVisible" width="30%">
      <div>
        <p>确定要删除标签 "{{ tempDeleteTag.name }}" 吗？</p>
        <p class="warning-text">删除后可能会影响已使用此标签的旅客资料。</p>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmDelete">确定删除</el-button>
      </span>
    </el-dialog>

    <!-- 查看标签旅客列表对话框 -->
    <el-dialog title="包含此标签的旅客" :visible.sync="passengersDialogVisible" width="70%">
      <div v-loading="passengersLoading">
        <el-table :data="tagPassengers" border fit highlight-current-row style="width: 100%;">
          <el-table-column label="ID" prop="id" align="center" width="80" />
          <el-table-column label="用户名" prop="username" align="center" />
          <el-table-column label="姓名" align="center">
            <template slot-scope="{row}">
              {{ (row.first_name || '') + (row.last_name || '') || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="联系方式" align="center">
            <template slot-scope="{row}">
              <div>{{ row.phone || '-' }}</div>
              <div>{{ row.email || '-' }}</div>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="120">
            <template slot-scope="{row}">
              <el-button type="primary" size="mini" @click="handleViewDetail(row)">
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <pagination
          v-if="tagPassengersTotal > 0"
          :total="tagPassengersTotal"
          :page.sync="passengersQuery.page"
          :limit.sync="passengersQuery.limit"
          @pagination="getTagPassengers"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getPassengerTags, createPassengerTag, updatePassengerTag, deletePassengerTag, getTagPassengers } from '@/api/passenger'
import waves from '@/directive/waves'
import Pagination from '@/components/Pagination'
import { parseTime } from '@/utils'

export default {
  name: 'PassengerTags',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        search: ''
      },
      dialogFormVisible: false,
      dialogStatus: '',
      temp: {
        id: undefined,
        name: '',
        color: '#409EFF',
        description: ''
      },
      rules: {
        name: [{ required: true, message: '标签名称不能为空', trigger: 'blur' }],
        color: [{ required: true, message: '请选择标签颜色', trigger: 'change' }]
      },
      deleteDialogVisible: false,
      tempDeleteTag: {},
      passengersDialogVisible: false,
      passengersLoading: false,
      currentTag: {},
      tagPassengers: [],
      tagPassengersTotal: 0,
      passengersQuery: {
        page: 1,
        limit: 10
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      getPassengerTags({
        page: this.listQuery.page,
        page_size: this.listQuery.limit,
        search: this.listQuery.search || undefined
      }).then(response => {
        this.list = response.results || response
        this.total = response.count || this.list.length
        this.listLoading = false
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        name: '',
        color: '#409EFF',
        description: ''
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          createPassengerTag(this.temp).then(() => {
            this.dialogFormVisible = false
            this.$message({
              message: '创建成功',
              type: 'success'
            })
            this.getList()
          })
        }
      })
    },
    handleEdit(row) {
      this.temp = Object.assign({}, row) // 复制对象，避免影响原始数据
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          updatePassengerTag(tempData.id, tempData).then(() => {
            this.dialogFormVisible = false
            this.$message({
              message: '更新成功',
              type: 'success'
            })
            this.getList()
          })
        }
      })
    },
    handleDelete(row) {
      this.tempDeleteTag = row
      this.deleteDialogVisible = true
    },
    confirmDelete() {
      deletePassengerTag(this.tempDeleteTag.id).then(() => {
        this.$message({
          message: '删除成功',
          type: 'success'
        })
        this.deleteDialogVisible = false
        this.getList()
      })
    },
    handleViewTagPassengers(tag) {
      this.currentTag = tag
      this.passengersQuery.page = 1
      this.passengersDialogVisible = true
      this.getTagPassengers()
    },
    getTagPassengers() {
      this.passengersLoading = true
      getTagPassengers(this.currentTag.id, {
        page: this.passengersQuery.page,
        page_size: this.passengersQuery.limit
      }).then(response => {
        this.tagPassengers = response.results || []
        this.tagPassengersTotal = response.count || this.tagPassengers.length
        this.passengersLoading = false
      }).catch(() => {
        this.passengersLoading = false
      })
    },
    handleViewDetail(row) {
      this.$router.push(`/passenger-management/detail/${row.id}`)
      this.passengersDialogVisible = false
    }
  }
}
</script>

<style lang="scss" scoped>
.filter-container {
  padding-bottom: 10px;
  .filter-item {
    display: inline-block;
    vertical-align: middle;
    margin-bottom: 10px;
  }
}

.tag-card {
  margin-bottom: 20px;
  border-radius: 4px;
  overflow: hidden;

  .tag-header {
    padding: 10px;
    color: white;
    text-align: center;
    font-weight: bold;
    font-size: 16px;
  }

  .tag-content {
    padding: 15px;

    .tag-description {
      color: #606266;
      margin-bottom: 10px;
      min-height: 40px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }

    .tag-info {
      font-size: 12px;
      color: #909399;
      margin-bottom: 10px;
    }

    .tag-actions {
      display: flex;
      justify-content: space-around;
      border-top: 1px solid #ebeef5;
      padding-top: 10px;
    }
  }
}

.warning-text {
  color: #E6A23C;
  font-size: 14px;
}
</style> 