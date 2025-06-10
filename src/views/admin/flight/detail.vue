<template>
  <div class="app-container">
    <div class="card-container">
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span>航班详情管理</span>
          <el-button style="float: right; margin-left: 10px;" type="primary" size="small" @click="handleEdit">编辑</el-button>
          <el-button style="float: right;" type="text" @click="goBack">返回列表</el-button>
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
                <el-descriptions-item label="创建时间">
                  {{ formatDateTime(flight.created_at) }}
                </el-descriptions-item>
                <el-descriptions-item label="更新时间">
                  {{ formatDateTime(flight.updated_at) }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
            
            <el-divider content-position="left">播报功能</el-divider>
            
            <div class="announce-section">
              <div class="digital-human-container">
                <digital-human ref="digitalHuman"></digital-human>
              </div>
              
              <div class="announce-controls">
                <el-form :model="announceForm" label-width="100px">
                  <el-form-item label="播报内容">
                    <el-input
                      type="textarea"
                      :rows="4"
                      v-model="announceForm.content"
                      placeholder="输入自定义播报内容或使用默认航班播报"
                    ></el-input>
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="announceDefault">默认播报</el-button>
                    <el-button type="success" @click="announceCustom">自定义播报</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </div>
            
            <el-divider content-position="left">历史播报记录</el-divider>
            
            <div class="history-section">
              <el-table
                v-loading="historyLoading"
                :data="announcementHistory"
                element-loading-text="加载中..."
                border
                style="width: 100%"
              >
                <el-table-column label="播报时间" align="center" width="180">
                  <template slot-scope="{row}">
                    <span>{{ formatDateTime(row.created_at) }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="播报内容" prop="content" align="left" show-overflow-tooltip></el-table-column>
                <el-table-column label="操作" align="center" width="100">
                  <template slot-scope="{row}">
                    <el-button type="text" @click="replayAnnouncement(row)">重播</el-button>
                  </template>
                </el-table-column>
              </el-table>
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
import { getFlightDetail, getFlightVoiceStatus, createFlightAnnouncement, getAnnouncementHistory } from '@/api/flight'
import DigitalHuman from '@/components/DigitalHuman'

export default {
  name: 'FlightDetail',
  components: {
    DigitalHuman
  },
  data() {
    return {
      loading: true,
      historyLoading: false,
      flightId: null,
      flight: null,
      announcementHistory: [],
      announceForm: {
        content: ''
      }
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
        this.fetchAnnouncementHistory()
        this.loading = false
      }).catch(error => {
        console.error('获取航班详情失败:', error)
        this.$message.error('获取航班详情失败，请重试')
        this.loading = false
      })
    },
    fetchAnnouncementHistory() {
      this.historyLoading = true
      getAnnouncementHistory({ flight: this.flightId }).then(response => {
        this.announcementHistory = response.results || []
        this.historyLoading = false
      }).catch(error => {
        console.error('获取播报历史失败:', error)
        this.historyLoading = false
      })
    },
    handleEdit() {
      this.$router.push({ name: 'EditFlight', params: { id: this.flightId }})
    },
    goBack() {
      this.$router.push({ name: 'AdminFlightManagement' })
    },
    announceDefault() {
      getFlightVoiceStatus(this.flightId).then(response => {
        this.announceForm.content = response.voice_content
        this.createAnnouncementRecord(response.voice_content)
      }).catch(error => {
        console.error('获取默认播报内容失败:', error)
        this.$message.error('获取默认播报内容失败，请重试')
      })
    },
    announceCustom() {
      if (!this.announceForm.content.trim()) {
        this.$message.warning('请输入播报内容')
        return
      }
      
      this.createAnnouncementRecord(this.announceForm.content)
    },
    createAnnouncementRecord(content) {
      createFlightAnnouncement({
        flight_number: this.flight.flight_number,
        content: content
      }).then(() => {
        // 调用数字人播报
        this.$refs.digitalHuman.speak(content)
        
        // 刷新历史记录
        this.fetchAnnouncementHistory()
        
        this.$message({
          type: 'success',
          message: '播报成功!'
        })
      }).catch(error => {
        console.error('创建播报记录失败:', error)
        this.$message.error('播报失败，请重试')
      })
    },
    replayAnnouncement(announcement) {
      this.$refs.digitalHuman.speak(announcement.content)
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
  max-width: 900px;
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

.announce-section {
  display: flex;
  margin-bottom: 30px;
  
  .digital-human-container {
    width: 40%;
    display: flex;
    justify-content: center;
  }
  
  .announce-controls {
    width: 60%;
    padding-left: 20px;
  }
}

.history-section {
  margin-bottom: 20px;
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

@media (max-width: 768px) {
  .announce-section {
    flex-direction: column;
    
    .digital-human-container,
    .announce-controls {
      width: 100%;
    }
    
    .announce-controls {
      padding-left: 0;
      margin-top: 20px;
    }
  }
}
</style>