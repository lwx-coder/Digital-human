<template>
  <div class="app-container">
    <el-card v-loading="loading">
      <div slot="header" class="clearfix">
        <span>旅客详情</span>
        <el-button style="float: right; margin-left: 10px" type="primary" size="small" @click="goBack">
          返回列表
        </el-button>
      </div>

      <el-row :gutter="20" v-if="passenger">
        <!-- 基本信息 -->
        <el-col :span="8">
          <div class="passenger-card">
            <div class="user-header">
              <el-avatar :size="80" :src="passenger.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
              <h3>{{ passenger.username }}</h3>
              <div>
                <el-tag v-for="role in passenger.roles" :key="role" type="success" style="margin-right: 5px">
                  {{ role === 'admin' ? '管理员' : role === 'passenger' ? '旅客' : role }}
                </el-tag>
              </div>
            </div>

            <el-divider content-position="left">基本信息</el-divider>
            <div class="info-item">
              <span class="label">注册日期:</span>
              <span class="value">{{ passenger.date_joined | parseTime }}</span>
            </div>
            <div class="info-item">
              <span class="label">上次登录:</span>
              <span class="value">{{ passenger.last_login | parseTime || '从未登录' }}</span>
            </div>
            <div class="info-item">
              <span class="label">姓名:</span>
              <span class="value">{{ (passenger.first_name || '') + (passenger.last_name || '') || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">邮箱:</span>
              <span class="value">{{ passenger.email || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">电话:</span>
              <span class="value">{{ passenger.phone || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">地址:</span>
              <span class="value">{{ passenger.address || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">生日:</span>
              <span class="value">{{ passenger.birth_date || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">账户状态:</span>
              <span class="value">
                <el-tag :type="passenger.is_active ? 'success' : 'danger'">
                  {{ passenger.is_active ? '激活' : '未激活' }}
                </el-tag>
              </span>
            </div>
          </div>
        </el-col>

        <!-- 扩展资料 -->
        <el-col :span="8">
          <div class="passenger-card">
            <h3>扩展资料</h3>
            <el-divider></el-divider>
            <div v-if="passenger.profile">
              <div class="info-item">
                <span class="label">VIP等级:</span>
                <span class="value">
                  <el-rate v-model="passenger.profile.vip_level" disabled text-color="#ff9900" :max="5"></el-rate>
                </span>
              </div>
              <div class="info-item">
                <span class="label">常旅客号:</span>
                <span class="value">{{ passenger.profile.frequent_flyer_number || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">护照号码:</span>
                <span class="value">{{ passenger.profile.passport_number || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">身份证号:</span>
                <span class="value">{{ passenger.profile.id_card_number || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">紧急联系人:</span>
                <span class="value">{{ passenger.profile.emergency_contact || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">紧急电话:</span>
                <span class="value">{{ passenger.profile.emergency_phone || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">上次登录IP:</span>
                <span class="value">{{ passenger.profile.last_login_ip || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">标签:</span>
                <span class="value">
                  <el-tag
                    v-for="tag in passenger.profile.tags"
                    :key="tag.id"
                    :color="tag.color"
                    style="margin-right: 5px; margin-bottom: 5px;"
                  >
                    {{ tag.name }}
                  </el-tag>
                  <span v-if="!passenger.profile.tags || passenger.profile.tags.length === 0">-</span>
                </span>
              </div>
            </div>
            <div v-else>
              <el-empty description="暂无扩展资料"></el-empty>
            </div>

            <div style="margin-top: 20px">
              <el-button type="primary" @click="handleEditProfile">编辑资料</el-button>
            </div>
          </div>
        </el-col>

        <!-- 备注与活动 -->
        <el-col :span="8">
          <div class="passenger-card">
            <div class="card-header">
              <h3>旅客备注</h3>
              <el-button type="success" size="small" @click="handleAddNote">添加备注</el-button>
            </div>
            <el-divider></el-divider>
            <div v-if="passenger.recent_notes && passenger.recent_notes.length > 0">
              <div v-for="note in passenger.recent_notes" :key="note.id" class="note-item">
                <div class="note-content">{{ note.note }}</div>
                <div class="note-footer">
                  <span>{{ note.created_by_username }}</span>
                  <span>{{ note.created_at | parseTime }}</span>
                </div>
              </div>
              <div class="view-more" v-if="passenger.recent_notes.length >= 5">
                <el-button type="text" @click="viewAllNotes">查看全部备注</el-button>
              </div>
            </div>
            <el-empty v-else description="暂无备注"></el-empty>

            <h3 style="margin-top: 30px">最近活动</h3>
            <el-divider></el-divider>
            <div v-if="passenger.recent_activities && passenger.recent_activities.length > 0">
              <el-timeline>
                <el-timeline-item
                  v-for="activity in passenger.recent_activities"
                  :key="activity.id"
                  :timestamp="activity.created_at | parseTime"
                  placement="top"
                >
                  <el-card shadow="hover" size="small">
                    <span>{{ activity.activity_type_display }}: {{ activity.description }}</span>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
              <div class="view-more" v-if="passenger.recent_activities.length >= 10">
                <el-button type="text" @click="viewAllActivities">查看全部活动</el-button>
              </div>
            </div>
            <el-empty v-else description="暂无活动记录"></el-empty>
          </div>
        </el-col>
      </el-row>

      <!-- 失物列表 -->
      <el-row v-if="passenger && passenger.recent_lost_items">
        <el-col :span="24">
          <div class="passenger-card">
            <div class="card-header">
              <h3>失物记录</h3>
              <el-button type="primary" size="small" @click="viewAllLostItems">查看全部</el-button>
            </div>
            <el-divider></el-divider>
            <div v-if="passenger.recent_lost_items.length > 0">
              <el-table :data="passenger.recent_lost_items" style="width: 100%">
                <el-table-column prop="id" label="ID" width="80"></el-table-column>
                <el-table-column prop="item_name" label="物品名称"></el-table-column>
                <el-table-column prop="lost_location" label="丢失地点"></el-table-column>
                <el-table-column prop="lost_time" label="丢失时间">
                  <template slot-scope="{row}">
                    {{ row.lost_time | parseTime }}
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="处理状态">
                  <template slot-scope="{row}">
                    <el-tag :type="getStatusType(row.status)">{{ row.status_display }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="120">
                  <template slot-scope="{row}">
                    <el-button type="text" @click="viewLostItemDetail(row.id)">查看详情</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <el-empty v-else description="暂无失物记录"></el-empty>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 添加备注对话框 -->
    <el-dialog title="添加旅客备注" :visible.sync="noteDialogVisible" width="500px">
      <el-form ref="noteForm" :model="noteForm" :rules="noteRules" label-width="80px">
        <el-form-item label="备注内容" prop="note">
          <el-input
            v-model="noteForm.note"
            type="textarea"
            :rows="4"
            placeholder="请输入备注内容..."
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="noteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitNoteForm">确认</el-button>
      </div>
    </el-dialog>

    <!-- 编辑资料对话框 -->
    <el-dialog title="编辑旅客资料" :visible.sync="profileDialogVisible" width="700px">
      <el-form ref="profileForm" :model="profileForm" :rules="profileRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="VIP等级" prop="vip_level">
              <el-rate v-model="profileForm.vip_level" :max="5" show-score></el-rate>
            </el-form-item>
            <el-form-item label="常旅客号" prop="frequent_flyer_number">
              <el-input v-model="profileForm.frequent_flyer_number"></el-input>
            </el-form-item>
            <el-form-item label="护照号码" prop="passport_number">
              <el-input v-model="profileForm.passport_number"></el-input>
            </el-form-item>
            <el-form-item label="身份证号" prop="id_card_number">
              <el-input v-model="profileForm.id_card_number"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="紧急联系人" prop="emergency_contact">
              <el-input v-model="profileForm.emergency_contact"></el-input>
            </el-form-item>
            <el-form-item label="紧急电话" prop="emergency_phone">
              <el-input v-model="profileForm.emergency_phone"></el-input>
            </el-form-item>
            <el-form-item label="标签" prop="tag_ids">
              <el-select v-model="profileForm.tag_ids" multiple placeholder="请选择标签" style="width: 100%">
                <el-option
                  v-for="item in tagOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                >
                  <el-tag :color="item.color" style="margin-right: 10px">{{ item.name }}</el-tag>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="profileDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitProfileForm">确认</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getPassengerDetail, addPassengerNote, getPassengerTags, updatePassengerProfile } from '@/api/passenger'
import { parseTime } from '@/utils'

export default {
  name: 'PassengerDetail',
  data() {
    return {
      loading: true,
      passenger: null,
      noteDialogVisible: false,
      noteForm: {
        note: ''
      },
      profileDialogVisible: false,
      profileForm: {
        vip_level: 0,
        frequent_flyer_number: '',
        passport_number: '',
        id_card_number: '',
        emergency_contact: '',
        emergency_phone: '',
        tag_ids: []
      },
      tagOptions: [],
      noteRules: {
        note: [{ required: true, message: '请输入备注内容', trigger: 'blur' }]
      },
      profileRules: {
        id_card_number: [
          { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号码', trigger: 'blur' }
        ],
        emergency_phone: [
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
        ]
      }
    }
  },
  created() {
    this.getDetail()
    this.getTags()
  },
  methods: {
    getDetail() {
      this.loading = true
      const id = this.$route.params.id
      getPassengerDetail(id).then(response => {
        this.passenger = response
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    getTags() {
      getPassengerTags().then(response => {
        this.tagOptions = response.results || response
      })
    },
    goBack() {
      this.$router.push('/passenger-management/list')
    },
    handleAddNote() {
      this.noteForm.note = ''
      this.noteDialogVisible = true
      this.$nextTick(() => {
        this.$refs.noteForm && this.$refs.noteForm.clearValidate()
      })
    },
    submitNoteForm() {
      this.$refs.noteForm.validate(valid => {
        if (valid) {
          const data = {
            note: this.noteForm.note
          }
          const id = this.$route.params.id
          addPassengerNote(id, data).then(() => {
            this.$message({
              type: 'success',
              message: '添加备注成功!'
            })
            this.noteDialogVisible = false
            this.getDetail() // 刷新数据
          })
        }
      })
    },
    handleEditProfile() {
      const profile = this.passenger.profile || {}
      this.profileForm = {
        vip_level: parseInt(profile.vip_level || 0, 10),
        frequent_flyer_number: profile.frequent_flyer_number || '',
        passport_number: profile.passport_number || '',
        id_card_number: profile.id_card_number || '',
        emergency_contact: profile.emergency_contact || '',
        emergency_phone: profile.emergency_phone || '',
        tag_ids: profile.tags ? profile.tags.map(tag => tag.id) : []
      }
      this.profileDialogVisible = true
    },
    submitProfileForm() {
      this.$refs.profileForm.validate(valid => {
        if (valid) {
          const id = this.$route.params.id
          const data = {
            ...this.profileForm,
            passenger: id
          }
          
          console.log('更新资料数据:', data)
          
          updatePassengerProfile(id, data).then(() => {
            this.$message({
              type: 'success',
              message: '资料更新成功!'
            })
            this.profileDialogVisible = false
            this.getDetail() // 刷新数据
          }).catch(error => {
            console.error('更新资料失败:', error.response?.data || error)
            this.$message({
              type: 'error',
              message: '资料更新失败，请检查信息是否正确'
            })
          })
        }
      })
    },
    viewAllNotes() {
      // 可以跳转到备注列表页面或者打开更大的弹窗显示所有备注
      this.$message.info('功能待实现: 查看全部备注')
    },
    viewAllActivities() {
      // 跳转到活动记录页面
      const id = this.$route.params.id
      this.$router.push(`/passenger-management/activities?passenger=${id}`)
    },
    viewAllLostItems() {
      // 可以跳转到失物列表页面，并且预设筛选条件为当前旅客
      this.$message.info('功能待实现: 查看全部失物记录')
    },
    viewLostItemDetail(id) {
      // 可以跳转到失物详情页面
      this.$router.push(`/lost-item/admin/detail/${id}`)
    },
    getStatusType(status) {
      const statusMap = {
        'pending': 'info',
        'processing': 'warning',
        'found': 'success',
        'closed': 'danger'
      }
      return statusMap[status] || 'info'
    }
  }
}
</script>

<style lang="scss" scoped>
.passenger-card {
  margin-bottom: 20px;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: #fff;

  .user-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 20px;
    h3 {
      margin: 10px 0;
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    h3 {
      margin: 0;
    }
  }

  .info-item {
    display: flex;
    margin-bottom: 10px;

    .label {
      width: 80px;
      color: #909399;
    }

    .value {
      flex: 1;
      color: #303133;
    }
  }

  .note-item {
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 4px;
    background-color: #f9f9f9;

    .note-content {
      margin-bottom: 5px;
    }

    .note-footer {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: #909399;
    }
  }

  .view-more {
    text-align: center;
    padding: 10px 0;
  }
}
</style> 