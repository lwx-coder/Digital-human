<template>
  <div class="app-container">
    <el-card class="form-card">
      <div slot="header" class="clearfix">
        <span>处理失物信息</span>
        <el-button type="text" @click="goBack" style="float: right">返回详情</el-button>
      </div>
      
      <el-form ref="lostItemForm" :model="form" :rules="rules" label-width="120px" v-loading="loading">
        <el-form-item label="物品名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入物品名称"></el-input>
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
        
        <el-form-item label="处理状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择处理状态" style="width: 100%">
            <el-option label="寻物中" value="lost"></el-option>
            <el-option label="已找到" value="found"></el-option>
            <el-option label="已认领" value="claimed"></el-option>
            <el-option label="已关闭" value="closed"></el-option>
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
          <el-input v-model="form.lost_location" placeholder="请输入丢失地点"></el-input>
        </el-form-item>
        
        <el-form-item label="物品描述" prop="description">
          <el-input
            type="textarea"
            v-model="form.description"
            :rows="4"
            placeholder="物品描述">
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
          <el-input v-model="form.image" placeholder="请输入物品图片URL（选填）"></el-input>
        </el-form-item>
        
        <el-form-item label="管理员备注" prop="admin_notes">
          <el-input
            type="textarea"
            v-model="form.admin_notes"
            :rows="4"
            placeholder="请输入处理过程、结果等相关备注信息"
            maxlength="500"
            show-word-limit>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm('lostItemForm')">保存</el-button>
          <el-button @click="resetForm('lostItemForm')">重置</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { getItemCategoryList, getLostItemDetail, updateLostItem } from '@/api/lost-item'

export default {
  name: 'EditLostItem',
  data() {
    return {
      loading: false,
      categoryOptions: [],
      itemId: null,
      form: {
        title: '',
        category: '',
        status: 'lost',
        lost_time: '',
        lost_location: '',
        description: '',
        contact_name: '',
        contact_phone: '',
        contact_email: '',
        image: '',
        admin_notes: ''
      },
      rules: {
        title: [
          { required: true, message: '请输入物品名称', trigger: 'blur' }
        ],
        category: [
          { required: true, message: '请选择物品类别', trigger: 'change' }
        ],
        status: [
          { required: true, message: '请选择处理状态', trigger: 'change' }
        ],
        lost_time: [
          { required: true, message: '请选择丢失时间', trigger: 'change' }
        ],
        lost_location: [
          { required: true, message: '请输入丢失地点', trigger: 'blur' }
        ],
        description: [
          { required: true, message: '请输入物品描述', trigger: 'blur' }
        ],
        contact_name: [
          { required: true, message: '请输入联系人姓名', trigger: 'blur' }
        ],
        contact_phone: [
          { required: true, message: '请输入联系电话', trigger: 'blur' }
        ],
        contact_email: [
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ]
      }
    }
  },
  created() {
    this.itemId = this.$route.params.id
    this.fetchCategories()
    this.fetchLostItemDetail()
  },
  methods: {
    fetchCategories() {
      getItemCategoryList().then(response => {
        this.categoryOptions = response.results || []
      })
    },
    fetchLostItemDetail() {
      if (!this.itemId) {
        this.$message.error('参数错误')
        this.goBack()
        return
      }
      
      this.loading = true
      getLostItemDetail(this.itemId).then(response => {
        // 填充表单数据
        this.form = {
          title: response.title,
          category: response.category,
          status: response.status,
          lost_time: new Date(response.lost_time),
          lost_location: response.lost_location,
          description: response.description,
          contact_name: response.contact_name,
          contact_phone: response.contact_phone,
          contact_email: response.contact_email || '',
          image: response.image || '',
          admin_notes: response.admin_notes || ''
        }
        
        this.loading = false
      }).catch(error => {
        console.error('获取失物详情失败:', error)
        this.$message.error('获取失物详情失败，请重试')
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
          
          updateLostItem(this.itemId, submitData).then(response => {
            this.$message({
              type: 'success',
              message: '更新失物信息成功！'
            })
            
            this.loading = false
            this.goToDetail()
          }).catch(error => {
            console.error('更新失物信息失败:', error)
            this.$message.error('更新失败，请稍后重试')
            this.loading = false
          })
        } else {
          return false
        }
      })
    },
    resetForm(formName) {
      this.$refs[formName].resetFields()
      this.fetchLostItemDetail()
    },
    goBack() {
      this.goToDetail()
    },
    goToDetail() {
      this.$router.push({ name: 'AdminLostItemDetail', params: { id: this.itemId }})
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  .form-card {
    max-width: 800px;
    margin: 0 auto;
  }
}
</style> 