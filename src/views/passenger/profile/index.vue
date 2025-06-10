<template>
  <div class="app-container">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    <div v-else>
      <!-- 旅客个人信息卡片 -->
      <el-card class="box-card" shadow="hover">
        <div slot="header" class="clearfix">
          <span>个人信息</span>
          <el-button
            style="float: right; padding: 3px 0"
            type="text"
            @click="updateDialogVisible = true"
          >编辑资料</el-button>
        </div>
        <div class="passenger-info">
          <div class="avatar-container">
            <el-avatar :size="100" :src="userInfo.avatar || defaultAvatar"></el-avatar>
            <el-upload
              class="avatar-uploader"
              action="/api/users/upload_avatar/"
              :headers="headers"
              :show-file-list="false"
              :on-success="handleAvatarSuccess"
              :before-upload="beforeAvatarUpload"
            >
              <el-button size="mini" type="primary" plain>更换头像</el-button>
            </el-upload>
          </div>
          <div class="info-container">
            <div class="info-item">
              <div class="label">用户名:</div>
              <div class="value">{{ userInfo.username }}</div>
            </div>
            <div class="info-item">
              <div class="label">姓名:</div>
              <div class="value">{{ userInfo.first_name }} {{ userInfo.last_name }}</div>
            </div>
            <div class="info-item">
              <div class="label">邮箱:</div>
              <div class="value">{{ userInfo.email || '未设置' }}</div>
            </div>
            <div class="info-item">
              <div class="label">手机:</div>
              <div class="value">{{ userInfo.phone || '未设置' }}</div>
            </div>
            <div class="info-item">
              <div class="label">地址:</div>
              <div class="value">{{ userInfo.address || '未设置' }}</div>
            </div>
            <div class="info-item">
              <div class="label">生日:</div>
              <div class="value">{{ userInfo.birth_date || '未设置' }}</div>
            </div>
          </div>
          <div class="tag-container">
            <div class="info-item">
              <div class="label">我的标签:</div>
              <div class="value">
                <el-tag
                  v-for="tag in profileData.tags"
                  :key="tag.id"
                  size="small"
                  :style="{ backgroundColor: tag.color, color: '#fff', marginRight: '5px' }"
                >{{ tag.name }}</el-tag>
              </div>
            </div>
            <div class="info-item" v-if="profileData.vip_level > 0">
              <div class="label">VIP等级:</div>
              <div class="value">
                <el-rate
                  v-model="profileData.vip_level"
                  disabled
                  show-score
                  text-color="#ff9900"
                  score-template="{value} 级"
                ></el-rate>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 旅客扩展资料卡片 -->
      <el-card class="box-card" shadow="hover">
        <div slot="header" class="clearfix">
          <span>旅行信息</span>
        </div>
        <div class="profile-container">
          <div class="profile-item" v-if="profileData.frequent_flyer_number">
            <div class="label">常旅客号码:</div>
            <div class="value">{{ profileData.frequent_flyer_number }}</div>
          </div>
          <div class="profile-item" v-if="profileData.passport_number">
            <div class="label">护照号码:</div>
            <div class="value">{{ profileData.passport_number }}</div>
          </div>
          <div class="profile-item" v-if="profileData.id_card_number">
            <div class="label">身份证号码:</div>
            <div class="value">{{ profileData.id_card_number }}</div>
          </div>
          <div class="profile-item" v-if="profileData.emergency_contact">
            <div class="label">紧急联系人:</div>
            <div class="value">{{ profileData.emergency_contact }}</div>
          </div>
          <div class="profile-item" v-if="profileData.emergency_phone">
            <div class="label">紧急联系电话:</div>
            <div class="value">{{ profileData.emergency_phone }}</div>
          </div>
          <el-empty v-if="!hasProfileData" description="暂无旅行信息">
            <el-button type="primary" @click="profileDialogVisible = true">填写旅行信息</el-button>
          </el-empty>
        </div>
      </el-card>

      <!-- 活动记录标签页 -->
      <el-card class="box-card" shadow="hover">
        <div slot="header" class="clearfix">
          <span>我的活动</span>
        </div>
        <el-tabs v-model="activeTab" type="card">
          <el-tab-pane label="活动记录" name="activities">
            <div class="filter-bar">
              <el-select v-model="activityFilter" placeholder="筛选活动类型" clearable @change="fetchActivities">
                <el-option
                  v-for="item in activityTypes"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </div>
            <el-timeline>
              <el-timeline-item
                v-for="activity in activities"
                :key="activity.id"
                :timestamp="formatTime(activity.created_at)"
                :type="getActivityType(activity.activity_type)"
              >
                <el-card shadow="hover">
                  <h4>{{ activity.activity_type_display }}</h4>
                  <p>{{ activity.description }}</p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <div class="load-more" v-if="activities.length > 0">
              <el-button type="text" @click="loadMoreActivities">加载更多</el-button>
            </div>
            <el-empty v-if="activities.length === 0" description="暂无活动记录" />
          </el-tab-pane>
          <el-tab-pane label="我的失物" name="lost_items">
            <el-table :data="lostItems" border style="width: 100%">
              <el-table-column prop="name" label="物品名称" />
              <el-table-column prop="category_name" label="物品类别" width="120" />
              <el-table-column prop="status_display" label="状态" width="120">
                <template slot-scope="scope">
                  <el-tag :type="getLostItemStatusType(scope.row.status)">
                    {{ scope.row.status_display }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="report_date" label="报失时间" width="180">
                <template slot-scope="scope">
                  {{ formatTime(scope.row.report_date) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" align="center">
                <template slot-scope="scope">
                  <el-button
                    size="mini"
                    type="primary"
                    @click="viewLostItemDetail(scope.row.id)"
                  >查看</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-if="lostItems.length === 0" description="暂无失物记录" />
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>

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

    <!-- 编辑旅行信息对话框 -->
    <el-dialog title="编辑旅行信息" :visible.sync="profileDialogVisible" width="500px">
      <el-form :model="profileForm" label-width="120px">
        <el-form-item label="常旅客号码">
          <el-input v-model="profileForm.frequent_flyer_number" placeholder="请输入常旅客号码" />
        </el-form-item>
        <el-form-item label="护照号码">
          <el-input v-model="profileForm.passport_number" placeholder="请输入护照号码" />
        </el-form-item>
        <el-form-item label="身份证号码">
          <el-input v-model="profileForm.id_card_number" placeholder="请输入身份证号码" />
        </el-form-item>
        <el-form-item label="紧急联系人">
          <el-input v-model="profileForm.emergency_contact" placeholder="请输入紧急联系人" />
        </el-form-item>
        <el-form-item label="紧急联系电话">
          <el-input v-model="profileForm.emergency_phone" placeholder="请输入紧急联系电话" />
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="profileDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitProfileForm">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { parseTime } from '@/utils'
import { getToken } from '@/utils/auth'
import { getUserDetail, updateUserInfo } from '@/api/user'
import { 
  getPassengerActivities,
  getPassengerLostItems,
  getPassengerProfile,
  updatePassengerProfile
} from '@/api/passenger'

export default {
  name: 'PassengerProfile',
  data() {
    return {
      loading: true,
      userInfo: {},
      profileData: {
        tags: []
      },
      defaultAvatar: require('@/assets/avatar.png'),
      
      // 标签页相关
      activeTab: 'activities',
      
      // 活动记录相关
      activities: [],
      activityPage: 1,
      activityFilter: '',
      activityTypes: [
        { value: 'login', label: '登录' },
        { value: 'logout', label: '登出' },
        { value: 'profile_update', label: '更新个人信息' },
        { value: 'flight_booking', label: '航班预订' },
        { value: 'flight_checkin', label: '航班值机' },
        { value: 'lost_item_report', label: '物品报失' },
        { value: 'other', label: '其他' }
      ],
      
      // 失物记录相关
      lostItems: [],
      
      // 编辑资料相关
      updateDialogVisible: false,
      profileDialogVisible: false,
      updateForm: {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        address: '',
        birth_date: '',
        bio: ''
      },
      profileForm: {
        frequent_flyer_number: '',
        passport_number: '',
        id_card_number: '',
        emergency_contact: '',
        emergency_phone: ''
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
      
      // 上传相关
      headers: {
        Authorization: `Bearer ${getToken()}`
      }
    }
  },
  computed: {
    hasProfileData() {
      return this.profileData.frequent_flyer_number || 
        this.profileData.passport_number || 
        this.profileData.id_card_number || 
        this.profileData.emergency_contact ||
        this.profileData.emergency_phone
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    formatTime(time) {
      if (time) {
        return parseTime(time)
      }
      return '未知'
    },
    fetchData() {
      this.loading = true
      
      // 获取用户详情
      getUserDetail().then(response => {
        this.userInfo = response
        
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
        
        // 获取旅客资料
        return getPassengerProfile(response.id)
      }).then(response => {
        this.profileData = response
        
        // 初始化旅行信息表单
        this.profileForm = {
          frequent_flyer_number: response.frequent_flyer_number || '',
          passport_number: response.passport_number || '',
          id_card_number: response.id_card_number || '',
          emergency_contact: response.emergency_contact || '',
          emergency_phone: response.emergency_phone || ''
        }
        
        // 获取活动记录
        return this.fetchActivities()
      }).then(() => {
        // 获取失物记录
        return getPassengerLostItems(this.userInfo.id)
      }).then(response => {
        this.lostItems = response
        this.loading = false
      }).catch(error => {
        console.error('获取用户信息失败:', error)
        this.$message.error('获取用户信息失败')
        this.loading = false
      })
    },
    fetchActivities() {
      const params = {
        page: this.activityPage,
        type: this.activityFilter
      }
      
      return getPassengerActivities(this.userInfo.id, params).then(response => {
        if (this.activityPage === 1) {
          this.activities = response
        } else {
          this.activities = [...this.activities, ...response]
        }
      }).catch(() => {
        this.$message.error('获取活动记录失败')
      })
    },
    loadMoreActivities() {
      this.activityPage += 1
      this.fetchActivities()
    },
    getActivityType(type) {
      const typeMap = {
        login: 'success',
        logout: 'info',
        profile_update: 'warning',
        flight_booking: 'primary',
        flight_checkin: 'success',
        lost_item_report: 'danger'
      }
      return typeMap[type] || 'info'
    },
    getLostItemStatusType(status) {
      const statusMap = {
        pending: 'warning',
        found: 'success',
        returned: 'primary',
        closed: 'info'
      }
      return statusMap[status] || 'info'
    },
    viewLostItemDetail(id) {
      this.$router.push({ path: `/passenger/lost-item/detail/${id}` })
    },
    submitUpdateForm() {
      this.$refs.updateForm.validate(valid => {
        if (valid) {
          updateUserInfo(this.updateForm).then(() => {
            this.$message.success('个人信息更新成功')
            this.updateDialogVisible = false
            
            // 刷新用户信息
            getUserDetail().then(response => {
              this.userInfo = response
            })
          }).catch(() => {
            this.$message.error('个人信息更新失败')
          })
        }
      })
    },
    submitProfileForm() {
      updatePassengerProfile(this.userInfo.id, this.profileForm).then(() => {
        this.$message.success('旅行信息更新成功')
        this.profileDialogVisible = false
        
        // 刷新资料
        getPassengerProfile(this.userInfo.id).then(response => {
          this.profileData = response
        })
      }).catch(() => {
        this.$message.error('旅行信息更新失败')
      })
    },
    handleAvatarSuccess(res) {
      if (res.success) {
        this.userInfo.avatar = res.avatar_url
        this.$message.success('头像上传成功')
      } else {
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
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding-bottom: 50px;
}

.box-card {
  margin-bottom: 20px;
}

.passenger-info {
  display: flex;
  flex-wrap: wrap;
  
  .avatar-container {
    width: 120px;
    text-align: center;
    margin-right: 40px;
    
    .avatar-uploader {
      margin-top: 10px;
    }
  }
  
  .info-container {
    flex: 1;
    min-width: 300px;
  }
  
  .tag-container {
    flex: 1;
    min-width: 300px;
  }
}

.info-item, .profile-item {
  margin-bottom: 15px;
  display: flex;
  
  .label {
    width: 120px;
    color: #606266;
    font-weight: bold;
  }
  
  .value {
    flex: 1;
  }
}

.profile-container {
  display: flex;
  flex-wrap: wrap;
  
  .profile-item {
    width: 50%;
    min-width: 300px;
  }
}

.filter-bar {
  margin-bottom: 20px;
}

.load-more {
  text-align: center;
  margin-top: 20px;
}

.loading-container {
  padding: 20px;
}
</style> 