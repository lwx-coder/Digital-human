<template>
  <div class="auth-container forget-pwd-container">
    <div class="auth-box forget-pwd-box">
      <div class="auth-header forget-pwd-header">
        <h2 class="title">找回密码</h2>
        <p class="subtitle">请填写邮箱信息以重置密码</p>
      </div>

      <el-steps :active="active" finish-status="success" simple class="steps">
        <el-step title="验证身份"></el-step>
        <el-step title="重置密码"></el-step>
        <el-step title="完成"></el-step>
      </el-steps>

      <!-- 步骤1：验证身份 -->
      <div v-if="active === 0">
        <el-form
          ref="verifyForm"
          :model="verifyForm"
          :rules="verifyRules"
          class="auth-form verify-form"
          label-position="top"
        >
          <el-form-item prop="email" label="邮箱">
            <el-input
              v-model="verifyForm.email"
              placeholder="请输入注册邮箱"
              prefix-icon="el-icon-message"
              clearable
            />
          </el-form-item>

          <el-form-item prop="code" label="验证码">
            <div class="code-input">
              <el-input
                v-model="verifyForm.code"
                placeholder="请输入验证码"
                prefix-icon="el-icon-key"
              />
              <el-button
                type="primary"
                class="code-button"
                :disabled="codeButtonDisabled"
                @click="handleSendCode"
              >{{ codeButtonText }}</el-button>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button
              :loading="loading"
              type="primary"
              class="primary-button submit-button"
              @click.native.prevent="handleVerify"
            >验证</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 步骤2：重置密码 -->
      <div v-if="active === 1">
        <el-form
          ref="resetForm"
          :model="resetForm"
          :rules="resetRules"
          class="auth-form reset-form"
          label-position="top"
        >
          <el-form-item prop="password" label="新密码">
            <el-input
              v-model="resetForm.password"
              :type="passwordType"
              placeholder="请输入新密码"
              prefix-icon="el-icon-lock"
            >
              <i
                slot="suffix"
                class="el-input__icon el-icon-view password-eye"
                @click="showPwd"
              />
            </el-input>
          </el-form-item>

          <el-form-item prop="confirmPassword" label="确认密码">
            <el-input
              v-model="resetForm.confirmPassword"
              :type="passwordType"
              placeholder="请再次输入新密码"
              prefix-icon="el-icon-lock"
            >
              <i
                slot="suffix"
                class="el-input__icon el-icon-view password-eye"
                @click="showPwd"
              />
            </el-input>
          </el-form-item>

          <el-form-item>
            <el-button
              :loading="loading"
              type="primary"
              class="primary-button submit-button"
              @click.native.prevent="handleReset"
            >重置密码</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 步骤3：完成 -->
      <div v-if="active === 2" class="success-page">
        <i class="el-icon-success success-icon"></i>
        <h3>密码重置成功</h3>
        <p>您的密码已重置，请使用新密码登录</p>
        <el-button type="primary" class="primary-button login-button" @click="goToLogin">立即登录</el-button>
      </div>

      <div class="auth-footer forget-pwd-footer">
        <p>遇到问题? <router-link to="/login" class="auth-link back-link">返回登录</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { resetPasswordRequest, resetPasswordConfirm } from '@/api/user'

