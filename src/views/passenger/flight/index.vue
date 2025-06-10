<template>
  <div class="app-container">
    <div class="search-container">
      <el-card class="search-card">
        <h3 class="card-title">航班查询</h3>
        <div class="search-form">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-input
                v-model="searchQuery"
                placeholder="请输入航班号/城市/机场"
                prefix-icon="el-icon-search"
                @keyup.enter.native="handleSearch"
              ></el-input>
            </el-col>
            <el-col :span="12">
              <el-button type="primary" @click="handleSearch">查询</el-button>
              <el-button @click="resetSearch">重置</el-button>
              <el-button type="success" @click="goToMyFlights">我的航班</el-button>
            </el-col>
          </el-row>
        </div>
      </el-card>
    </div>
    
    <div class="digital-human-container">
      <el-card class="digital-human-card">
        <div class="digital-human-wrapper">
          <digital-human ref="digitalHuman"></digital-human>
          <el-button type="primary" @click="speakWelcomeMessage" size="small">
            播报欢迎信息
          </el-button>
        </div>
      </el-card>
    </div>
    
    <div class="flight-list-container">
      <el-card class="flight-list-card">
        <div slot="header" class="clearfix">
          <span>航班列表</span>
        </div>
        
        <el-table
          v-loading="loading"
          :data="flightList"
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
          <el-table-column label="出发/到达" align="center" min-width="150">
            <template slot-scope="{row}">
              <span>{{ row.departure_city }} → {{ row.arrival_city }}</span>
            </template>
          </el-table-column>
          <el-table-column label="计划出发时间" align="center" min-width="150">
            <template slot-scope="{row}">
              <span>{{ formatDateTime(row.scheduled_departure_time) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" align="center" min-width="100">
            <template slot-scope="{row}">
              <el-tag :type="getStatusType(row.status)">{{ row.status_display }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" min-width="200">
            <template slot-scope="{row}">
              <el-button type="primary" size="mini" @click="viewDetail(row)">
                详情
              </el-button>
              <el-button type="success" size="mini" @click="announceFlightInfo(row)">
                播报
              </el-button>
              <el-button type="warning" size="mini" @click="selectFlight(row)">
                选择
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
            :page-sizes="[5, 10, 20, 50]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total">
          </el-pagination>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { getFlightList, searchFlights, getFlightVoiceStatus, createFlightAnnouncement, selectFlight as apiSelectFlight } from '@/api/flight'
import DigitalHuman from '@/components/DigitalHuman'

export default {
  name: 'PassengerFlightQuery',
  components: {
    DigitalHuman
  },
  data() {
    return {
      searchQuery: '',
      loading: false,
      flightList: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      welcomeMessages: [
        '欢迎使用智能机场服务系统，我是您的数字助手，有什么可以帮助您的吗？',
        '您好，我是机场数字服务助手，今天我可以为您提供航班信息查询和播报服务。',
        '欢迎来到机场智能服务系统，您可以在此查询航班信息，我将为您提供及时的语音播报服务。'
      ]
    }
  },
  created() {
    this.fetchFlights()
  },
  methods: {
    fetchFlights() {
      this.loading = true
      
      const params = {
        page: this.currentPage,
        page_size: this.pageSize
      }
      
      getFlightList(params).then(response => {
        this.flightList = response.results || []
        this.total = response.count || 0
        this.loading = false
      }).catch(error => {
        console.error('获取航班列表失败:', error)
        this.$message.error('获取航班信息失败，请重试')
        this.loading = false
      })
    },
    handleSearch() {
      if (!this.searchQuery.trim()) {
        this.fetchFlights()
        return
      }
      
      this.loading = true
      searchFlights(this.searchQuery).then(response => {
        this.flightList = response.results || []
        this.total = response.count || 0
        this.loading = false
      }).catch(error => {
        console.error('搜索航班失败:', error)
        this.$message.error('搜索航班失败，请重试')
        this.loading = false
      })
    },
    resetSearch() {
      this.searchQuery = ''
      this.currentPage = 1
      this.fetchFlights()
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.fetchFlights()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchFlights()
    },
    viewDetail(row) {
      this.$router.push({ name: 'PassengerFlightDetail', params: { id: row.id }})
    },
    announceFlightInfo(flight) {
      getFlightVoiceStatus(flight.id).then(response => {
        const voiceContent = response.voice_content
        
        // 创建播报记录
        createFlightAnnouncement({
          flight_number: flight.flight_number,
          content: voiceContent
        }).then(() => {
          // 调用数字人播报
          this.$refs.digitalHuman.speak(voiceContent)
        }).catch(error => {
          console.error('创建播报记录失败:', error)
        })
      }).catch(error => {
        console.error('获取航班播报信息失败:', error)
        this.$message.error('获取航班播报信息失败，请重试')
      })
    },
    speakWelcomeMessage() {
      const randomIndex = Math.floor(Math.random() * this.welcomeMessages.length)
      const message = this.welcomeMessages[randomIndex]
      this.$refs.digitalHuman.speak(message)
    },
    selectFlight(row) {
      apiSelectFlight(row.id).then(response => {
        this.$message({
          message: response.message || '航班选择成功',
          type: 'success'
        })
        // 数字人播报选择成功信息
        this.$refs.digitalHuman.speak(`您已成功选择 ${row.flight_number} 航班，从 ${row.departure_city} 飞往 ${row.arrival_city}`)
      }).catch(error => {
        console.error('选择航班失败:', error)
        this.$message.error('选择航班失败，请重试')
      })
    },
    goToMyFlights() {
      this.$router.push({ name: 'MyFlights' })
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
.app-container {
  padding: 20px;
}

.search-container {
  margin-bottom: 20px;
  
  .search-card {
    .card-title {
      margin-top: 0;
      margin-bottom: 20px;
      color: #303133;
      font-size: 18px;
    }
    
    .search-form {
      margin-bottom: 10px;
    }
  }
}

.digital-human-container {
  margin-bottom: 20px;
  
  .digital-human-card {
    .digital-human-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      
      .el-button {
        margin-top: 15px;
      }
    }
  }
}

.flight-list-container {
  .flight-list-card {
    .pagination-container {
      margin-top: 20px;
      text-align: center;
    }
  }
}
</style> 