<template>
  <div class="auth-container login-container">
    <div class="auth-box login-box">
      <div class="auth-header login-header">
        <h2 class="title">智能数字人服务系统</h2>
        <p class="subtitle">机场旅客服务平台</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane name="account" label="账号密码登录">
          <transition name="fade" mode="out-in">
            <el-form
              ref="loginForm"
              :model="loginForm"
              :rules="loginRules"
              class="auth-form login-form"
              label-position="top"
            >
              <el-form-item prop="username" label="用户名">
                <el-input
                  ref="username"
                  v-model="loginForm.username"
                  placeholder="请输入用户名"
                  type="text"
                  prefix-icon="el-icon-user"
                  clearable
                />
              </el-form-item>

              <el-form-item prop="password" label="密码">
                <el-input
                  ref="password"
                  v-model="loginForm.password"
                  :type="passwordType"
                  placeholder="请输入密码"
                  prefix-icon="el-icon-lock"
                  @keyup.enter.native="handleLogin"
                >
                  <i
                    slot="suffix"
                    class="el-input__icon el-icon-view password-eye"
                    @click="showPwd"
                  />
                </el-input>
              </el-form-item>

              <div class="login-options">
                <el-checkbox v-model="rememberMe">记住我</el-checkbox>
                <router-link to="/forget-password" class="auth-link forget-password">忘记密码?</router-link>
              </div>

              <el-form-item>
                <el-button
                  :loading="loading"
                  type="primary"
                  class="primary-button login-button"
                  @click.native.prevent="handleLogin"
                >登录</el-button>
              </el-form-item>
            </el-form>
          </transition>
        </el-tab-pane>

        <el-tab-pane name="mobile" label="手机号登录">
          <transition name="fade" mode="out-in">
            <el-form
              ref="mobileForm"
              :model="mobileForm"
              :rules="mobileRules"
              class="auth-form login-form"
              label-position="top"
            >
              <el-form-item prop="mobile" label="手机号">
                <el-input
                  ref="mobile"
                  v-model="mobileForm.mobile"
                  placeholder="请输入手机号"
                  type="text"
                  prefix-icon="el-icon-mobile-phone"
                  clearable
                />
              </el-form-item>

              <el-form-item prop="code" label="验证码">
                <div class="code-input">
                  <el-input
                    ref="code"
                    v-model="mobileForm.code"
                    placeholder="请输入验证码"
                    prefix-icon="el-icon-message"
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
                  class="primary-button login-button"
                  @click.native.prevent="handleMobileLogin"
                >登录</el-button>
              </el-form-item>
            </el-form>
          </transition>
        </el-tab-pane>
      </el-tabs>

      <div class="auth-actions login-actions">
        <p>还没有账号? <router-link to="/register" class="auth-link register-link">立即注册</router-link></p>
      </div>

      <div class="auth-footer login-footer">
        <p>Copyright © 2025 智能数字人服务系统</p>
        <p>推荐使用Chrome浏览器访问</p>
      </div>
    </div>

    <!-- 装饰元素 -->
    <div class="floating-element floating-element-1"></div>
    <div class="floating-element floating-element-2"></div>
    <div class="floating-element floating-element-3"></div>
    <div class="airplane airplane-1"></div>
    <div class="airplane airplane-2"></div>
    <div class="cloud cloud-1"></div>
    <div class="cloud cloud-2"></div>
    <div class="cloud cloud-3"></div>
  </div>
</template>

<script>
// 导入需要的API函数
import { sendPhoneCode } from '@/api/user'

