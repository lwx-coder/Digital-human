<template>
  <div class="digital-human-container">
    <div class="human-avatar">
      <template v-if="isSpeaking">
        <video class="avatar-video" :src="videoSrc" type="video/webm" autoplay muted loop ></video>
      </template>
      <template v-else>
        <img :src="avatarSrc" alt="数字人头像" class="avatar-img" />
      </template>
    </div>
    <div class="human-controls">
      <el-button type="primary" size="small" @click="speakRandomMessage" :disabled="isSpeaking">
        <i class="el-icon-microphone"></i> 随机播报
      </el-button>
      <el-button type="info" size="small" @click="speakCustomMessage" :disabled="isSpeaking">
        <i class="el-icon-message"></i> 自定义播报
      </el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DigitalHuman',
  data() {
    return {
      avatarSrc: 'https://imgcdn.ccmapp.cn/7/860x/5ba08a598a8691c371bea451/application/f1wgwXrHilsYew7iOSusc9NBwtCHe5ns/2023/0221/155e3990-b19a-11ed-8a09-87fb4e858195.png', // 使用占位图
      videoSrc: require('../../assets/avator_vedio.webm'),
      isSpeaking: false,
      speechSynthesis: null,
      // 语音配置
      config: {
        name: '智能助手',
        language: 'zh-CN',
        rate: 1.2, // 语速
        pitch: 1.2, // 音调
        volume: 1.0  // 音量
      },
      randomMessages: [
        '欢迎使用数字人系统，我能为您提供智能助手服务',
        '今天天气不错，适合出门散步',
        '您有3条未读消息，请注意查看',
        '系统运行状态良好，所有服务正常运行中',
        '今日访问量比昨日增长了15%',
        '数据分析完成，您可以在报表中查看详细信息',
        '已为您自动整理了今日工作事项',
        '祝您工作顺利，有问题随时可以呼叫我'
      ]
    }
  },
  mounted() {
    // 检查浏览器是否支持语音合成API
    if ('speechSynthesis' in window) {
      this.speechSynthesis = window.speechSynthesis
    } else {
      this.$message.warning('您的浏览器不支持语音合成功能')
    }
    
    // 尝试从本地存储加载配置
    this.loadConfig()
  },
  methods: {
    // 加载配置
    loadConfig() {
      const savedConfig = localStorage.getItem('digitalHumanConfig')
      if (savedConfig) {
        try {
          const config = JSON.parse(savedConfig)
          // 更新头像
          if (config.avatarUrl) {
            this.avatarSrc = config.avatarUrl
          }
          
          // 更新语音配置
          if (config.language) {
            this.config.language = config.language
          }
          if (config.rate) {
            this.config.rate = config.rate
          }
          if (config.pitch) {
            this.config.pitch = config.pitch
          }
          if (config.volume) {
            this.config.volume = config.volume
          }
          
          // 更新预设消息
          if (config.presetMessages && config.presetMessages.length > 0) {
            this.randomMessages = config.presetMessages
          }
        } catch (e) {
          console.error('解析数字人配置出错:', e)
        }
      }
    },
    
    // 更新配置
    updateConfig(newConfig) {
      if (!newConfig) return
      
      // 更新头像
      if (newConfig.avatarUrl) {
        this.avatarSrc = newConfig.avatarUrl
      }
      
      // 更新语音配置
      if (newConfig.language) {
        this.config.language = newConfig.language
      }
      if (newConfig.rate !== undefined) {
        this.config.rate = newConfig.rate
      }
      if (newConfig.pitch !== undefined) {
        this.config.pitch = newConfig.pitch
      }
      if (newConfig.volume !== undefined) {
        this.config.volume = newConfig.volume
      }
      
      // 更新预设消息
      if (newConfig.presetMessages && newConfig.presetMessages.length > 0) {
        this.randomMessages = newConfig.presetMessages
      }
      
      console.log('数字人配置已更新', this.config)
    },
    
    // 播放随机消息
    speakRandomMessage() {
      if (!this.speechSynthesis) return
      const randomIndex = Math.floor(Math.random() * this.randomMessages.length)
      const message = this.randomMessages[randomIndex]
      this.speak(message)
    },
    // 播放自定义消息
    speakCustomMessage() {
      if (!this.speechSynthesis) return
      this.$prompt('请输入要播报的内容', '自定义播报', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /.+/,
        inputErrorMessage: '播报内容不能为空'
      }).then(({ value }) => {
        this.speak(value)
      }).catch(() => {
        this.$message.info('已取消播报')
      })
    },
    // 执行语音播报
    speak(text) {
      if (!this.speechSynthesis) return
      this.isSpeaking = true
      // 创建语音对象
      const utterance = new SpeechSynthesisUtterance(text)
      // 设置语音参数
      utterance.lang = this.config.language
      utterance.rate = this.config.rate
      utterance.pitch = this.config.pitch
      utterance.volume = this.config.volume
      
      // 监听语音结束事件
      utterance.onend = () => {
        this.isSpeaking = false
      }
      // 监听语音错误事件
      utterance.onerror = (event) => {
        console.error('语音合成错误:', event)
        this.isSpeaking = false
        this.$message.error('语音播报失败')
      }
      // 开始播放语音
      this.speechSynthesis.speak(utterance)
    }
  }
}
</script>

<style lang="scss" scoped>
.digital-human-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.human-avatar {
  position: relative;
  margin-bottom: 20px;
  .avatar-img {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: contain;
    border: 3px solid #409EFF;
  }
  .avatar-video {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: contain;
    border: 3px solid #409EFF;
  }
}

.human-controls {
  display: flex;
  gap: 10px;
}

@keyframes sound-wave {
  0%, 100% {
    height: 5px;
  }
  50% {
    height: 15px;
  }
}
</style> 