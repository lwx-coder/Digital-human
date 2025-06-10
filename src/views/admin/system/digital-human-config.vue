<template>
  <div class="app-container">
    <el-card class="config-card">
      <div slot="header" class="clearfix">
        <span>数字人配置</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="saveConfig">保存配置</el-button>
      </div>
      
      <el-form :model="configForm" label-width="120px" ref="configForm">
        <el-row :gutter="20">
          <el-col :span="12">
            <!-- 基本配置 -->
            <h3 class="section-title">基本配置</h3>
            
            <el-form-item label="数字人名称" prop="name">
              <el-input v-model="configForm.name" placeholder="请输入数字人名称"></el-input>
            </el-form-item>
            
            <el-form-item label="默认欢迎语" prop="welcomeMessage">
              <el-input 
                type="textarea" 
                :rows="3" 
                v-model="configForm.welcomeMessage" 
                placeholder="请输入默认欢迎语"
              ></el-input>
            </el-form-item>
            
            <el-form-item label="数字人头像">
              <el-upload
                class="avatar-uploader"
                action="#"
                :http-request="uploadAvatar"
                :show-file-list="false"
                :before-upload="beforeAvatarUpload">
                <img v-if="configForm.avatarUrl" :src="configForm.avatarUrl" class="avatar">
                <i v-else class="el-icon-plus avatar-uploader-icon"></i>
              </el-upload>
              <div class="avatar-tip">建议上传 1:1 比例的图片</div>
              <el-input 
                v-model="configForm.avatarUrl" 
                placeholder="或直接输入头像URL地址"
                style="margin-top: 10px;"
              ></el-input>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <!-- 语音配置 -->
            <h3 class="section-title">语音配置</h3>
            
            <el-form-item label="语音语言" prop="language">
              <el-select v-model="configForm.language" placeholder="请选择语言">
                <el-option label="中文(女音)" value="zh-CN"></el-option>
                <el-option label="中文(男音)" value="ko-KR"></el-option>
                <el-option label="日语" value="ja-JP"></el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item label="语速调节" prop="rate">
              <el-slider
                v-model="configForm.rate"
                :min="0.5"
                :max="2"
                :step="0.1"
                :format-tooltip="formatRate"
                show-stops
              ></el-slider>
              <div class="slider-info">当前语速: {{ formatRate(configForm.rate) }}</div>
            </el-form-item>
            
            <el-form-item label="音调调节" prop="pitch">
              <el-slider
                v-model="configForm.pitch"
                :min="0.5"
                :max="2"
                :step="0.1"
                :format-tooltip="formatPitch"
                show-stops
              ></el-slider>
              <div class="slider-info">当前音调: {{ formatPitch(configForm.pitch) }}</div>
            </el-form-item>
            
            <el-form-item label="音量调节" prop="volume">
              <el-slider
                v-model="configForm.volume"
                :min="0"
                :max="1"
                :step="0.1"
                :format-tooltip="formatVolume"
                show-stops
              ></el-slider>
              <div class="slider-info">当前音量: {{ formatVolume(configForm.volume) }}</div>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 预设消息配置 -->
        <h3 class="section-title">预设消息配置</h3>
        <div class="preset-messages">
          <div v-for="(message, index) in configForm.presetMessages" :key="index" class="preset-message-item">
            <el-input
              type="textarea"
              :rows="2"
              v-model="configForm.presetMessages[index]"
              placeholder="输入预设消息"
            >
              <el-button 
                slot="append" 
                icon="el-icon-delete" 
                @click="removePresetMessage(index)"
              ></el-button>
            </el-input>
          </div>
          <el-button class="add-message-btn" type="primary" plain @click="addPresetMessage">
            <i class="el-icon-plus"></i> 添加预设消息
          </el-button>
        </div>
      </el-form>
      
      <!-- 测试功能 -->
      <div class="test-section">
        <h3 class="section-title">测试配置</h3>
        <div class="test-content">
          <el-input
            type="textarea"
            :rows="3"
            v-model="testText"
            placeholder="输入测试文本"
          ></el-input>
          <div class="digital-human-preview">
            <digital-human ref="digitalHuman"></digital-human>
          </div>
          <div class="test-actions">
            <el-button type="primary" @click="testSpeech">测试语音</el-button>
            <el-button type="info" @click="testRandomMessage">测试随机消息</el-button>
            <el-button @click="resetConfig">重置配置</el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import DigitalHuman from '@/components/DigitalHuman'

