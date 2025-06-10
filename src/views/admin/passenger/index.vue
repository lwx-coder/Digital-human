<template>
  <div class="app-container">
    <!-- 搜索区域 -->
    <div class="filter-container">
      <el-input
        v-model="listQuery.search"
        placeholder="请输入用户名、邮箱或手机号"
        style="width: 250px"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select v-model="listQuery.tag" placeholder="标签" clearable class="filter-item" style="width: 130px" @change="handleFilter">
        <el-option v-for="item in tagOptions" :key="item.id" :label="item.name" :value="item.id">
          <el-tag :color="item.color" style="margin-right: 10px">{{ item.name }}</el-tag>
        </el-option>
      </el-select>
      <el-select v-model="listQuery.vip_level" placeholder="VIP等级" clearable class="filter-item" style="width: 120px" @change="handleFilter">
        <el-option v-for="i in 5" :key="i" :label="`VIP${i}`" :value="i" />
      </el-select>
      <el-select v-model="listQuery.is_active" placeholder="状态" clearable class="filter-item" style="width: 120px" @change="handleFilter">
        <el-option label="激活" value="true" />
        <el-option label="未激活" value="false" />
      </el-select>
      <el-select v-model="listQuery.last_login_days" placeholder="最近登录" clearable class="filter-item" style="width: 120px" @change="handleFilter">
        <el-option label="7天内" value="7" />
        <el-option label="30天内" value="30" />
        <el-option label="90天内" value="90" />
      </el-select>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button v-waves class="filter-item" style="margin-left: 10px;" type="warning" icon="el-icon-download" @click="handleExport">
        导出
      </el-button>
    </div>

    <!-- 数据表格 -->
    <el-table
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column label="ID" prop="id" align="center" width="80" />
      <el-table-column label="头像" width="85" align="center">
        <template slot-scope="{row}">
          <el-avatar :src="row.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" :size="40" />
        </template>
      </el-table-column>
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
      <el-table-column label="VIP等级" align="center" width="100">
        <template slot-scope="{row}">
          <el-rate
            v-model="row.vip_level"
            disabled
            text-color="#ff9900"
            show-score
            :max="5"
          />
        </template>
      </el-table-column>
      <el-table-column label="标签" align="center">
        <template slot-scope="{row}">
          <el-tag
            v-for="tag in row.tags"
            :key="tag.id"
            :color="tag.color"
            size="small"
            style="margin-right: 5px; margin-bottom: 5px;"
          >
            {{ tag.name }}
          </el-tag>
          <span v-if="!row.tags || row.tags.length === 0">-</span>
        </template>
      </el-table-column>
      <el-table-column label="失物记录" prop="lost_items_count" align="center" width="90" />
      <el-table-column label="状态" align="center" width="100">
        <template slot-scope="{row}">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '激活' : '未激活' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="注册日期" align="center" width="160">
        <template slot-scope="{row}">
          {{ row.date_joined | parseTime }}
        </template>
      </el-table-column>
      <el-table-column label="最后登录" align="center" width="160">
        <template slot-scope="{row}">
          {{ row.last_login | parseTime || '从未登录' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="150" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="primary" size="mini" @click="handleDetail(row)">
            详情
          </el-button>
          <el-button size="mini" type="success" @click="handleAddNote(row)">
            备注
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <pagination
      v-show="total > 0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <!-- 添加备注对话框 -->
    <el-dialog title="添加旅客备注" :visible.sync="noteDialogVisible" width="500px">
      <el-form ref="noteForm" :model="noteForm" :rules="noteRules" label-width="80px">
        <el-form-item label="备注内容" prop="note">
          <el-input
            v-model="noteForm.note"
            type="textarea"
            :rows="4"
            placeholder="请输入备注内容..."
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="noteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitNoteForm">确认</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getPassengerList, getPassengerTags, addPassengerNote } from '@/api/passenger'
import waves from '@/directive/waves'
import Pagination from '@/components/Pagination'
import { parseTime } from '@/utils'

export default {
  name: 'PassengerList',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 10,
        search: '',
        tag: '',
        vip_level: '',
        is_active: '',
        last_login_days: '',
        ordering: '-date_joined'
      },
      tagOptions: [],
      noteDialogVisible: false,
      noteForm: {
        passengerId: null,
        note: ''
      },
      noteRules: {
        note: [{ required: true, message: '请输入备注内容', trigger: 'blur' }]
      },
      downloadLoading: false
    }
  },
  created() {
    this.getList()
    this.getTags()
  },
  methods: {
    getList() {
      this.listLoading = true
      const params = {
        page: this.listQuery.page,
        page_size: this.listQuery.limit,
        search: this.listQuery.search || undefined,
        tag: this.listQuery.tag || undefined,
        vip_level: this.listQuery.vip_level || undefined,
        is_active: this.listQuery.is_active || undefined,
        last_login_days: this.listQuery.last_login_days || undefined,
        ordering: this.listQuery.ordering
      }

      getPassengerList(params).then(response => {
        this.list = response.results
        this.total = response.count
        this.listLoading = false
      }).catch(() => {
        this.listLoading = false
      })
    },
    getTags() {
      getPassengerTags().then(response => {
        this.tagOptions = response.results || response // 根据API返回格式调整
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleDetail(row) {
      this.$router.push(`/passenger-management/detail/${row.id}`)
    },
    handleAddNote(row) {
      this.noteForm.passengerId = row.id
      this.noteForm.note = ''
      this.noteDialogVisible = true
      this.$nextTick(() => {
        this.$refs.noteForm && this.$refs.noteForm.clearValidate()
      })
    },
    submitNoteForm() {
      this.$refs.noteForm.validate(valid => {
        if (valid) {
          const data = {
            note: this.noteForm.note
          }
          addPassengerNote(this.noteForm.passengerId, data).then(() => {
            this.$message({
              type: 'success',
              message: '添加备注成功!'
            })
            this.noteDialogVisible = false
          })
        }
      })
    },
    handleExport() {
      this.$confirm('确认导出所有旅客数据?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.downloadLoading = true
        // 先加载所有数据
        getPassengerList({ page_size: 1000 }).then(response => {
          const exportData = response.results || [];
          import('@/vendor/Export2Excel').then(excel => {
            try {
              const tHeader = ['ID', '用户名', '姓名', '邮箱', '手机', 'VIP等级', '状态', '注册日期', '最后登录']
              const filterVal = ['id', 'username', 'name', 'email', 'phone', 'vip_level', 'is_active', 'date_joined', 'last_login']
              const data = this.formatJson(filterVal, exportData)
              excel.export_json_to_excel({
                header: tHeader,
                data,
                filename: '旅客数据',
                autoWidth: true,
                bookType: 'xlsx'
              })
            } catch (error) {
              console.error('导出失败:', error)
              this.$message.error(`导出失败: ${error.message}`)
            } finally {
              this.downloadLoading = false
            }
          }).catch(error => {
            console.error('加载导出模块失败:', error)
            this.$message.error(`加载导出模块失败: ${error.message}`)
            this.downloadLoading = false
          })
        }).catch(error => {
          console.error('获取数据失败:', error)
          this.$message.error(`获取数据失败: ${error.message}`)
          this.downloadLoading = false
        })
      }).catch(() => {
        // 用户取消操作
      })
    },
    formatJson(filterVal, jsonData) {
      return jsonData.map(v => filterVal.map(j => {
        if (j === 'name') {
          return (v.first_name || '') + (v.last_name || '')
        } else if (j === 'date_joined' || j === 'last_login') {
          return v[j] ? parseTime(v[j]) : ''
        } else if (j === 'is_active') {
          return v[j] ? '激活' : '未激活'
        } else {
          return v[j]
        }
      }))
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
    margin-right: 10px;
  }
}
</style> 