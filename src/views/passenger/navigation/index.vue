<template>
  <div class="navigation-container">
    <el-card class="map-card">
      <div slot="header" class="clearfix">
        <span>机场导航</span>
        <div class="operation-buttons">
          <el-select v-model="currentFloor" placeholder="选择楼层" size="small" @change="changeFloor">
            <el-option v-for="floor in floors" :key="floor" :label="`${floor}楼`" :value="floor" />
          </el-select>
          <el-select v-model="locationType" placeholder="位置类型" size="small" @change="filterLocations">
            <el-option v-for="type in locationTypes" :key="type.value" :label="type.label" :value="type.value" />
          </el-select>
        </div>
      </div>
      
      <div class="map-container" ref="mapContainer">
        <!-- 简化版地图，实际项目中可能使用更复杂的地图组件 -->
        <div class="map-area" :style="{ height: mapHeight + 'px' }">
          <!-- 当前位置标记 -->
          <div v-if="currentPosition.x && currentPosition.y" 
               class="current-position" 
               :style="{
                 left: `${currentPosition.x}px`,
                 top: `${currentPosition.y}px`
               }">
            <i class="el-icon-location"></i>
          </div>
          
          <!-- 目标位置标记 -->
          <div v-if="destination.x && destination.y" 
               class="destination-position" 
               :style="{
                 left: `${destination.x}px`,
                 top: `${destination.y}px`
               }">
            <i class="el-icon-place"></i>
          </div>
          
          <!-- 位置点 -->
          <div v-for="location in filteredLocations" 
               :key="location.id" 
               class="location-point"
               :class="{ 'active': isLocationActive(location.id) }"
               :style="{
                 left: `${location.x_coordinate}px`,
                 top: `${location.y_coordinate}px`,
                 backgroundColor: getLocationColor(location.type)
               }"
               @click="selectLocation(location)">
            <el-tooltip :content="location.name" placement="top" :open-delay="300">
              <div class="location-icon">
                <i :class="getLocationIcon(location.type)"></i>
              </div>
            </el-tooltip>
          </div>
          
          <!-- 导航路径 -->
          <svg v-if="showPath" class="path-overlay">
            <line :x1="currentPosition.x" 
                  :y1="currentPosition.y" 
                  :x2="destination.x" 
                  :y2="destination.y" 
                  stroke="#409EFF" 
                  stroke-width="3" 
                  stroke-dasharray="5,5" />
          </svg>
        </div>
      </div>
    </el-card>
    
    <el-row :gutter="20" class="info-row">
      <el-col :span="12">
        <el-card class="location-card">
          <div slot="header">
            <span>当前位置</span>
          </div>
          <div v-if="selectedCurrentLocation">
            <h3>{{ selectedCurrentLocation.name }}</h3>
            <p>{{ selectedCurrentLocation.type_display }}</p>
            <p v-if="selectedCurrentLocation.description">{{ selectedCurrentLocation.description }}</p>
            <p>楼层: {{ selectedCurrentLocation.floor }}F</p>
          </div>
          <div v-else class="empty-tip">
            <i class="el-icon-position"></i>
            <p>请在地图上选择您的当前位置</p>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="destination-card">
          <div slot="header">
            <span>目的地</span>
          </div>
          <div v-if="selectedDestination">
            <h3>{{ selectedDestination.name }}</h3>
            <p>{{ selectedDestination.type_display }}</p>
            <p v-if="selectedDestination.description">{{ selectedDestination.description }}</p>
            <p>楼层: {{ selectedDestination.floor }}F</p>
          </div>
          <div v-else class="empty-tip">
            <i class="el-icon-map-location"></i>
            <p>请在地图上选择您想去的目的地</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card class="navigation-card" v-if="selectedCurrentLocation && selectedDestination">
      <div slot="header">
        <span>导航信息</span>
      </div>
      <div class="navigation-info">
        <div class="route-info">
          <p class="route-title">
            <i class="el-icon-location"></i> 
            {{ selectedCurrentLocation.name }} 
            <i class="el-icon-right"></i> 
            <i class="el-icon-place"></i> 
            {{ selectedDestination.name }}
          </p>
          <template v-if="navigationRecord">
            <p>距离: {{ navigationRecord.distance }} 米</p>
            <p>预计时间: {{ navigationRecord.estimated_time }} 分钟</p>
          </template>
        </div>
        
        <div class="button-group">
          <el-button type="primary" @click="startNavigation" :disabled="isNavigating">
            开始导航
          </el-button>
          <el-button @click="clearNavigation" type="info" plain>
            清除
          </el-button>
        </div>
      </div>
      
      <div v-if="voiceMessage" class="voice-message">
        <i class="el-icon-microphone"></i>
        <div class="voice-text">{{ voiceMessage }}</div>
      </div>
      
      <div class="voice-buttons" v-if="isNavigating">
        <el-tooltip content="获取导航指南" placement="top">
          <el-button type="primary" icon="el-icon-guide" circle @click="getVoiceDirection"></el-button>
        </el-tooltip>
        <el-tooltip content="查询到达时间" placement="top">
          <el-button type="success" icon="el-icon-time" circle @click="getArrivalTime"></el-button>
        </el-tooltip>
        <el-tooltip content="查询时间安排" placement="top">
          <el-button type="warning" icon="el-icon-date" circle @click="getSchedule"></el-button>
        </el-tooltip>
        <el-tooltip content="查询附近设施" placement="top">
          <el-button type="info" icon="el-icon-discover" circle @click="getNearbyFacilities"></el-button>
        </el-tooltip>
        <el-tooltip content="完成导航" placement="top">
          <el-button type="danger" icon="el-icon-check" circle @click="completeCurrentNavigation"></el-button>
        </el-tooltip>
      </div>
    </el-card>
    
    <el-card class="schedules-card" v-if="isNavigating">
      <div slot="header">
        <span>今日安排</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="goToSchedule">
          查看全部
        </el-button>
      </div>
      <div v-if="todaySchedules.length > 0" class="schedule-list">
        <div v-for="(schedule, index) in todaySchedules" :key="index" class="schedule-item">
          <div class="time">{{ formatTime(schedule.start_time) }}</div>
          <div class="event-info">
            <div class="event-name">{{ schedule.event_name }}</div>
            <div class="event-location" v-if="schedule.location_detail">
              {{ schedule.location_detail.name }}
            </div>
          </div>
          <div class="event-status">
            <el-tag v-if="schedule.is_completed" type="success" size="mini">已完成</el-tag>
            <el-tag v-else type="info" size="mini">未完成</el-tag>
          </div>
        </div>
      </div>
      <div v-else class="empty-schedule">
        <i class="el-icon-date"></i>
        <p>今日暂无安排</p>
      </div>
    </el-card>
  </div>