export default {
  name: 'DigitalHumanConfig',
  components: {
    DigitalHuman
  },
  data() {
    return {
      configForm: {
        name: '智能助手',
        welcomeMessage: '您好，我是机场智能数字人助手，有什么可以帮助您的吗？',
        avatarUrl: 'https://imgcdn.ccmapp.cn/7/860x/5ba08a598a8691c371bea451/application/f1wgwXrHilsYew7iOSusc9NBwtCHe5ns/2023/0221/155e3990-b19a-11ed-8a09-87fb4e858195.png',
        language: 'zh-CN',
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
        presetMessages: [
          '欢迎使用数字人系统，我能为您提供智能助手服务',
          '今天天气不错，适合出门散步',
          '您有3条未读消息，请注意查看',
          '系统运行状态良好，所有服务正常运行中',
          '今日访问量比昨日增长了15%',
          '数据分析完成，您可以在报表中查看详细信息',
          '已为您自动整理了今日工作事项',
          '祝您工作顺利，有问题随时可以呼叫我'
        ]
      },
      testText: '这是一段测试文本，用于测试数字人语音效果。',
      loading: false
    }
  },
  created() {
    // 从本地存储或API加载配置
    this.loadConfig()
  },
  methods: {
    // 加载配置
    loadConfig() {
      this.loading = true
      // 这里可以从API获取配置，或者从本地存储获取
      const savedConfig = localStorage.getItem('digitalHumanConfig')
      if (savedConfig) {
        try {
          const config = JSON.parse(savedConfig)
          this.configForm = { ...this.configForm, ...config }
        } catch (e) {
          this.$message.error('加载配置失败')
          console.error('解析配置出错:', e)
        }
      }
      this.loading = false
    },
    
    // 保存配置
    saveConfig() {
      // 可以保存到API或本地存储
      localStorage.setItem('digitalHumanConfig', JSON.stringify(this.configForm))
      // 更新数字人组件的配置
      if (this.$refs.digitalHuman) {
        this.$refs.digitalHuman.updateConfig(this.configForm)
      }
      this.$message.success('配置已保存')
    },
    
    // 重置配置
    resetConfig() {
      this.$confirm('确定要重置所有配置吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 重置为默认配置
        this.configForm = {
          name: '智能助手',
          welcomeMessage: '您好，我是机场智能数字人助手，有什么可以帮助您的吗？',
          avatarUrl: 'https://imgcdn.ccmapp.cn/7/860x/5ba08a598a8691c371bea451/application/f1wgwXrHilsYew7iOSusc9NBwtCHe5ns/2023/0221/155e3990-b19a-11ed-8a09-87fb4e858195.png',
          language: 'zh-CN',
          rate: 1.0,
          pitch: 1.0,
          volume: 1.0,
          presetMessages: [
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
        localStorage.removeItem('digitalHumanConfig')
        this.$message.success('配置已重置')
      }).catch(() => {
        // 取消重置
      })
    },
    
    // 格式化语速显示
    formatRate(val) {
      return `${val}x`
    },
    
    // 格式化音调显示
    formatPitch(val) {
      if (val < 1) {
        return `低(${val})`
      } else if (val > 1) {
        return `高(${val})`
      } else {
        return `中(${val})`
      }
    },
    
    // 格式化音量显示
    formatVolume(val) {
      return `${Math.round(val * 100)}%`
    },
    
    // 添加预设消息
    addPresetMessage() {
      this.configForm.presetMessages.push('')
    },
    
    // 移除预设消息
    removePresetMessage(index) {
      this.configForm.presetMessages.splice(index, 1)
    },
    
    // 上传头像前的验证
    beforeAvatarUpload(file) {
      const isImage = file.type.startsWith('image/')
      const isLt2M = file.size / 1024 / 1024 < 2
      
      if (!isImage) {
        this.$message.error('上传头像图片只能是图片格式!')
      }
      if (!isLt2M) {
        this.$message.error('上传头像图片大小不能超过 2MB!')
      }
      return isImage && isLt2M
    },
    
    // 自定义上传头像
    uploadAvatar(options) {
      const file = options.file
      // 这里可以实现上传到服务器的逻辑
      // 目前使用本地的 FileReader 实现预览
      const reader = new FileReader()
      reader.onload = (e) => {
        this.configForm.avatarUrl = e.target.result
      }
      reader.readAsDataURL(file)
      
      // 模拟上传成功
      setTimeout(() => {
        this.$message.success('头像上传成功')
      }, 1000)
    },
    
    // 测试语音
    testSpeech() {
      if (!this.testText.trim()) {
        this.$message.warning('请输入测试文本')
        return
      }
      
      // 使用数字人组件播放语音
      if (this.$refs.digitalHuman) {
        // 先更新配置
        this.$refs.digitalHuman.updateConfig(this.configForm)
        // 播放测试文本
        this.$refs.digitalHuman.speak(this.testText)
      }
    },
    
    // 测试随机消息
    testRandomMessage() {
      if (this.configForm.presetMessages.length === 0) {
        this.$message.warning('请先添加预设消息')
        return
      }
      
      // 使用数字人组件播放随机消息
      if (this.$refs.digitalHuman) {
        // 先更新配置
        this.$refs.digitalHuman.updateConfig(this.configForm)
        // 播放随机消息
        this.$refs.digitalHuman.speakRandomMessage()
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.config-card {
  margin-bottom: 20px;
}

.section-title {
  margin: 20px 0 15px;
  padding-left: 10px;
  border-left: 3px solid #409EFF;
  font-size: 16px;
  font-weight: bold;
}

.avatar-uploader {
  display: inline-block;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  
  &:hover {
    border-color: #409EFF;
  }
  
  .avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 100px;
    height: 100px;
    line-height: 100px;
    text-align: center;
  }
  
  .avatar {
    width: 100px;
    height: 100px;
    display: block;
    object-fit: contain;
  }
}

.avatar-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 5px;
}

.slider-info {
  color: #606266;
  font-size: 12px;
  margin-top: 5px;
  text-align: right;
}

.preset-messages {
  margin-bottom: 20px;
  
  .preset-message-item {
    margin-bottom: 10px;
  }
  
  .add-message-btn {
    width: 100%;
  }
}

.test-section {
  border-top: 1px solid #EBEEF5;
  padding-top: 20px;
  margin-top: 30px;
  
  .test-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .digital-human-preview {
      margin: 20px 0;
    }
    
    .test-actions {
      display: flex;
      gap: 10px;
      margin-top: 10px;
    }
  }
}

@media (max-width: 768px) {
  .el-form-item {
    margin-bottom: 18px;
  }
  
  .test-section .test-actions {
    flex-direction: column;
    width: 100%;
    
    .el-button {
      margin-left: 0 !important;
      margin-bottom: 10px;
    }
  }
}
</style> 