export default {
  name: 'ForgetPassword',
  data() {
    // 校验密码一致性
    const validatePassword = (rule, value, callback) => {
      if (value !== this.resetForm.password) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }

    // 校验邮箱格式
    const validateEmail = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请输入邮箱'))
        return
      }

      // 邮箱格式验证
      const emailReg = /^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$/
      if (!emailReg.test(value)) {
        callback(new Error('请输入正确的邮箱格式'))
      } else {
        callback()
      }
    }

    return {
      active: 0, // 当前步骤
      // 验证表单
      verifyForm: {
        email: '',
        code: ''
      },
      // 重置密码表单
      resetForm: {
        email: '', // 存储邮箱，用于提交到后端
        code: '', // 存储验证码，用于提交到后端
        password: '',
        confirmPassword: ''
      },
      // 验证规则
      verifyRules: {
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { validator: validateEmail, trigger: 'blur' }
        ],
        code: [
          { required: true, message: '请输入验证码', trigger: 'blur' },
          { min: 4, max: 6, message: '验证码长度为4-6位', trigger: 'blur' }
        ]
      },
      // 重置密码规则
      resetRules: {
        password: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, max: 30, message: '长度在 6 到 30 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入新密码', trigger: 'blur' },
          { validator: validatePassword, trigger: 'blur' }
        ]
      },
      // 密码显示类型
      passwordType: 'password',
      // 加载状态
      loading: false,
      // 验证码按钮文字
      codeButtonText: '获取验证码',
      // 验证码按钮禁用状态
      codeButtonDisabled: false,
      // 计时器
      timer: null,
      // 倒计时
      countdown: 60
    }
  },
  methods: {
    // 显示密码
    showPwd() {
      this.passwordType = this.passwordType === 'password' ? '' : 'password'
    },
    // 发送验证码
    handleSendCode() {
      // 验证邮箱输入
      this.$refs.verifyForm.validateField('email', (error) => {
        if (!error) {
          this.loading = true
          // 发送邮箱验证码
          resetPasswordRequest({ email: this.verifyForm.email })
            .then(response => {
              this.startCountdown()
              this.$message.success('验证码已发送至您的邮箱')
              this.loading = false
            })
            .catch(error => {
              console.error('发送验证码失败:', error)
              this.$message.error(error.message || error.response?.data?.error || '验证码发送失败，请重试')
              this.loading = false
            })
        }
      })
    },
    // 开始倒计时
    startCountdown() {
      this.codeButtonDisabled = true
      this.codeButtonText = `${this.countdown}秒后重新获取`
      // 设置倒计时
      this.timer = setInterval(() => {
        this.countdown--
        this.codeButtonText = `${this.countdown}秒后重新获取`
        if (this.countdown <= 0) {
          clearInterval(this.timer)
          this.codeButtonDisabled = false
          this.codeButtonText = '获取验证码'
          this.countdown = 60
        }
      }, 1000)
    },
    // 验证身份
    handleVerify() {
      this.$refs.verifyForm.validate(valid => {
        if (!valid) return
        this.loading = true

        // 验证码固定为123456
        const isCodeValid = this.verifyForm.code === '123456'

        if (isCodeValid) {
          // 保存信息供重置密码使用
          this.resetForm.email = this.verifyForm.email
          this.resetForm.code = this.verifyForm.code

          // 进入下一步
          setTimeout(() => {
            this.loading = false
            this.active = 1
            this.$message.success('验证通过')
          }, 500)
        } else {
          this.loading = false
          this.$message.error('验证码错误，请重新输入')
        }
      })
    },
    // 重置密码
    handleReset() {
      this.$refs.resetForm.validate(valid => {
        if (!valid) return
        this.loading = true

        // 构建重置密码参数
        const resetData = {
          email: this.resetForm.email,
          code: this.resetForm.code,
          new_password: this.resetForm.password,
          new_password_confirm: this.resetForm.confirmPassword
        }

        // 调用重置密码API
        resetPasswordConfirm(resetData)
          .then(response => {
            this.$message.success('密码重置成功')
            this.loading = false
            this.active = 2
          })
          .catch(error => {
            console.error('重置密码失败:', error)
            this.$message.error(error.message || error.response?.data?.error || '重置密码失败，请重试')
            this.loading = false
          })
      })
    },
    // 跳转到登录页
    goToLogin() {
      this.$router.push('/login')
    }
  },
  // 组件销毁前清除计时器
  beforeDestroy() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  }
}
</script>

<style lang="scss" scoped>
@import "@/styles/auth-forms.scss";

.forget-pwd-container {
  .forget-pwd-box {
    .steps {
      margin: 20px 0 30px;
    }

    .code-input {
      display: flex;
      .el-input {
        flex: 1;
        margin-right: 10px;
      }
      .code-button {
        width: 120px;
      }
    }

    .success-page {
      text-align: center;
      padding: 30px 0;

      .success-icon {
        font-size: 70px;
        color: #67c23a;
        margin-bottom: 20px;
      }

      h3 {
        font-size: 24px;
        color: #303133;
        margin-bottom: 12px;
      }

      p {
        color: #606266;
        margin-bottom: 30px;
        font-size: 16px;
      }

      .login-button {
        width: 220px;
        height: 44px;
        font-size: 16px;
      }
    }
    
    .primary-button {
      width: 100%;
      height: 44px;
      font-size: 16px;
      margin-top: 10px;
    }
  }
}
</style> 