<template>
  <div class="dashboard-container">
    <div class="dashboard-welcome">
      <div class="welcome-info">
        <h1 class="welcome-title">欢迎回来, {{ name }}</h1>
        <p class="welcome-subtitle">今天是 {{ currentDate }}, 祝您工作愉快!</p>
      </div>
      <div class="welcome-decoration">
        <div class="airplane-animation">
          <svg class="airplane-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white">
            <path d="M21.5,15.5c-0.83,0-1.5-0.67-1.5-1.5V8.25L5.5,11.47V14c0,0.55-0.45,1-1,1h0c-0.55,0-1-0.45-1-1v-1.53L1,13v-2l2.5-0.5V9 c0-0.55,0.45-1,1-1h0c0.55,0,1,0.45,1,1v2.53l14.5-3.22V7.5C20,6.67,20.67,6,21.5,6S23,6.67,23,7.5v6C23,14.33,22.33,15,21.5,15.5z"/>
          </svg>
        </div>
        <div class="cloud-animation cloud-1"></div>
        <div class="cloud-animation cloud-2"></div>
        <div class="cloud-animation cloud-3"></div>
      </div>
    </div>
    
    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :md="16" :lg="18">
        <el-card class="dashboard-card stat-cards-container">
          <div slot="header" class="card-header">
            <span>系统概览</span>
            <el-button type="text" @click="refreshData">
              <i class="el-icon-refresh" :class="{'is-loading': refreshing}"></i>
            </el-button>
          </div>
          <div class="card-content">
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="stat-card" :class="{'stat-card-active': activeCard === 'users'}" 
                     @mouseenter="activeCard = 'users'" @mouseleave="activeCard = ''">
                  <div class="stat-icon">
                    <i class="el-icon-user"></i>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value count-up">{{ userCount }}</div>
                    <div class="stat-label">用户数量</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-card" :class="{'stat-card-active': activeCard === 'visits'}" 
                     @mouseenter="activeCard = 'visits'" @mouseleave="activeCard = ''">
                  <div class="stat-icon">
                    <i class="el-icon-s-data"></i>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value count-up">{{ visitCount }}</div>
                    <div class="stat-label">访问量</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-card" :class="{'stat-card-active': activeCard === 'data'}" 
                     @mouseenter="activeCard = 'data'" @mouseleave="activeCard = ''">
                  <div class="stat-icon">
                    <i class="el-icon-document"></i>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value count-up">{{ dataCount }}</div>
                    <div class="stat-label">数据量</div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
        
        <el-card class="dashboard-card flight-status-card">
          <div slot="header" class="card-header">
            <span>今日航班状态</span>
          </div>
          <div class="card-content">
            <div class="flight-status-overview">
              <div class="status-item">
                <div class="status-icon on-time">
                  <i class="el-icon-time"></i>
                </div>
                <div class="status-info">
                  <div class="status-value">{{ flightStatus.onTime }}</div>
                  <div class="status-label">准点</div>
                </div>
              </div>
              <div class="status-item">
                <div class="status-icon delayed">
                  <i class="el-icon-warning-outline"></i>
                </div>
                <div class="status-info">
                  <div class="status-value">{{ flightStatus.delayed }}</div>
                  <div class="status-label">延误</div>
                </div>
              </div>
              <div class="status-item">
                <div class="status-icon cancelled">
                  <i class="el-icon-close"></i>
                </div>
                <div class="status-info">
                  <div class="status-value">{{ flightStatus.cancelled }}</div>
                  <div class="status-label">取消</div>
                </div>
              </div>
            </div>
            
            <div class="lottie-section">
              <airport-lottie 
                animation-path="/lottie-animations/plane.json"
                width="100%" 
                height="120px" 
                :loop="true" 
                :autoplay="true" 
                :speed="0.8"
              />
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="24" :md="8" :lg="6">
        <el-card class="dashboard-card digital-human-card">
          <div slot="header" class="card-header">
            <span>智能数字人</span>
          </div>
          <div class="card-content">
            <digital-human ref="digitalHuman"></digital-human>
            <div class="digital-human-message">
              <p>点击下方按钮，让我为您服务</p>
              <el-button type="primary" size="small" @click="speakWelcomeMessage">
                <i class="el-icon-s-promotion"></i> 播报欢迎信息
              </el-button>
              <el-button type="success" size="small" @click="speakFlightStatus">
                <i class="el-icon-message"></i> 播报航班信息
              </el-button>
            </div>
          </div>
        </el-card>
        
        <el-card class="dashboard-card boarding-card">
          <div slot="header" class="card-header">
            <span>登机提示</span>
          </div>
          <div class="card-content">
            <div class="boarding-animation">
              <airport-lottie 
                animation-path="/lottie-animations/boarding.json"
                width="100%" 
                height="150px" 
                :loop="true" 
                :autoplay="true" 
                :speed="1"
              />
            </div>
            <div class="boarding-info">
              <p>当前登机航班:</p>
              <ul class="boarding-list">
                <li>CA1234 北京-上海 20号登机口</li>
                <li>MU5678 成都-广州 15号登机口</li>
              </ul>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import DigitalHuman from '@/components/DigitalHuman'
