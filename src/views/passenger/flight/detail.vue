<template>
  <div class="app-container">
    <div class="card-container">
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span>航班详情</span>
          <el-button style="float: right; padding: 3px 0" type="text" @click="goBack">返回列表</el-button>
        </div>
        
        <div v-loading="loading">
          <template v-if="flight">
            <div class="flight-header">
              <div class="flight-number">
                <h2>{{ flight.flight_number }}</h2>
                <el-tag :type="getStatusType(flight.status)">{{ flight.status_display }}</el-tag>
              </div>
              <div class="flight-airline">
                <span>{{ flight.airline }}</span>
              </div>
            </div>
            
            <div class="flight-route">
              <div class="departure">
                <div class="city">{{ flight.departure_city }}</div>
                <div class="airport">{{ flight.departure_airport }}</div>
                <div class="time">{{ formatDateTime(flight.scheduled_departure_time) }}</div>
                <div class="terminal" v-if="flight.terminal">{{ flight.terminal }}航站楼</div>
                <div class="gate" v-if="flight.gate">{{ flight.gate }}登机口</div>
              </div>
              
              <div class="route-line">
                <div class="line"></div>
                <i class="el-icon-plane"></i>
              </div>
              
              <div class="arrival">
                <div class="city">{{ flight.arrival_city }}</div>
                <div class="airport">{{ flight.arrival_airport }}</div>
                <div class="time">{{ formatDateTime(flight.scheduled_arrival_time) }}</div>
              </div>
            </div>
            
            <div class="flight-info">
              <el-descriptions title="航班信息" :column="2" border>
                <el-descriptions-item label="计划出发时间">
                  {{ formatDateTime(flight.scheduled_departure_time) }}
                </el-descriptions-item>
                <el-descriptions-item label="计划到达时间">
                  {{ formatDateTime(flight.scheduled_arrival_time) }}
                </el-descriptions-item>
                <el-descriptions-item label="实际出发时间">
                  {{ flight.actual_departure_time ? formatDateTime(flight.actual_departure_time) : '未起飞' }}
                </el-descriptions-item>
                <el-descriptions-item label="实际到达时间">
                  {{ flight.actual_arrival_time ? formatDateTime(flight.actual_arrival_time) : '未到达' }}
                </el-descriptions-item>
                <el-descriptions-item label="航班状态">
                  <el-tag :type="getStatusType(flight.status)">{{ flight.status_display }}</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>
            
            <div class="digital-human-container">
              <h3>数字人航班播报</h3>
              <div class="digital-human-wrapper">
                <digital-human ref="digitalHuman"></digital-human>
                <div class="action-buttons">
                  <el-button type="primary" @click="announceFlightInfo">航班播报</el-button>
                  <el-button type="success" @click="handleSelectFlight">选择航班</el-button>
                </div>
              </div>
            </div>
          </template>
          
          <div v-else class="no-data">
            <i class="el-icon-warning"></i>
            <p>未找到航班信息</p>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { getFlightDetail, getFlightVoiceStatus, createFlightAnnouncement, selectFlight, unselectFlight } from '@/api/flight'
import DigitalHuman from '@/components/DigitalHuman'

export default {
  name: 'PassengerFlightDetail',
  components: {
    DigitalHuman
  },
  data() {
    return {
      loading: true,
      flightId: null,
      flight: null
    }
  },
  created() {
    this.flightId = this.$route.params.id
    this.fetchFlightDetail()
  },
  mounted() {
    this.fetchFlightDetail()
    
    // 尝试加载数字人配置
    this.loadDigitalHumanConfig()
  },
  methods: {
    fetchFlightDetail() {
      this.loading = true
      getFlightDetail(this.flightId).then(response => {
        this.flight = response
        this.loading = false
      }).catch(error => {
        console.error('获取航班详情失败:', error)
        this.$message.error('获取航班详情失败，请重试')
        this.loading = false
      })
    },
    goBack() {
      this.$router.push({ name: 'PassengerFlightQuery' })
    },
    announceFlightInfo() {
      getFlightVoiceStatus(this.flightId).then(response => {
        const voiceContent = response.voice_content
        
        // 创建播报记录
        createFlightAnnouncement({
          flight_number: this.flight.flight_number,
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
    handleSelectFlight() {
      this.$confirm('确定要选择此航班吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }).then(() => {
        selectFlight(this.flightId).then(response => {
          this.$message({
            type: 'success',
            message: response.message || '航班选择成功'
          })
          
          // 数字人播报选择成功信息
          this.$refs.digitalHuman.speak(`您已成功选择 ${this.flight.flight_number} 航班，从 ${this.flight.departure_city} 飞往 ${this.flight.arrival_city}`)
        }).catch(error => {
          console.error('选择航班失败:', error)
          this.$message.error('选择航班失败，请重试')
        })
      }).catch(() => {
        // 取消选择
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
    },
    // 加载数字人配置
    loadDigitalHumanConfig() {
      if (this.$refs.digitalHuman) {
        // 组件内部已实现自动加载配置的功能
        console.log('数字人组件已加载')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

.card-container {
  max-width: 800px;
  margin: 0 auto;
}

.flight-header {
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .flight-number {
    display: flex;
    align-items: center;
    
    h2 {
      margin: 0 10px 0 0;
    }
  }
  
  .flight-airline {
    font-size: 16px;
    color: #606266;
  }
}

.flight-route {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  
  .departure, .arrival {
    flex: 1;
    
    .city {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 5px;
    }
    
    .airport {
      font-size: 14px;
      color: #606266;
      margin-bottom: 5px;
    }
    
    .time {
      font-size: 16px;
      margin-bottom: 5px;
    }
    
    .terminal, .gate {
      font-size: 14px;
      color: #606266;
    }
  }
  
  .route-line {
    position: relative;
    width: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .line {
      height: 2px;
      background-color: #409EFF;
      width: 100%;
    }
    
    i {
      position: absolute;
      font-size: 24px;
      color: #409EFF;
    }
  }
  
  .arrival {
    text-align: right;
  }
}

.flight-info {
  margin-bottom: 30px;
}

.digital-human-container {
  h3 {
    margin-top: 0;
    margin-bottom: 20px;
  }
  
  .digital-human-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .el-button {
      margin-top: 15px;
    }
  }
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.no-data {
  text-align: center;
  padding: 40px 0;
  
  i {
    font-size: 48px;
    color: #909399;
    margin-bottom: 10px;
  }
  
  p {
    color: #909399;
  }
}
</style> 