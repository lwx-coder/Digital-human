<template>
  <div class="app-container">
    <el-card class="form-card">
      <div class="card-header">
        <h2>物品报失</h2>
        <p class="sub-title">请填写您丢失物品的详细信息，以便我们帮助您寻找</p>
      </div>
      
      <el-form ref="lostItemForm" :model="form" :rules="rules" label-width="120px" v-loading="loading">
        <el-form-item label="物品名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入物品名称" maxlength="100"></el-input>
        </el-form-item>
        
        <el-form-item label="物品类别" prop="category">
          <el-select v-model="form.category" placeholder="请选择物品类别" style="width: 100%">
            <el-option
              v-for="item in categoryOptions"
              :key="item.id"
              :label="item.description"
              :value="item.id">
              <span style="float: left">
                <i :class="item.icon" :style="{marginRight: '8px'}"></i> {{ item.description }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="丢失时间" prop="lost_time">
          <el-date-picker
            v-model="form.lost_time"
            type="datetime"
            placeholder="选择丢失时间"
            style="width: 100%">
          </el-date-picker>
        </el-form-item>
        
        <el-form-item label="丢失地点" prop="lost_location">
          <el-input v-model="form.lost_location" placeholder="请尽量详细描述丢失地点，如航站楼、登机口等"></el-input>
        </el-form-item>
        
        <el-form-item label="物品描述" prop="description">
          <el-input
            type="textarea"
            v-model="form.description"
            :rows="5"
            placeholder="请详细描述物品的特征，如颜色、大小、品牌等，以便我们更好地帮助您找回物品"
            maxlength="500"
            show-word-limit>
          </el-input>
        </el-form-item>
        
        <el-form-item label="联系人姓名" prop="contact_name">
          <el-input v-model="form.contact_name" placeholder="请输入联系人姓名"></el-input>
        </el-form-item>
        
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="form.contact_phone" placeholder="请输入联系电话"></el-input>
        </el-form-item>
        
        <el-form-item label="联系邮箱" prop="contact_email">
          <el-input v-model="form.contact_email" placeholder="请输入联系邮箱（选填）"></el-input>
        </el-form-item>
        
        <el-form-item label="物品图片URL" prop="image">
          <el-input v-model="form.image" placeholder="请输入物品图片的URL地址（选填）"></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm('lostItemForm')">提交报失</el-button>
          <el-button @click="resetForm('lostItemForm')">重置</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { getItemCategoryList, addLostItem } from '@/api/lost-item'

export default {
  name: 'AddLostItem',
  data() {
    return {
      loading: false,
      categoryOptions: [],
      form: {
        title: '',
        category: '',
        lost_time: new Date(),
        lost_location: '',
        description: '',
        contact_name: '',
        contact_phone: '',
        contact_email: '',
        image: ''
      },
      rules: {
        title: [
          { required: true, message: '请输入物品名称', trigger: 'blur' },
          { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
        ],
        category: [
          { required: true, message: '请选择物品类别', trigger: 'change' }
        ],
        lost_time: [
          { required: true, message: '请选择丢失时间', trigger: 'change' }
        ],
        lost_location: [
          { required: true, message: '请输入丢失地点', trigger: 'blur' },
          { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
        ],
        description: [
          { required: true, message: '请输入物品描述', trigger: 'blur' },
          { min: 5, max: 500, message: '长度在 5 到 500 个字符', trigger: 'blur' }
        ],
        contact_name: [
          { required: true, message: '请输入联系人姓名', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        contact_phone: [
          { required: true, message: '请输入联系电话', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
        ],
        contact_email: [
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ]
      }
    }
  },
  created() {
    this.fetchCategories()
  },
  methods: {
    fetchCategories() {
      this.loading = true
      getItemCategoryList().then(response => {
        this.categoryOptions = response.results || []
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          this.loading = true
          
          // 转换日期为ISO字符串
          const submitData = {
            ...this.form,
            lost_time: this.form.lost_time.toISOString()
          }
          
          addLostItem(submitData).then(response => {
            this.$message({
              type: 'success',
              message: '物品报失信息提交成功！'
            })
            
            this.loading = false
            this.goBack()
          }).catch(error => {
            console.error('提交失物信息失败:', error)
            this.$message.error('提交失败，请稍后重试')
            this.loading = false
          })
        } else {
          return false
        }
      })
    },
    resetForm(formName) {
      this.$refs[formName].resetFields()
    },
    goBack() {
      this.$router.push({ name: 'PassengerLostItemList' })
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  .form-card {
    max-width: 800px;
    margin: 0 auto;
    
    .card-header {
      margin-bottom: 20px;
      padding-bottom: 15px;
      border-bottom: 1px solid #ebeef5;
      
      h2 {
        margin-top: 0;
        margin-bottom: 10px;
        color: #303133;
      }
      
      .sub-title {
        margin: 0;
        color: #909399;
      }
    }
  }
}
</style> 