import AirportLottie from '@/components/AirportLottie'

export default {
  name: 'Dashboard',
  components: {
    DigitalHuman,
    AirportLottie
  },
  data() {
    return {
      userCount: 1254,
      visitCount: 5678,
      dataCount: 9876,
      currentDate: this.formatDate(new Date()),
      activeCard: '',
      refreshing: false,
      flightStatus: {
        onTime: 42,
        delayed: 7,
        cancelled: 2
      },
      digitalHumanConfig: null
    }
  },
  computed: {
    ...mapGetters([
      'name'
    ])
  },
  mounted() {
    // 加载数字人配置
    this.loadDigitalHumanConfig()
    
    // 页面加载完成后自动播报欢迎信息
    setTimeout(() => {
      this.speakWelcomeMessage()
    }, 1500)
  },
  methods: {
    // 加载数字人配置
    loadDigitalHumanConfig() {
      const savedConfig = localStorage.getItem('digitalHumanConfig')
      if (savedConfig) {
        try {
          this.digitalHumanConfig = JSON.parse(savedConfig)
        } catch (e) {
          console.error('解析数字人配置出错:', e)
          this.digitalHumanConfig = null
        }
      }
    },
    
    formatDate(date) {
      const year = date.getFullYear()
      const month = date.getMonth() + 1
      const day = date.getDate()
      const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
      const weekday = weekdays[date.getDay()]
      return `${year}年${month}月${day}日 ${weekday}`
    },
    refreshData() {
      this.refreshing = true
      setTimeout(() => {
        // 模拟数据刷新
        this.userCount = Math.floor(1000 + Math.random() * 1000)
        this.visitCount = Math.floor(5000 + Math.random() * 2000)
        this.dataCount = Math.floor(9000 + Math.random() * 2000)
        this.flightStatus = {
          onTime: Math.floor(30 + Math.random() * 20),
          delayed: Math.floor(5 + Math.random() * 10),
          cancelled: Math.floor(1 + Math.random() * 5)
        }
        this.refreshing = false
      }, 800)
    },
    speakWelcomeMessage() {
      // 使用配置中的欢迎语，如果没有则使用随机默认欢迎语
      if (this.digitalHumanConfig && this.digitalHumanConfig.welcomeMessage) {
        this.$refs.digitalHuman.speak(this.digitalHumanConfig.welcomeMessage)
      } else {
        const defaultMessages = [
          '欢迎使用智能机场服务系统，我是您的数字助手，有什么可以帮助您的吗？',
          '您好，我是机场数字服务助手，今天可以为您提供航班信息查询和播报服务。',
          '欢迎回来，我是您的智能助理，点击按钮可以获取最新的航班和机场服务信息。'
        ]
        const randomIndex = Math.floor(Math.random() * defaultMessages.length)
        const message = defaultMessages[randomIndex]
        this.$refs.digitalHuman.speak(message)
      }
    },
    speakFlightStatus() {
      const total = this.flightStatus.onTime + this.flightStatus.delayed + this.flightStatus.cancelled
      const message = `今日共有${total}个航班，其中${this.flightStatus.onTime}个准点航班，${this.flightStatus.delayed}个延误航班，${this.flightStatus.cancelled}个取消航班。`
      this.$refs.digitalHuman.speak(message)
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
  &-container {
    padding: 20px;
  }

  &-welcome {
    position: relative;
    margin-bottom: 20px;
    padding: 20px;
    background: linear-gradient(135deg, #409EFF, #36D1DC);
    border-radius: 8px;
    color: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    
    .welcome-title {
      font-size: 24px;
      margin: 0 0 10px 0;
    }
    
    .welcome-subtitle {
      font-size: 14px;
      margin: 0;
      opacity: 0.9;
    }
    
    .welcome-decoration {
      position: absolute;
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
      pointer-events: none;
      z-index: 1;
    }
    
    .welcome-info {
      position: relative;
      z-index: 2;
    }
  }
  
  &-card {
    margin-bottom: 20px;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: bold;
    }
    
    .card-content {
      padding: 10px 0;
    }
  }
}

.airplane-animation {
  position: absolute;
  top: 15px;
  right: -40px;
  
  .airplane-icon {
    width: 40px;
    height: 40px;
    animation: flyPlane 20s linear infinite;
  }
}

@keyframes flyPlane {
  0% {
    transform: translateX(0) translateY(0) rotate(-10deg);
  }
  25% {
    transform: translateX(-300px) translateY(20px) rotate(-5deg);
  }
  50% {
    transform: translateX(-600px) translateY(0) rotate(0deg);
  }
  75% {
    transform: translateX(-900px) translateY(-20px) rotate(5deg);
  }
  100% {
    transform: translateX(-1200px) translateY(0) rotate(0deg);
  }
}

.cloud-animation {
  position: absolute;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 50px;
  
  &.cloud-1 {
    width: 100px;
    height: 40px;
    top: 10px;
    right: 100px;
    animation: moveCloud 35s linear infinite;
  }
  
  &.cloud-2 {
    width: 70px;
    height: 30px;
    bottom: 15px;
    right: 200px;
    animation: moveCloud 25s linear infinite;
    animation-delay: -5s;
  }
  
  &.cloud-3 {
    width: 50px;
    height: 20px;
    top: 45px;
    right: 300px;
    animation: moveCloud 30s linear infinite;
    animation-delay: -12s;
  }
}

@keyframes moveCloud {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-1000px);
  }
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
  
  &:hover {
    background-color: #eef5ff;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  &-active {
    background-color: #eef5ff;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    
    .stat-icon {
      transform: scale(1.1);
    }
    
    .stat-value {
      color: #409EFF;
    }
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #409EFF;
    color: white;
    border-radius: 8px;
    margin-right: 15px;
    transition: all 0.3s ease;
    
    i {
      font-size: 24px;
    }
  }
  
  .stat-info {
    flex: 1;
    
    .stat-value {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 5px;
      transition: color 0.3s ease;
    }
    
    .stat-label {
      font-size: 12px;
      color: #909399;
    }
  }
}