</template>

<script>
import { 
  getLocationList, getLocationsByType, 
  createNavigation, getVoiceNavigation, completeNavigation,
  getTodaySchedules
} from '@/api/navigation'
import { parseTime } from '@/utils'

export default {
  name: 'PassengerNavigation',
  data() {
    return {
      // 地图相关
      mapHeight: 400,
      currentFloor: 1,
      floors: [1, 2, 3],
      locationType: '',
      locationTypes: [
        { value: '', label: '全部' },
        { value: 'gate', label: '登机口' },
        { value: 'shop', label: '商店' },
        { value: 'restaurant', label: '餐厅' },
        { value: 'toilet', label: '卫生间' },
        { value: 'security', label: '安检口' },
        { value: 'check_in', label: '值机柜台' },
        { value: 'luggage', label: '行李提取处' },
        { value: 'exit', label: '出口' },
        { value: 'entrance', label: '入口' },
        { value: 'lounge', label: '休息室' },
        { value: 'other', label: '其他' }
      ],
      
      // 位置数据
      allLocations: [],
      filteredLocations: [],
      selectedCurrentLocationId: null,
      selectedDestinationId: null,
      currentPosition: {},
      destination: {},
      showPath: false,
      
      // 导航相关
      navigationRecord: null,
      isNavigating: false,
      voiceMessage: '',
      
      // 日程相关
      todaySchedules: []
    }
  },
  computed: {
    selectedCurrentLocation() {
      return this.allLocations.find(loc => loc.id === this.selectedCurrentLocationId) || null
    },
    selectedDestination() {
      return this.allLocations.find(loc => loc.id === this.selectedDestinationId) || null
    }
  },
  created() {
    this.fetchLocations()
    this.fetchTodaySchedules()
    
    // 检查URL中是否有目的地参数
    const destinationId = this.$route.query.destination
    if (destinationId) {
      // 设置延时，等待位置数据加载完成
      setTimeout(() => {
        this.handleDestinationFromUrl(destinationId)
      }, 1000) // 增加等待时间确保数据加载完成
    }
  },
  mounted() {
    this.adjustMapHeight()
    window.addEventListener('resize', this.adjustMapHeight)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.adjustMapHeight)
  },
  methods: {
    // 格式化时间
    formatTime(time) {
      return parseTime(time, '{h}:{i}')
    },
    
    // 调整地图高度
    adjustMapHeight() {
      if (this.$refs.mapContainer) {
        const containerWidth = this.$refs.mapContainer.clientWidth
        this.mapHeight = containerWidth * 0.6 // 长宽比例可根据需要调整
      }
    },
    
    // 获取位置数据
    fetchLocations() {
      console.log('开始获取位置数据')
      getLocationList().then(response => {
        // 调试信息
        console.log('获取到位置数据响应:', response)
        
        // 确保response是数组
        this.allLocations = Array.isArray(response) ? response : []
        if (this.allLocations.length === 0) {
          console.warn('未获取到位置数据或数据格式不正确')
          console.log('原始响应:', response)
          this.$message.warning('未获取到位置数据，请检查数据库中是否有数据')
        } else {
          console.log(`成功加载${this.allLocations.length}个位置点`)
          // 立即过滤位置
          this.filterLocations()
        }
      }).catch(error => {
        console.error('获取位置列表失败:', error)
        this.$message.error('获取位置列表失败')
        // 确保在出错时也初始化为空数组
        this.allLocations = []
      })
    },
    
    // 获取今日安排
    fetchTodaySchedules() {
      console.log('开始获取今日安排')
      getTodaySchedules().then(response => {
        console.log('获取到今日安排响应:', response)
        // 确保response是数组
        this.todaySchedules = Array.isArray(response) ? response : []
        if (this.todaySchedules.length === 0) {
          console.log('今日没有安排或未获取到数据')
        } else {
          console.log(`成功加载${this.todaySchedules.length}个今日安排`)
        }
      }).catch(error => {
        console.error('获取今日安排失败:', error)
        this.$message.error('获取今日安排失败')
        // 确保在出错时也初始化为空数组
        this.todaySchedules = []
      })
    },
    
    // 筛选位置
    filterLocations() {
      console.log('开始筛选位置，楼层:', this.currentFloor, '类型:', this.locationType)
      console.log('筛选前的位置数据:', this.allLocations)
      
      if (!Array.isArray(this.allLocations) || this.allLocations.length === 0) {
        console.warn('没有位置数据可供筛选')
        this.filteredLocations = []
        return
      }
      
      // 先按楼层筛选
      let filtered = this.allLocations.filter(loc => loc.floor === this.currentFloor)
      
      // 如果指定了类型，进一步筛选
      if (this.locationType) {
        filtered = filtered.filter(loc => loc.type === this.locationType)
      }
      
      console.log(`筛选结果: ${filtered.length}个位置`)
      this.filteredLocations = filtered
    },
    
    // 切换楼层
    changeFloor() {
      this.filterLocations()
      this.clearNavigation()
    },
    
    // 选择位置
    selectLocation(location) {
      console.log('选择位置:', location.name, location.id)
      
      // 如果已经有当前位置，但没有目的地，则设置为目的地
      if (this.selectedCurrentLocationId && !this.selectedDestinationId) {
        this.selectedDestinationId = location.id
        this.destination = {
          x: location.x_coordinate,
          y: location.y_coordinate
        }
        this.showPath = true
        console.log('设置为目的地:', location.name)
        
        // 创建导航记录
        this.createNavigationRecord()
      } 
      // 如果已经有当前位置和目的地，重新设置为目的地
      else if (this.selectedCurrentLocationId && this.selectedDestinationId) {
        // 如果点击的是当前位置，什么都不做
        if (location.id === this.selectedCurrentLocationId) {
          return
        }
        
        this.selectedDestinationId = location.id
        this.destination = {
          x: location.x_coordinate,
          y: location.y_coordinate
        }
        console.log('更新目的地:', location.name)
        
        // 创建新的导航记录
        this.createNavigationRecord()
      }
      // 否则设置为当前位置
      else {
        this.selectedCurrentLocationId = location.id
        this.selectedDestinationId = null
        this.currentPosition = {
          x: location.x_coordinate,
          y: location.y_coordinate
        }
        this.destination = {}
        this.showPath = false
        this.navigationRecord = null
        console.log('设置为起点:', location.name)
      }
    },
    
    // 判断位置是否被选中
    isLocationActive(locationId) {
      return locationId === this.selectedCurrentLocationId || 
             locationId === this.selectedDestinationId
    },
    
    // 根据位置类型获取不同颜色
    getLocationColor(type) {
      const colorMap = {
        gate: '#409EFF',
        shop: '#67C23A',
        restaurant: '#E6A23C',
        toilet: '#F56C6C',
        security: '#909399',
        check_in: '#86B0D6',
        luggage: '#C78EB5',
        exit: '#71CC98',
        entrance: '#5180CB',
        lounge: '#E08D45',
        other: '#8E8E8E'
      }
      return colorMap[type] || '#8E8E8E'
    },
    
    // 根据位置类型获取图标
    getLocationIcon(type) {
      const iconMap = {
        gate: 'el-icon-s-cooperation',
        shop: 'el-icon-shopping-cart-2',
        restaurant: 'el-icon-dish',
        toilet: 'el-icon-toilet-paper',
        security: 'el-icon-s-check',
        check_in: 'el-icon-s-claim',
        luggage: 'el-icon-suitcase',
        exit: 'el-icon-switch-button',
        entrance: 'el-icon-rank',
        lounge: 'el-icon-s-home',
        other: 'el-icon-location'
      }
      return iconMap[type] || 'el-icon-location'
    },
    
    // 创建导航记录
    createNavigationRecord() {
      if (!this.selectedCurrentLocationId || !this.selectedDestinationId) {
        console.warn('起点或终点未设置，无法创建导航记录')
        return
      }
      
      console.log('创建导航记录: 从', this.selectedCurrentLocationId, '到', this.selectedDestinationId)
      
      const data = {
        current_location_id: this.selectedCurrentLocationId,
        destination_id: this.selectedDestinationId
      }
      
      createNavigation(data).then(response => {
        console.log('导航记录创建成功:', response)
        this.navigationRecord = response
        this.$message.success('导航路线已生成')
      }).catch(error => {
        console.error('创建导航失败:', error)
        this.$message.error('创建导航失败')
      })
    },
    
    // 开始导航
    startNavigation() {
      if (!this.navigationRecord) {
        this.$message.warning('请先选择起点和终点')
        return
      }
      
      this.isNavigating = true
      this.getVoiceDirection()
    },
    
    // 清除导航
    clearNavigation() {
      this.selectedCurrentLocationId = null
      this.selectedDestinationId = null
      this.currentPosition = {}
      this.destination = {}
      this.showPath = false
      this.navigationRecord = null
      this.isNavigating = false
      this.voiceMessage = ''
    },
    
    // 获取语音导航指令
    getVoiceDirection() {
      if (!this.navigationRecord) return
      
      const data = {
        navigation_id: this.navigationRecord.id,
        query_type: 'direction'
      }
      
      getVoiceNavigation(data).then(response => {
        this.voiceMessage = response.voice_text
        this.speakText(this.voiceMessage)
      }).catch(error => {
        console.error('获取导航指令失败:', error)
        this.$message.error('获取导航指令失败')
      })
    },
    
    // 获取到达时间
    getArrivalTime() {
      if (!this.navigationRecord) return
      
      const data = {
        navigation_id: this.navigationRecord.id,
        query_type: 'time_to_destination'
      }
      
      getVoiceNavigation(data).then(response => {
        this.voiceMessage = response.voice_text
        this.speakText(this.voiceMessage)
      }).catch(error => {
        console.error('获取到达时间失败:', error)
        this.$message.error('获取到达时间失败')
      })
    },
    
    // 获取时间安排
    getSchedule() {
      if (!this.navigationRecord) return
      
      const data = {
        navigation_id: this.navigationRecord.id,
        query_type: 'schedule'
      }
      
      getVoiceNavigation(data).then(response => {
        this.voiceMessage = response.voice_text
        this.speakText(this.voiceMessage)
      }).catch(error => {
        console.error('获取时间安排失败:', error)
        this.$message.error('获取时间安排失败')
      })
    },
    
    // 获取附近设施
    getNearbyFacilities() {
      if (!this.navigationRecord) return
      
      const data = {
        navigation_id: this.navigationRecord.id,
        query_type: 'nearby'
      }
      
      getVoiceNavigation(data).then(response => {
        this.voiceMessage = response.voice_text
        this.speakText(this.voiceMessage)
      }).catch(error => {
        console.error('获取附近设施失败:', error)
        this.$message.error('获取附近设施失败')
      })
    },
    
    // 标记导航完成
    completeCurrentNavigation() {
      if (!this.navigationRecord) return
      
      completeNavigation(this.navigationRecord.id).then(() => {
        this.$message.success('导航已完成')
        this.isNavigating = false
        this.voiceMessage = '您已到达目的地。'
        this.speakText(this.voiceMessage)
      }).catch(error => {
        console.error('完成导航失败:', error)
        this.$message.error('完成导航失败')
      })
    },
    
    // 跳转到时间安排页面
    goToSchedule() {
      this.$router.push('/passenger-navigation/schedule')
    },
    
    // 文本语音播报
    speakText(text) {
      // 使用浏览器的语音合成API
      if ('speechSynthesis' in window) {
        const speech = new SpeechSynthesisUtterance()
        speech.text = text
        speech.lang = 'zh-CN'
        window.speechSynthesis.speak(speech)
      } else {
        console.warn('浏览器不支持语音合成')
      }
    },
    
    // 处理从URL传递的目的地ID
    handleDestinationFromUrl(destinationId) {
      console.log('处理URL传递的目的地ID:', destinationId)
      console.log('当前位置数据状态:', this.allLocations.length, '个位置')
      
      if (!Array.isArray(this.allLocations) || this.allLocations.length === 0) {
        console.warn('位置数据尚未加载，无法处理目的地')
        // 延迟再次尝试
        setTimeout(() => this.handleDestinationFromUrl(destinationId), 1000)
        return
      }
      
      const destId = parseInt(destinationId)
      if (!isNaN(destId)) {
        const destination = this.allLocations.find(loc => loc.id === destId)
        if (destination) {
          console.log('找到目的地:', destination.name)
          // 自动选择一个合适的起点（这里简单地选择第一个位置）
          const startLocation = this.allLocations.find(loc => loc.id !== destId && loc.floor === destination.floor)
          
          if (startLocation) {
            console.log('选择起点:', startLocation.name)
            // 先选择起点
            this.selectLocation(startLocation)
            // 再选择终点
            setTimeout(() => {
              this.selectLocation(destination)
            }, 100)
            
            // 自动跳转到目的地所在楼层
            this.currentFloor = destination.floor
            this.filterLocations()
          } else {
            console.warn('未找到合适的起点')
            this.$message.warning('未找到合适的起点位置')
          }
        } else {
          console.warn('未找到ID为', destId, '的目的地')
          this.$message.warning(`未找到ID为${destId}的目的地`)
        }
      }
    }
  }
}
</script>

