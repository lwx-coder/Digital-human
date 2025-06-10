<template>
  <div class="app-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="user-card">
          <div class="user-header">
            <div class="avatar-container">
              <div class="avatar-wrapper">
                <img 
                  :src="imageUrl || (userInfo.avatar ? userInfo.avatar : defaultAvatar)" 
                  class="user-avatar"
                  @click="$refs.avatarInput.click()"
                  alt="用户头像"
                />
                <input 
                  ref="avatarInput" 
                  type="file" 
                  class="avatar-input" 
                  accept="image/jpeg,image/png" 
                  @change="handleAvatarUpload"
                />
                <el-button size="mini" type="primary" class="avatar-upload-btn" @click="$refs.avatarInput.click()">
                  <i class="el-icon-upload"></i>更换头像
                </el-button>
              </div>
            </div>
            <div class="user-name">{{ userInfo.name || userInfo.username }}</div>
            <div class="user-role">
              <el-tag v-for="role in userInfo.roles" :key="role" size="small" style="margin-right: 5px">
                {{ getRoleDisplay(role) }}
              </el-tag>
            </div>
          </div>
          <div class="user-info">
            <div v-if="userInfo.introduction" class="info-item">
              <div class="label">简介:</div>
              <div class="value">{{ userInfo.introduction }}</div>
            </div>
            <div v-if="userInfo.email" class="info-item">
              <div class="label">邮箱:</div>
              <div class="value">{{ userInfo.email }}</div>
            </div>
            <div v-if="userInfo.phone" class="info-item">
              <div class="label">电话:</div>
              <div class="value">{{ userInfo.phone }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="18">
        <el-card shadow="hover">
          <div slot="header" class="clearfix">
            <span>个人信息</span>
            <el-button style="float: right; padding: 3px 0" type="text" @click="showUpdateDialog">编辑资料</el-button>
          </div>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="基本信息" name="basic">
              <el-form label-position="left" label-width="100px" class="user-form">
                <el-form-item label="用户名">
                  <span>{{ userInfo.username }}</span>
                </el-form-item>
                <el-form-item label="姓名">
                  <span>{{ userInfo.first_name || '' }} {{ userInfo.last_name || '' }}</span>
                </el-form-item>
                <el-form-item label="邮箱">
                  <span>{{ userInfo.email || '未设置' }}</span>
                </el-form-item>
                <el-form-item label="手机号码">
                  <span>{{ userInfo.phone || '未设置' }}</span>
                </el-form-item>
                <el-form-item label="地址">
                  <span>{{ userInfo.address || '未设置' }}</span>
                </el-form-item>
                <el-form-item label="生日">
                  <span>{{ userInfo.birth_date || '未设置' }}</span>
                </el-form-item>
                <el-form-item label="注册时间">
                  <span>{{ formatTime(userInfo.date_joined) }}</span>
                </el-form-item>
                <el-form-item label="最后登录">
                  <span>{{ formatTime(userInfo.last_login) }}</span>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            <el-tab-pane label="安全设置" name="security">
              <el-form label-position="left" label-width="100px" class="security-form">
                <el-form-item label="修改密码">
                  <el-button type="primary" size="small" @click="showChangePasswordDialog">修改密码</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            <el-tab-pane v-if="isPassenger" label="更多信息" name="more">
              <div class="more-info">
                <el-alert
                  title="您可以在个人资料页面查看和编辑更多旅客信息"
                  type="info"
                  :closable="false"
                >
                  <template slot="title">
                    <div>您可以在旅客个人资料页面查看和编辑更多旅客相关信息</div>
                  </template>
                  <el-button type="primary" size="small" @click="goToPassengerProfile">前往旅客资料</el-button>
                </el-alert>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <!-- 编辑个人信息对话框 -->
    <el-dialog title="编辑个人信息" :visible.sync="updateDialogVisible" width="500px">
      <el-form :model="updateForm" label-width="100px" :rules="rules" ref="updateForm">
        <el-form-item label="姓" prop="first_name">
          <el-input v-model="updateForm.first_name" placeholder="请输入姓" />
        </el-form-item>
        <el-form-item label="名" prop="last_name">
          <el-input v-model="updateForm.last_name" placeholder="请输入名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="updateForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="updateForm.phone" placeholder="请输入手机号码" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="updateForm.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="出生日期" prop="birth_date">
          <el-date-picker
            v-model="updateForm.birth_date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="yyyy-MM-dd"
          />
        </el-form-item>
        <el-form-item label="个人简介" prop="bio">
          <el-input
            v-model="updateForm.bio"
            type="textarea"
            :rows="3"
            placeholder="请输入个人简介"
          />
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="updateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUpdateForm">确定</el-button>
      </span>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog title="修改密码" :visible.sync="passwordDialogVisible" width="500px">
      <el-form :model="passwordForm" label-width="120px" :rules="passwordRules" ref="passwordForm">
        <el-form-item label="当前密码" prop="old_password">
          <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入当前密码" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPasswordForm">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { parseTime } from '@/utils'
import { getToken } from '@/utils/auth'
import { getUserDetail, updateUserInfo, changePassword, uploadAvatar } from '@/api/user'

export default {
  name: 'Profile',
  data() {
    // 确认密码的验证规则
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.passwordForm.new_password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    return {
      userInfo: {},
      defaultAvatar: require('@/assets/avatar.png'),
      activeTab: 'basic',
      
      // 编辑资料相关
      updateDialogVisible: false,
      updateForm: {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        address: '',
        birth_date: '',
        bio: ''
      },
      
      // 表单验证规则
      rules: {
        email: [
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        phone: [
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
        ]
      },
      
      // 密码修改相关
      passwordDialogVisible: false,
      passwordForm: {
        old_password: '',
        new_password: '',
        confirm_password: ''
      },
      passwordRules: {
        old_password: [
          { required: true, message: '请输入当前密码', trigger: 'blur' }
        ],
        new_password: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
        ],
        confirm_password: [
          { required: true, message: '请再次输入新密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      },
      
      // 上传相关
      headers: {
        Authorization: `Bearer ${getToken()}`
      },
      avatarUrl: '',
      imageUrl: ''
    }
  },
  computed: {
    isPassenger() {
      return this.userInfo.roles && this.userInfo.roles.includes('passenger')
    }
  },
  created() {
    this.fetchUserInfo()
  },
  methods: {
    formatTime(time) {
      if (time) {
        return parseTime(time)
      }
      return '未知'
    },
    fetchUserInfo() {
      getUserDetail().then(response => {
        console.log('获取用户信息响应:', response)
        this.userInfo = response
        
        // 更新Vuex中的用户信息
        if (response.avatar) {
          console.log('更新Vuex头像:', response.avatar)
          this.$store.commit('user/SET_AVATAR', response.avatar)
        } else {
          console.log('用户没有头像')
        }
        
        // 初始化表单数据
        this.updateForm = {
          first_name: response.first_name || '',
          last_name: response.last_name || '',
          email: response.email || '',
          phone: response.phone || '',
          address: response.address || '',
          birth_date: response.birth_date || '',
          bio: response.bio || ''
        }
      }).catch(error => {
        console.error('获取用户信息失败:', error)
        this.$message.error('获取用户信息失败')
      })
    },
    showUpdateDialog() {
      this.updateDialogVisible = true
    },
    submitUpdateForm() {
      this.$refs.updateForm.validate(valid => {
        if (valid) {
          updateUserInfo(this.updateForm).then(() => {
            this.$message.success('个人信息更新成功')
            this.updateDialogVisible = false
            this.fetchUserInfo()
          }).catch(() => {
            this.$message.error('个人信息更新失败')
          })
        }
      })
    },
    showChangePasswordDialog() {
      this.passwordForm = {
        old_password: '',
        new_password: '',
        confirm_password: ''
      }
      this.passwordDialogVisible = true
    },
    submitPasswordForm() {
      this.$refs.passwordForm.validate(valid => {
        if (valid) {
          changePassword(this.passwordForm).then(() => {
            this.$message.success('密码修改成功')
            this.passwordDialogVisible = false
          }).catch(error => {
            this.$message.error(error.response?.data?.detail || '密码修改失败')
          })
        }
      })
    },
    handleAvatarSuccess(res) {
      console.log('上传头像响应:', res)
      if (res.success) {
        // 确保avatar_url存在并且是一个有效的URL
        if (res.avatar_url) {
          console.log('设置新头像URL:', res.avatar_url)
          this.userInfo.avatar = res.avatar_url
          // 更新Vuex存储的头像
          this.$store.commit('user/SET_AVATAR', res.avatar_url)
          this.$message.success('头像上传成功')
          
          // 清除本地预览
          this.imageUrl = ''
          
          // 刷新用户信息
          this.fetchUserInfo()
        } else {
          console.error('头像URL不存在:', res)
          this.$message.error('获取头像URL失败')
        }
      } else {
        console.error('上传头像失败:', res)
        this.$message.error(res.message || '头像上传失败')
      }
    },
    beforeAvatarUpload(file) {
      const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
      const isLt2M = file.size / 1024 / 1024 < 2

      if (!isJPG) {
        this.$message.error('上传头像图片只能是 JPG 或 PNG 格式!')
      }
      if (!isLt2M) {
        this.$message.error('上传头像图片大小不能超过 2MB!')
      }
      return isJPG && isLt2M
    },
    handleAvatarUpload(e) {
      const file = e.target.files[0]
      if (!file) return
      
      // 先验证文件
      const isValidFile = this.beforeAvatarUpload(file)
      if (!isValidFile) return
      
      // 本地预览
      this.imageUrl = URL.createObjectURL(file)
      
      // 上传头像
      uploadAvatar(file).then(response => {
        this.handleAvatarSuccess(response)
      }).catch(error => {
        this.$message.error('头像上传失败：' + (error.message || '未知错误'))
      })
    },
    goToPassengerProfile() {
      this.$router.push('/passenger-management/passenger/profile')
    },
    getRoleDisplay(role) {
      const roleMap = {
        'admin': '管理员',
        'passenger': '旅客'
      }
      return roleMap[role] || role
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
  
  .user-card {
    .user-header {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding-bottom: 20px;
      border-bottom: 1px solid #ebeef5;
      
      .avatar-container {
        text-align: center;
        margin-bottom: 15px;
        
        .avatar-input {
          display: none;
        }
        
        .avatar-wrapper {
          position: relative;
          display: inline-block;
          
          .user-avatar {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            object-fit: contain;
            cursor: pointer;
            border: 2px solid #f0f0f0;
            transition: all 0.3s;
            
            &:hover {
              border-color: #409EFF;
              transform: scale(1.02);
            }
          }
          
          .avatar-upload-btn {
            margin-top: 10px;
            
            i {
              margin-right: 5px;
            }
          }
        }
      }
      
      .user-name {
        font-size: 20px;
        font-weight: bold;
        margin: 10px 0;
      }
      
      .user-role {
        margin-bottom: 10px;
      }
    }
    
    .user-info {
      margin-top: 20px;
      
      .info-item {
        margin-bottom: 15px;
        
        .label {
          color: #606266;
          font-weight: bold;
          margin-bottom: 5px;
        }
        
        .value {
          color: #303133;
        }
      }
    }
  }
  
  .user-form {
    padding: 20px;
    
    .el-form-item {
      margin-bottom: 22px;
    }
  }
  
  .security-form {
    padding: 20px;
  }
  
  .more-info {
    padding: 20px;
  }
}

.avatar-container {
  text-align: center;
  margin-bottom: 15px;
  
  .avatar-wrapper {
    position: relative;
    display: inline-block;
    
    .user-avatar {
      width: 100px;
      height: 100px;
      border-radius: 50%;
      object-fit: contain;
      cursor: pointer;
      border: 2px solid #f0f0f0;
      transition: all 0.3s;
      
      &:hover {
        border-color: #409EFF;
        transform: scale(1.02);
      }
    }
    
    .avatar-upload-btn {
      margin-top: 10px;
      
      i {
        margin-right: 5px;
      }
    }
  }
}
</style> 