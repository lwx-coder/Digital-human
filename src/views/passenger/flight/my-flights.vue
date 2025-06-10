<template>
  <div class="app-container">
    <div class="header-container">
      <el-card class="header-card">
        <div class="page-title">
          <h2>我的航班</h2>
          <div class="actions">
            <el-button type="primary" @click="goToFlightQuery">查询更多航班</el-button>
          </div>
        </div>
        
        <div class="digital-human-container">
          <digital-human ref="digitalHuman"></digital-human>
          <el-button type="primary" size="small" @click="speakMyFlights">播报我的航班</el-button>
        </div>
      </el-card>
    </div>
    
    <el-card v-loading="loading" class="flights-card">
      <div v-if="flights.length > 0">
        <div class="flight-cards">
          <el-card 
            v-for="flight in flights" 
            :key="flight.id" 
            class="flight-card"
            :class="{ 'is-delayed': flight.status === 'delayed', 'is-cancelled': flight.status === 'cancelled' }"
          >
            <div class="flight-header">
              <div class="flight-number">{{ flight.flight_number }}</div>
              <el-tag :type="getStatusType(flight.status)">{{ flight.status_display }}</el-tag>
            </div>
            
            <div class="flight-route">
              <div class="route-item">
                <div class="city">{{ flight.departure_city }}</div>
                <div class="time">{{ formatDateTime(flight.scheduled_departure_time) }}</div>
              </div>
              <div class="route-arrow">
                <i class="el-icon-arrow-right"></i>
              </div>
              <div class="route-item">
                <div class="city">{{ flight.arrival_city }}</div>
                <div class="time">{{ formatDateTime(flight.scheduled_arrival_time) }}</div>
              </div>
            </div>
            
            <div class="flight-airline">{{ flight.airline }}</div>
            
            <div class="flight-actions">
              <el-button type="text" @click="viewDetail(flight)">查看详情</el-button>
              <el-button type="text" @click="announceFlightInfo(flight)">播报航班</el-button>
              <el-button type="text" style="color: #F56C6C" @click="unselectFlight(flight)">取消选择</el-button>
            </div>
          </el-card>
        </div>
        
        <div class="pagination-container">
          <el-pagination
            background
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page.sync="currentPage"
            :page-sizes="[6, 12, 24, 36]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total">
          </el-pagination>
        </div>
      </div>
      
      <div v-else class="no-flights">
        <i class="el-icon-warning-outline"></i>
        <h3>您还没有选择任何航班</h3>
        <p>请前往航班查询页面选择您的航班</p>
        <el-button type="primary" @click="goToFlightQuery">查询航班</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { getMyFlights, getFlightVoiceStatus, createFlightAnnouncement, unselectFlight as apiUnselectFlight } from '@/api/flight'
import DigitalHuman from '@/components/DigitalHuman'

export default {
  name: 'MyFlights',
  components: {
    DigitalHuman
  },
  data() {
    return {
      loading: false,
      flights: [],
      currentPage: 1,
      pageSize: 6,
      total: 0
    }
  },
  created() {
    this.fetchMyFlights()
  },
  methods: {
    fetchMyFlights() {
      this.loading = true
      getMyFlights({
        page: this.currentPage,
        page_size: this.pageSize
      }).then(response => {
        this.flights = response.results || []
        this.total = response.count || 0
        this.loading = false
      }).catch(error => {
        console.error('获取我的航班失败:', error)
        this.$message.error('获取我的航班失败，请重试')
        this.loading = false
      })
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.fetchMyFlights()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchMyFlights()
    },
    viewDetail(flight) {
      this.$router.push({ name: 'PassengerFlightDetail', params: { id: flight.id }})
    },
    goToFlightQuery() {
      this.$router.push({ name: 'PassengerFlightQuery' })
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
    unselectFlight(flight) {
      this.$confirm(`确定要取消选择航班 ${flight.flight_number} 吗?`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        apiUnselectFlight(flight.id).then(response => {
          this.$message({
            type: 'success',
            message: response.message || '取消选择成功'
          })
          
          // 刷新航班列表
          this.fetchMyFlights()
          
          // 数字人播报
          this.$refs.digitalHuman.speak(`您已取消选择 ${flight.flight_number} 航班`)
        }).catch(error => {
          console.error('取消选择航班失败:', error)
          this.$message.error('取消选择失败，请重试')
        })
      }).catch(() => {
        // 用户取消操作
      })
    },
    speakMyFlights() {
      if (this.flights.length === 0) {
        this.$refs.digitalHuman.speak('您当前没有选择任何航班，请前往航班查询页面选择航班')
        return
      }
      
      let message = `您当前有${this.flights.length}个选择的航班。`
      
      this.flights.forEach((flight, index) => {
        message += `航班${index + 1}：${flight.flight_number}，从${flight.departure_city}飞往${flight.arrival_city}，`
        
        if (flight.status === 'delayed') {
          message += '该航班已延误。'
        } else if (flight.status === 'cancelled') {
          message += '该航班已取消。'
        } else if (flight.status === 'boarding') {
          message += '该航班正在登机。'
        } else if (flight.status === 'departed') {
          message += '该航班已起飞。'
        } else if (flight.status === 'arrived') {
          message += '该航班已到达。'
        } else {
          message += '该航班按计划进行。'
        }
      })
      
      this.$refs.digitalHuman.speak(message)
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

.header-container {
  margin-bottom: 20px;
  
  .header-card {
    .page-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      
      h2 {
        margin: 0;
      }
    }
    
    .digital-human-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-top: 20px;
      
      .el-button {
        margin-top: 10px;
      }
    }
  }
}

.flights-card {
  .flight-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
    
    .flight-card {
      position: relative;
      transition: all 0.3s;
      
      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
      }
      
      &.is-delayed {
        border-left: 4px solid #E6A23C;
      }
      
      &.is-cancelled {
        border-left: 4px solid #F56C6C;
      }
      
      .flight-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        
        .flight-number {
          font-size: 18px;
          font-weight: bold;
        }
      }
      
      .flight-route {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        
        .route-item {
          flex: 1;
          
          .city {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 5px;
          }
          
          .time {
            font-size: 14px;
            color: #606266;
          }
        }
        
        .route-arrow {
          padding: 0 10px;
          color: #409EFF;
          font-size: 20px;
        }
      }
      
      .flight-airline {
        margin-bottom: 15px;
        color: #606266;
      }
      
      .flight-actions {
        display: flex;
        justify-content: space-between;
        border-top: 1px solid #EBEEF5;
        padding-top: 10px;
      }
    }
  }
  
  .pagination-container {
    text-align: center;
  }
  
  .no-flights {
    text-align: center;
    padding: 40px 0;
    
    i {
      font-size: 60px;
      color: #909399;
      margin-bottom: 20px;
    }
    
    h3 {
      margin-bottom: 10px;
      font-weight: normal;
    }
    
    p {
      color: #606266;
      margin-bottom: 20px;
    }
  }
}
</style> 