<style scoped>
.navigation-container {
  padding: 20px;
}

.map-card {
  margin-bottom: 20px;
}

.operation-buttons {
  float: right;
}

.operation-buttons .el-select {
  margin-left: 10px;
}

.map-container {
  width: 100%;
  overflow: hidden;
  position: relative;
}

.map-area {
  background-color: #f5f7fa;
  position: relative;
  min-height: 400px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.location-point {
  position: absolute;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  text-align: center;
  line-height: 30px;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 1;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.location-point.active {
  border: 3px solid #ff4949;
  z-index: 2;
}

.location-icon {
  color: white;
  font-size: 16px;
}

.current-position {
  position: absolute;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #409EFF;
  color: white;
  text-align: center;
  line-height: 40px;
  transform: translate(-50%, -50%);
  z-index: 3;
  animation: pulse 1.5s infinite;
  box-shadow: 0 0 0 rgba(64, 158, 255, 0.4);
}

.destination-position {
  position: absolute;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #67C23A;
  color: white;
  text-align: center;
  line-height: 40px;
  transform: translate(-50%, -50%);
  z-index: 3;
}

.current-position i, .destination-position i {
  font-size: 24px;
}

.path-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.info-row {
  margin-bottom: 20px;
}

.location-card, .destination-card {
  height: 200px;
  overflow: auto;
}

.empty-tip {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100px;
  color: #909399;
}

.empty-tip i {
  font-size: 32px;
  margin-bottom: 10px;
}

.navigation-card {
  margin-bottom: 20px;
}

.navigation-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.route-info {
  flex: 1;
}

.route-title {
  font-size: 16px;
  margin-bottom: 10px;
}

.voice-message {
  background-color: #f0f9eb;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  display: flex;
  align-items: flex-start;
}

.voice-message i {
  font-size: 20px;
  color: #67C23A;
  margin-right: 10px;
  margin-top: 2px;
}

.voice-text {
  flex: 1;
  line-height: 1.5;
}

.voice-buttons {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
}

.schedules-card {
  margin-bottom: 20px;
}

.schedule-list {
  max-height: 300px;
  overflow-y: auto;
}

.schedule-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.schedule-item:last-child {
  border-bottom: none;
}

.time {
  width: 60px;
  font-weight: bold;
}

.event-info {
  flex: 1;
  margin: 0 15px;
}

.event-name {
  font-size: 14px;
  margin-bottom: 5px;
}

.event-location {
  font-size: 12px;
  color: #909399;
}

.empty-schedule {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100px;
  color: #909399;
}

.empty-schedule i {
  font-size: 32px;
  margin-bottom: 10px;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(64, 158, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0);
  }
}
</style> 