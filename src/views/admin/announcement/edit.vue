<template>
  <div class="app-container">
    <el-card class="edit-card" v-loading="loading">
      <div slot="header" class="clearfix">
        <span>编辑公告</span>
        <el-button type="text" @click="goBack" style="float: right">返回列表</el-button>
      </div>
      
      <el-form ref="announcementForm" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="公告标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入公告标题" maxlength="100" show-word-limit></el-input>
        </el-form-item>
        
        <el-form-item label="公告类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择公告类型" style="width: 100%">
            <el-option 
              v-for="item in typeOptions" 
              :key="item.id" 
              :label="item.description" 
              :value="item.id">
              <span style="float: left">
                <i :class="item.icon" :style="{color: item.color}"></i> {{ item.description }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="form.priority" placeholder="请选择优先级" style="width: 100%">
            <el-option label="低" :value="1"></el-option>
            <el-option label="中" :value="2"></el-option>
            <el-option label="高" :value="3"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="form.is_active"
            active-text="激活"
            inactive-text="停用"
            active-color="#13ce66"
            inactive-color="#ff4949">
          </el-switch>
        </el-form-item>
        
        <el-form-item label="相关位置" prop="location">
          <el-input v-model="form.location" placeholder="请输入相关位置（选填）" maxlength="100"></el-input>
        </el-form-item>
        
        <el-form-item label="生效时间" prop="start_time">
          <el-date-picker
            v-model="form.start_time"
            type="datetime"
            placeholder="选择生效时间（选填）"
            style="width: 100%">
          </el-date-picker>
        </el-form-item>
        
        <el-form-item label="失效时间" prop="end_time">
          <el-date-picker
            v-model="form.end_time"
            type="datetime"
            placeholder="选择失效时间（选填）"
            style="width: 100%">
          </el-date-picker>
        </el-form-item>
        
        <el-form-item label="公告内容" prop="content">
          <el-input
            type="textarea"
            v-model="form.content"
            :rows="6"
            placeholder="请输入公告内容"
            maxlength="1000"
            show-word-limit>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm('announcementForm')">保存</el-button>
          <el-button @click="resetForm('announcementForm')">重置</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>

      <!-- 语音测试部分 -->
      <div class="voice-test-container" v-if="form.title && form.content">
        <div class="section-title">语音效果预览</div>
        <digital-human ref="digitalHuman"></digital-human>
        <div class="action-buttons">
          <el-button type="primary" @click="testVoice">测试播报</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { getAnnouncementDetail, getAnnouncementTypeList, updateAnnouncement } from '@/api/announcement'
import DigitalHuman from '@/components/DigitalHuman'

export default {
  name: 'EditAnnouncement',
  components: {
    DigitalHuman
  },
  data() {
    return {
      loading: false,
      announcementId: null,
      typeOptions: [],
      form: {
        title: '',
        content: '',
        type: '',
        priority: 2,
        is_active: true,
        location: '',
        start_time: null,
        end_time: null
      },
      rules: {
        title: [
          { required: true, message: '请输入公告标题', trigger: 'blur' },
          { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
        ],
        content: [
          { required: true, message: '请输入公告内容', trigger: 'blur' },
          { min: 5, max: 1000, message: '长度在 5 到 1000 个字符', trigger: 'blur' }
        ],
        type: [
          { required: true, message: '请选择公告类型', trigger: 'change' }
        ],
        priority: [
          { required: true, message: '请选择优先级', trigger: 'change' }
        ],
        end_time: [
          { 
            validator: (rule, value, callback) => {
              if (this.form.start_time && value && value < this.form.start_time) {
                callback(new Error('失效时间不能早于生效时间'));
              } else {
                callback();
              }
            }, 
            trigger: 'change' 
          }
        ]
      }
    }
  },
  created() {
    this.announcementId = this.$route.params.id
    this.getTypeList()
    this.fetchAnnouncementDetail()
  },
  methods: {
    getTypeList() {
      getAnnouncementTypeList().then(response => {
        this.typeOptions = response.results || []
      })
    },
    fetchAnnouncementDetail() {
      this.loading = true
      getAnnouncementDetail(this.announcementId).then(response => {
        // 填充表单数据
        this.form = {
          title: response.title,
          content: response.content,
          type: response.type,
          priority: response.priority,
          is_active: response.is_active,
          location: response.location || '',
          start_time: response.start_time ? new Date(response.start_time) : null,
          end_time: response.end_time ? new Date(response.end_time) : null
        }
        
        this.loading = false
      }).catch(error => {
        console.error('获取公告详情失败:', error)
        this.$message.error('获取公告详情失败，请重试')
        this.loading = false
      })
    },
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          this.loading = true
          
          // 准备提交的数据
          const submitData = {
            title: this.form.title,
            content: this.form.content,
            type: this.form.type,
            priority: this.form.priority,
            is_active: this.form.is_active,
            location: this.form.location || null,
            start_time: this.form.start_time || null,
            end_time: this.form.end_time || null
          }
          
          updateAnnouncement(this.announcementId, submitData).then(response => {
            this.$message({
              type: 'success',
              message: '更新公告成功！'
            })
            this.loading = false
            this.goBack()
          }).catch(error => {
            console.error('更新公告失败:', error)
            this.$message.error('更新公告失败，请重试')
            this.loading = false
          })
        } else {
          return false
        }
      })
    },
    resetForm(formName) {
      this.$refs[formName].resetFields()
      // 重新获取公告原始数据
      this.fetchAnnouncementDetail()
    },
    goBack() {
      this.$router.push({ name: 'AdminAnnouncementList' })
    },
    testVoice() {
      if (!this.form.title || !this.form.content) {
        this.$message.warning('请先填写公告标题和内容')
        return
      }
      
      // 生成测试播报内容
      let typeName = '通知'
      if (this.form.type) {
        const selectedType = this.typeOptions.find(item => item.id === this.form.type)
        if (selectedType) {
          typeName = selectedType.description
        }
      }
      
      let voiceContent = `${typeName}：${this.form.title}。${this.form.content}`
      
      if (this.form.location) {
        voiceContent += `。相关区域：${this.form.location}`
      }
      
      // 调用数字人播报
      this.$refs.digitalHuman.speak(voiceContent)
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  .edit-card {
    max-width: 900px;
    margin: 0 auto;
  }
  
  .voice-test-container {
    margin-top: 30px;
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .section-title {
      align-self: flex-start;
      font-weight: bold;
      margin-bottom: 15px;
      color: #303133;
    }
    
    .action-buttons {
      margin-top: 15px;
    }
  }
}
</style> 