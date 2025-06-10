<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.search"
        placeholder="航班号/航空公司/城市"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select v-model="listQuery.status" placeholder="航班状态" clearable style="width: 120px" class="filter-item">
        <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" style="margin-left: 10px;" type="success" icon="el-icon-plus" @click="handleCreate">
        添加航班
      </el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="list"
      element-loading-text="加载中..."
      border
      fit
      highlight-current-row
      style="width: 100%"
    >
      <el-table-column label="航班号" prop="flight_number" align="center" min-width="100">
        <template slot-scope="{row}">
          <span>{{ row.flight_number }}</span>
        </template>
      </el-table-column>
      <el-table-column label="航空公司" prop="airline" align="center" min-width="120">
        <template slot-scope="{row}">
          <span>{{ row.airline }}</span>
        </template>
      </el-table-column>
      <el-table-column label="出发城市" prop="departure_city" align="center" min-width="100">
        <template slot-scope="{row}">
          <span>{{ row.departure_city }}</span>
        </template>
      </el-table-column>
      <el-table-column label="到达城市" prop="arrival_city" align="center" min-width="100">
        <template slot-scope="{row}">
          <span>{{ row.arrival_city }}</span>
        </template>
      </el-table-column>
      <el-table-column label="计划出发时间" align="center" min-width="150">
        <template slot-scope="{row}">
          <span>{{ formatDateTime(row.scheduled_departure_time) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="计划到达时间" align="center" min-width="150">
        <template slot-scope="{row}">
          <span>{{ formatDateTime(row.scheduled_arrival_time) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" align="center" min-width="100">
        <template slot-scope="{row}">
          <el-tag :type="getStatusType(row.status)">{{ row.status_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" min-width="200" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="primary" size="mini" @click="handleDetail(row)">
            详情
          </el-button>
          <el-button type="success" size="mini" @click="handleVoiceAnnounce(row)">
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
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />
    
    <!-- 语音播报对话框 -->
    <el-dialog title="数字人播报" :visible.sync="dialogVisible" width="30%">
      <div class="digital-human-dialog">
        <digital-human ref="digitalHuman"></digital-human>
        <div class="voice-content">
          <p>当前播报内容:</p>
          <el-input
            type="textarea"
            :rows="4"
            v-model="voiceContent"
            placeholder="播报内容"
          ></el-input>
        </div>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAnnounce">确认播报</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getFlightList, deleteFlight, getFlightVoiceStatus, createFlightAnnouncement } from '@/api/flight'
import Pagination from '@/components/Pagination'
import DigitalHuman from '@/components/DigitalHuman'

export default {
  name: 'AdminFlightManagement',
  components: { Pagination, DigitalHuman },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      dialogVisible: false,
      voiceContent: '',
      currentFlight: null,
      listQuery: {
        page: 1,
        limit: 10,
        search: '',
        status: ''
      },
      statusOptions: [
        { label: '计划', value: 'scheduled' },
        { label: '延误', value: 'delayed' },
        { label: '登机中', value: 'boarding' },
        { label: '已起飞', value: 'departed' },
        { label: '已到达', value: 'arrived' },
        { label: '取消', value: 'cancelled' }
      ]
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      
      const params = {
        page: this.listQuery.page,
        page_size: this.listQuery.limit
      }
      
      if (this.listQuery.status) {
        params.status = this.listQuery.status
      }
      
      if (this.listQuery.search) {
        getFlightList(params).then(response => {
          this.list = response.results || []
          this.total = response.count || 0
          this.listLoading = false
        }).catch(() => {
          this.listLoading = false
        })
      } else {
        getFlightList(params).then(response => {
          this.list = response.results || []
          this.total = response.count || 0
          this.listLoading = false
        }).catch(() => {
          this.listLoading = false
        })
      }
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleCreate() {
      this.$router.push({ name: 'AddFlight' })
    },
    handleUpdate(row) {
      this.$router.push({ name: 'EditFlight', params: { id: row.id }})
    },
    handleDetail(row) {
      this.$router.push({ name: 'FlightDetail', params: { id: row.id }})
    },
    handleDelete(row) {
      this.$confirm('确认删除该航班信息吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteFlight(row.id).then(() => {
          this.$message({
            type: 'success',
            message: '删除成功!'
          })
          this.getList()
        }).catch(error => {
          console.error(error)
          this.$message({
            type: 'error',
            message: '删除失败，请重试!'
          })
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    handleVoiceAnnounce(row) {
      this.currentFlight = row
      this.dialogVisible = true
      
      // 获取航班语音播报内容
      getFlightVoiceStatus(row.id).then(response => {
        this.voiceContent = response.voice_content
      }).catch(error => {
        console.error(error)
        this.voiceContent = `航班${row.flight_number}信息获取失败，请重试!`
      })
    },
    confirmAnnounce() {
      if (!this.voiceContent) {
        this.$message.warning('播报内容不能为空')
        return
      }
      
      // 创建播报记录
      createFlightAnnouncement({
        flight_number: this.currentFlight.flight_number,
        content: this.voiceContent
      }).then(() => {
        // 调用数字人组件播报
        this.$refs.digitalHuman.speak(this.voiceContent)
        
        this.$message({
          type: 'success',
          message: '播报成功!'
        })
      }).catch(error => {
        console.error(error)
        this.$message({
          type: 'error',
          message: '播报失败，请重试!'
        })
      })
    },
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return ''
      const date = new Date(dateTimeStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      
      return `${year}-${month}-${day} ${hours}:${minutes}`
    },
    getStatusType(status) {
      const statusMap = {
        scheduled: '',
        delayed: 'warning',
        boarding: 'success',
        departed: 'info',
        arrived: '',
        cancelled: 'danger'
      }
      return statusMap[status] || ''
    }
  }
}
</script>

<style lang="scss" scoped>
.filter-container {
  padding-bottom: 10px;
  .filter-item {
    margin-right: 10px;
  }
}

.digital-human-dialog {
  display: flex;
  flex-direction: column;
  align-items: center;
  
  .voice-content {
    width: 100%;
    margin-top: 20px;
    
    p {
      margin-bottom: 10px;
    }
  }
  
  .dialog-footer {
    margin-top: 20px;
    text-align: right;
    width: 100%;
  }
}
</style> 