.flight-status-card {
  .flight-status-overview {
    display: flex;
    justify-content: space-around;
    margin-top: 10px;
    
    .status-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 15px;
      border-radius: 8px;
      transition: all 0.3s ease;
      
      &:hover {
        background-color: #f8f9fa;
      }
      
      .status-icon {
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        margin-bottom: 10px;
        
        i {
          font-size: 24px;
          color: white;
        }
        
        &.on-time {
          background-color: #67C23A;
        }
        
        &.delayed {
          background-color: #E6A23C;
        }
        
        &.cancelled {
          background-color: #F56C6C;
        }
      }
      
      .status-info {
        text-align: center;
        
        .status-value {
          font-size: 18px;
          font-weight: bold;
          margin-bottom: 5px;
        }
        
        .status-label {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }
  
  .lottie-section {
    margin-top: 20px;
    border-top: 1px dashed #ebeef5;
    padding-top: 15px;
  }
}

.digital-human-card {
  height: calc(100% - 20px);
  
  .card-content {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .digital-human-message {
    text-align: center;
    margin-top: 15px;
    
    p {
      margin-bottom: 10px;
      color: #909399;
      font-size: 14px;
    }
  }
}

.boarding-card {
  .boarding-animation {
    margin-bottom: 15px;
  }
  
  .boarding-info {
    p {
      margin: 5px 0;
      font-weight: bold;
      color: #606266;
    }
    
    .boarding-list {
      list-style: none;
      padding: 0;
      margin: 10px 0 0 0;
      
      li {
        padding: 8px 10px;
        margin-bottom: 8px;
        background-color: #f0f9eb;
        color: #67c23a;
        border-radius: 4px;
        font-size: 12px;
        
        &:last-child {
          margin-bottom: 0;
        }
      }
    }
  }
}

.count-up {
  transition: all 0.5s ease;
}

.is-loading {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
