<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>添加公告</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="goBack">返回列表</el-button>
      </div>

      <el-form ref="announcementForm" :model="announcementForm" :rules="rules" label-width="120px" class="announcement-form">
        <el-form-item label="标题" prop="title">
          <el-input v-model="announcementForm.title" placeholder="请输入公告标题"></el-input>
        </el-form-item>

        <el-form-item label="公告类型" prop="type">
          <el-select v-model="announcementForm.type" placeholder="请选择公告类型" style="width: 100%">
            <el-option
              v-for="item in typeOptions"
              :key="item.id"
              :label="item.description"
              :value="item.id"
            >
              <span style="float: left">
                <i :class="item.icon" :style="{color: item.color}"></i> {{ item.description }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-select v-model="announcementForm.priority" placeholder="请选择优先级" style="width: 100%">
            <el-option label="低" :value="1" />
            <el-option label="中" :value="2" />
            <el-option label="高" :value="3" />
          </el-select>
        </el-form-item>

        <el-form-item label="是否激活" prop="is_active">
          <el-switch v-model="announcementForm.is_active" active-text="激活" inactive-text="停用" />
        </el-form-item>

        <el-form-item label="生效时间" prop="start_time">
          <el-date-picker
            v-model="announcementForm.start_time"
            type="datetime"
            placeholder="选择生效时间"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="失效时间" prop="end_time">
          <el-date-picker
            v-model="announcementForm.end_time"
            type="datetime"
            placeholder="选择失效时间"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="相关位置" prop="location">
          <el-input v-model="announcementForm.location" placeholder="请输入相关位置（如：T1航站楼、A区安检处等）"></el-input>
        </el-form-item>

        <el-form-item label="公告内容" prop="content">
          <el-input 
            v-model="announcementForm.content" 
            type="textarea" 
            :rows="6" 
            placeholder="请输入公告内容"
          />
        </el-form-item>

        <el-form-item label="播报预览">
          <div class="preview-container">
            <div class="preview-content">{{ generateVoiceContent() }}</div>
            <el-button type="success" @click="previewVoiceContent">数字人播报预览</el-button>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submitForm">提交</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 播报预览对话框 -->
    <el-dialog :visible.sync="dialogPreviewVisible" title="播报预览">
      <digital-human ref="digitalHuman"></digital-human>
      <div style="margin-top: 20px; text-align: center;">
        <el-button type="primary" @click="previewPlay">开始播报预览</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getAnnouncementTypeList, addAnnouncement } from '@/api/announcement'
import DigitalHuman from '@/components/DigitalHuman'

export default {
  name: 'AddAnnouncement',
  components: {
    DigitalHuman
  },
  data() {
    return {
      loading: false,
      typeOptions: [],
      announcementForm: {
        title: '',
        content: '',
        type: '',
        priority: 2, // 默认中优先级
        is_active: true, // 默认激活
        start_time: null,
        end_time: null,
        location: ''
      },
      rules: {
        title: [
          { required: true, message: '请输入公告标题', trigger: 'blur' },
          { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
        ],
        content: [
          { required: true, message: '请输入公告内容', trigger: 'blur' }
        ],
        type: [
          { required: true, message: '请选择公告类型', trigger: 'change' }
        ],
        priority: [
          { required: true, message: '请选择优先级', trigger: 'change' }
        ]
      },
      dialogPreviewVisible: false,
      selectedType: null
    }
  },
  created() {
    this.getTypeList()
  },
  methods: {
    getTypeList() {
      getAnnouncementTypeList().then(response => {
        this.typeOptions = response.results || []
      })
    },
    submitForm() {
      this.$refs.announcementForm.validate(valid => {
        if (valid) {
          this.loading = true
          
          // 处理时间格式
          const formData = { ...this.announcementForm }
          
          addAnnouncement(formData).then(response => {
            this.$message({
              message: '添加公告成功！',
              type: 'success'
            })
            this.loading = false
            this.goBack()
          }).catch(error => {
            console.error('添加公告失败:', error)
            this.$message.error('添加公告失败，请重试')
            this.loading = false
          })
        } else {
          return false
        }
      })
    },
    resetForm() {
      this.$refs.announcementForm.resetFields()
    },
    goBack() {
      this.$router.push({ name: 'AdminAnnouncementList' })
    },
    getSelectedTypeDescription() {
      if (!this.announcementForm.type) return '通知'
      const selectedType = this.typeOptions.find(item => item.id === this.announcementForm.type)
      return selectedType ? selectedType.description : '通知'
    },
    generateVoiceContent() {
      const typeName = this.getSelectedTypeDescription()
      const { title, content, location } = this.announcementForm
      
      if (!title && !content) {
        return '请填写公告标题和内容以预览播报内容'
      }
      
      if (location) {
        return `${typeName}：${title || ''}。${content || ''}。相关区域：${location}。`
      }
      return `${typeName}：${title || ''}。${content || ''}。`
    },
    previewVoiceContent() {
      this.dialogPreviewVisible = true
    },
    previewPlay() {
      const content = this.generateVoiceContent()
      this.$refs.digitalHuman.speak(content)
    }
  }
}
</script>

<style lang="scss" scoped>
.announcement-form {
  max-width: 800px;
  margin: 0 auto;
}

.preview-container {
  display: flex;
  flex-direction: column;
  
  .preview-content {
    background-color: #f8f8f8;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 10px;
    margin-bottom: 10px;
    min-height: 60px;
  }
}
</style> 