export default {
  name: 'Login',
  data() {
    // 校验手机号
    const validateMobile = (rule, value, callback) => {
      const mobileReg = /^1[3-9]\d{9}$/
      if (!value) {
        callback(new Error('请输入手机号'))
      } else if (!mobileReg.test(value)) {
        callback(new Error('请输入正确的手机号'))
      } else {
        callback()
      }
    }

    return {
      // 当前激活的标签页
      activeTab: 'account',
      // 账号密码表单
      loginForm: {
        username: '',
        password: ''
      },
      // 手机号表单
      mobileForm: {
        mobile: '',
        code: ''
      },
      // 表单验证规则
      loginRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 30, message: '长度在 6 到 30 个字符', trigger: 'blur' }
        ]
      },
      // 手机表单验证规则
      mobileRules: {
        mobile: [
          { required: true, trigger: 'blur', validator: validateMobile }
        ],
        code: [
          { required: true, message: '请输入验证码', trigger: 'blur' },
          { min: 4, max: 6, message: '长度在 4 到 6 个字符', trigger: 'blur' }
        ]
      },
      // 密码显示类型
      passwordType: 'password',
      // 加载状态
      loading: false,
      // 重定向路径
      redirect: undefined,
      // 验证码按钮文字
      codeButtonText: '获取验证码',
      // 验证码按钮禁用状态
      codeButtonDisabled: false,
      // 计时器
      timer: null,
      // 倒计时
      countdown: 60,
      // 记住我
      rememberMe: false
    }
  },
  watch: {
    $route: {
      handler: function(route) {
        this.redirect = route.query && route.query.redirect
      },
      immediate: true
    }
  },
  methods: {
    // 展示密码
    showPwd() {
      this.passwordType = this.passwordType === 'password' ? '' : 'password'
      this.$nextTick(() => {
        this.$refs.password.focus()
      })
    },
    // 账号密码登录
    handleLogin() {
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true
          // 构建请求参数
          const loginParams = {
            username: this.loginForm.username,
            password: this.loginForm.password
          }
          this.$store.dispatch('user/login', loginParams)
            .then(() => {
              this.$message.success('登录成功')
              this.$router.push({ path: this.redirect || '/' })
              this.loading = false
            })
            .catch(error => {
              console.error('登录失败:', error)
              this.$message.error(error.message || error.response?.data?.error || '登录失败，请重试')
              this.loading = false
            })
        }
      })
    },
    // 手机号登录
    handleMobileLogin() {
      this.$refs.mobileForm.validate(valid => {
        if (valid) {
          this.loading = true
          // 构建手机登录请求参数
          const mobileLoginParams = {
            phone: this.mobileForm.mobile,
            code: this.mobileForm.code
          }
          // 调用手机登录API
          this.$store.dispatch('user/mobileLogin', mobileLoginParams)
            .then(() => {
              this.$message.success('登录成功')
              this.$router.push({ path: this.redirect || '/' })
              this.loading = false
            })
            .catch(error => {
              console.error('登录失败:', error)
              this.$message.error(error.message || error.response?.data?.error || '登录失败，请重试')
              this.loading = false
            })
        }
      })
    },
    // 发送验证码
    handleSendCode() {
      this.$refs.mobileForm.validateField('mobile', (error) => {
        if (!error) {
          this.loading = true
          // 调用发送验证码API
          sendPhoneCode(this.mobileForm.mobile)
            .then(response => {
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
              this.$message.success(`验证码已发送至 ${this.mobileForm.mobile}`)
              this.loading = false
            })
            .catch(error => {
              console.error('发送验证码失败:', error)
              this.$message.error(error.message || error.response?.data?.error || '验证码发送失败，请重试')
              this.loading = false
            })
        }
      })
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

.login-container {
  background: linear-gradient(135deg, #1a75ff, #3e9dff);
  
  &::before, &::after {
    animation: floating 20s infinite ease-in-out;
  }
  
  .login-box {
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(15px);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.2);
    overflow: hidden;
    transition: all 0.5s cubic-bezier(0.215, 0.61, 0.355, 1);
    
    &::before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 5px;
      background: linear-gradient(90deg, #409EFF, #36D1DC);
    }
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    .login-header {
      .title {
        font-size: 28px;
        font-weight: 600;
        background: linear-gradient(90deg, #409EFF, #36D1DC);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        margin-bottom: 8px;
      }
      
      .subtitle {
        color: #666;
        font-size: 16px;
      }
    }
    
    .login-tabs {
      margin-bottom: 15px;
      
      .el-tabs__header {
        margin-bottom: 25px;
      }
      
      .el-tabs__nav-wrap::after {
        height: 1px;
        background-color: #ebeef5;
      }
      
      .el-tabs__item {
        font-size: 16px;
        height: 50px;
        line-height: 50px;
        transition: all 0.3s;
        
        &:hover {
          color: #36D1DC;
        }
        
        &.is-active {
          color: #409EFF;
          font-weight: 500;
        }
      }
      
      .el-tabs__active-bar {
        background: linear-gradient(90deg, #409EFF, #36D1DC);
        height: 3px;
        border-radius: 3px;
      }
    }
    
    .login-form {
      .el-input__inner {
        border-radius: 8px;
        height: 42px;
        border: 1px solid #e0e7ff;
        transition: all 0.3s;
        
        &:focus {
          border-color: #409EFF;
          box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
        }
      }
      
      .code-input {
        display: flex;
        
        .el-input {
          flex: 1;
          margin-right: 10px;
        }
        
        .code-button {
          border-radius: 8px;
          background: linear-gradient(90deg, #409EFF, #36D1DC);
          border: none;
        }
      }
      
      .password-eye {
        cursor: pointer;
        color: #c0c4cc;
        
        &:hover {
          color: #409EFF;
        }
      }
    }
    
    .login-options {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;

      .el-checkbox__input.is-checked .el-checkbox__inner {
        background-color: #409EFF;
        border-color: #409EFF;
      }
      
      .el-checkbox__input.is-checked + .el-checkbox__label {
        color: #409EFF;
      }

      .forget-password {
        font-size: 14px;
        color: #409EFF;
        
        &:hover {
          text-decoration: underline;
        }
      }
    }
    
    .login-button {
      width: 100%;
      height: 44px;
      font-size: 16px;
      border-radius: 8px;
      background: linear-gradient(90deg, #409EFF, #36D1DC);
      border: none;
      transition: all 0.3s;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
      }
    }
    
    .login-actions {
      text-align: center;
      margin-top: 20px;
      font-size: 14px;
      
      .register-link {
        font-weight: 600;
        color: #409EFF;
        
        &:hover {
          text-decoration: underline;
        }
      }
    }
    
    .login-footer {
      margin-top: 20px;
      text-align: center;
      color: #909399;
      font-size: 12px;
      
      p {
        margin: 5px 0;
      }
    }
  }
}

// 装饰元素样式
.floating-element {
  position: absolute;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
}

.floating-element-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  left: 15%;
  animation: floating-1 20s infinite ease-in-out;
}

.floating-element-2 {
  width: 150px;
  height: 150px;
  bottom: 20%;
  right: 15%;
  animation: floating-2 15s infinite ease-in-out;
}

.floating-element-3 {
  width: 100px;
  height: 100px;
  top: 50%;
  right: 25%;
  animation: floating-3 10s infinite ease-in-out;
}

// 飞机元素
.airplane {
  position: absolute;
  width: 40px;
  height: 40px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M21.5,15.5c-0.83,0-1.5-0.67-1.5-1.5V8.25L5.5,11.47V14c0,0.55-0.45,1-1,1h0c-0.55,0-1-0.45-1-1v-1.53L1,13v-2l2.5-0.5V9c0-0.55,0.45-1,1-1h0c0.55,0,1,0.45,1,1v2.53l14.5-3.22V7.5C20,6.67,20.67,6,21.5,6S23,6.67,23,7.5v6C23,14.33,22.33,15,21.5,15.5z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  z-index: 1;
  opacity: 0.7;
}

.airplane-1 {
  top: 15%;
  left: 10%;
  animation: fly-1 30s linear infinite;
}

.airplane-2 {
  bottom: 25%;
  left: 20%;
  transform: scale(0.8);
  animation: fly-2 40s linear infinite;
  animation-delay: -15s;
}

// 云朵元素
.cloud {
  position: absolute;
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: 50px;
  z-index: 0;
  filter: blur(5px);
}

.cloud-1 {
  width: 120px;
  height: 40px;
  top: 25%;
  right: 10%;
  animation: cloud-move-1 35s linear infinite;
}

.cloud-2 {
  width: 80px;
  height: 30px;
  top: 60%;
  right: 20%;
  animation: cloud-move-2 25s linear infinite;
  animation-delay: -5s;
}

.cloud-3 {
  width: 100px;
  height: 30px;
  top: 40%;
  left: 5%;
  animation: cloud-move-3 30s linear infinite;
  animation-delay: -12s;
}

@keyframes floating-1 {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(20px, 30px) rotate(5deg); }
  50% { transform: translate(0, 60px) rotate(0deg); }
  75% { transform: translate(-20px, 30px) rotate(-5deg); }
}

@keyframes floating-2 {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(-30px, 20px) rotate(-5deg); }
  50% { transform: translate(0, 40px) rotate(0deg); }
  75% { transform: translate(30px, 20px) rotate(5deg); }
}

@keyframes floating-3 {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(15px, -20px) rotate(5deg); }
  50% { transform: translate(0, -40px) rotate(0deg); }
  75% { transform: translate(-15px, -20px) rotate(-5deg); }
}

@keyframes fly-1 {
  0% { transform: translateX(0) rotate(-10deg); }
  100% { transform: translateX(calc(100vw + 100px)) rotate(-10deg); }
}

@keyframes fly-2 {
  0% { transform: translateX(0) rotate(-5deg) scale(0.8); }
  100% { transform: translateX(calc(100vw + 100px)) rotate(-5deg) scale(0.8); }
}

@keyframes cloud-move-1 {
  0% { transform: translateX(0); }
  100% { transform: translateX(-100vw); }
}

@keyframes cloud-move-2 {
  0% { transform: translateX(0); }
  100% { transform: translateX(-100vw); }
}

@keyframes cloud-move-3 {
  0% { transform: translateX(0); }
  100% { transform: translateX(100vw); }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .login-container {
    .login-box {
      width: 90%;
      max-width: 450px;
      padding: 30px 20px;
    }
    
    .floating-element-1, .floating-element-2 {
      display: none;
    }
  }
}
</style>
