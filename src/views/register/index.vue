<template>
  <div class="auth-container register-container">
    <div class="auth-box register-box">
      <div class="auth-header register-header">
        <h2 class="title">智能数字人服务系统</h2>
        <p class="subtitle">账号注册</p>
      </div>

      <transition name="fade-in" appear>
        <el-form
          ref="registerForm"
          :model="registerForm"
          :rules="registerRules"
          class="auth-form register-form"
          label-position="top"
        >
          <div class="form-row">
            <el-form-item prop="username" label="用户名">
              <el-input
                v-model="registerForm.username"
                placeholder="请输入用户名"
                type="text"
                prefix-icon="el-icon-user"
                clearable
              />
            </el-form-item>
            <el-form-item prop="email" label="邮箱">
              <el-input
                v-model="registerForm.email"
                placeholder="请输入邮箱"
                type="email"
                prefix-icon="el-icon-message"
                clearable
              />
            </el-form-item>
          </div>
          
          <div class="form-row">
            <el-form-item prop="mobile" label="手机号">
              <el-input
                v-model="registerForm.mobile"
                placeholder="请输入手机号"
                type="text"
                prefix-icon="el-icon-mobile-phone"
                clearable
              />
            </el-form-item>
          </div>

          <div class="form-row">
            <el-form-item prop="password" label="密码">
              <el-input
                v-model="registerForm.password"
                :type="passwordType"
                placeholder="请输入密码"
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
                v-model="registerForm.confirmPassword"
                :type="passwordType"
                placeholder="请再次输入密码"
                prefix-icon="el-icon-lock"
              >
                <i
                  slot="suffix"
                  class="el-input__icon el-icon-view password-eye"
                  @click="showPwd"
                />
              </el-input>
            </el-form-item>
          </div>

          <el-form-item prop="agreement">
            <el-checkbox v-model="registerForm.agreement">我已阅读并同意<a href="javascript:void(0)" @click="showAgreement" class="agreement-link">《用户协议》</a></el-checkbox>
          </el-form-item>

          <el-form-item>
            <el-button
              :loading="loading"
              type="primary"
              class="primary-button register-button"
              @click.native.prevent="handleRegister"
            >注册</el-button>
          </el-form-item>
        </el-form>
      </transition>

      <div class="auth-actions register-actions">
        <p>已有账号? <router-link to="/login" class="auth-link login-link">立即登录</router-link></p>
      </div>

      <div class="auth-footer register-footer">
        <p>Copyright © 2025 智能数字人服务系统</p>
      </div>
    </div>
    
    <!-- 机场相关装饰元素 -->
    <div class="decoration-element airplane-large"></div>
    <div class="decoration-element airplane-small"></div>
    <div class="decoration-element boarding-pass"></div>
    <div class="decoration-element luggage"></div>
    <div class="cloud-decoration cloud-1"></div>
    <div class="cloud-decoration cloud-2"></div>
    <div class="cloud-decoration cloud-3"></div>
    <div class="runway-decoration"></div>
  </div>
</template>

<script>
import { register } from '@/api/user'

export default {
  name: 'Register',
  data() {
    // 校验密码一致性
    const validatePassword = (rule, value, callback) => {
      if (value !== this.registerForm.password) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
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
    // 校验邮箱
    const validateEmail = (rule, value, callback) => {
      const emailReg = /^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/
      if (!value) {
        callback(new Error('请输入邮箱'))
      } else if (!emailReg.test(value)) {
        callback(new Error('请输入正确的邮箱格式'))
      } else {
        callback()
      }
    }
    // 校验协议
    const validateAgreement = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请同意用户协议'))
      } else {
        callback()
      }
    }

    return {
      // 注册表单
      registerForm: {
        username: '',
        email: '',
        mobile: '',
        password: '',
        confirmPassword: '',
        agreement: false
      },
      // 表单验证规则
      registerRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, trigger: 'blur', validator: validateEmail }
        ],
        mobile: [
          { required: true, trigger: 'blur', validator: validateMobile }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 30, message: '长度在 6 到 30 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          { validator: validatePassword, trigger: 'blur' }
        ],
        agreement: [
          { validator: validateAgreement, trigger: 'change' }
        ]
      },
      // 密码显示类型
      passwordType: 'password',
      // 加载状态
      loading: false
    }
  },
  methods: {
    // 显示密码
    showPwd() {
      this.passwordType = this.passwordType === 'password' ? '' : 'password'
    },
    // 处理注册
    handleRegister() {
      this.$refs.registerForm.validate(valid => {
        if (valid) {
          this.loading = true
          // 构建注册参数
          const registerParams = {
            username: this.registerForm.username,
            email: this.registerForm.email,
            phone: this.registerForm.mobile,
            password: this.registerForm.password,
            password_confirm: this.registerForm.confirmPassword
          }
          register(registerParams)
            .then(response => {
              this.$message.success('注册成功，请登录')
              // 跳转到登录页
              this.$router.push('/login')
              this.loading = false
            })
            .catch(error => {
              console.error('注册失败:', error)
              this.$message.error(error.message || error.response?.data?.error || '注册失败，请重试')
              this.loading = false
            })
        }
      })
    },
    // 显示用户协议
    showAgreement() {
      this.$alert('本协议是您与本站所有者之间的协议，规范用户使用本网站的行为。请您仔细阅读以下内容。', '用户协议', {
        confirmButtonText: '我已阅读并同意',
        callback: action => {
          this.registerForm.agreement = true
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
@import "@/styles/auth-forms.scss";

.register-container {
  background: linear-gradient(135deg, #409EFF, #36D1DC);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 15%;
    background: rgba(255, 255, 255, 0.08);
    transform: skewY(-1.5deg);
    transform-origin: bottom left;
    z-index: 0;
  }
  
  .register-box {
    width: 580px;
    max-width: 95%;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(15px);
    border-radius: 16px;
    padding: 30px;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
    position: relative;
    z-index: 10;
    transition: all 0.5s ease;
    border: 1px solid rgba(255, 255, 255, 0.2);
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    &::before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 5px;
      background: linear-gradient(90deg, #409EFF, #36D1DC);
      border-radius: 16px 16px 0 0;
    }
    
    .register-header {
      margin-bottom: 20px;
      
      .title {
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 8px;
        background: linear-gradient(90deg, #409EFF, #36D1DC);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
      }
      
      .subtitle {
        font-size: 16px;
        color: #606266;
      }
    }
    
    .register-form {
      .form-row {
        display: flex;
        gap: 15px;
        margin-bottom: 5px;
        
        .el-form-item {
          flex: 1;
          
          &:last-child {
            margin-right: 0;
          }
        }
      }
      
      .el-form-item {
        margin-bottom: 15px;
      }
      
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
      
      .password-eye {
        cursor: pointer;
        color: #c0c4cc;
        
        &:hover {
          color: #409EFF;
        }
      }
      
      .el-checkbox__input.is-checked .el-checkbox__inner {
        background-color: #409EFF;
        border-color: #409EFF;
      }
      
      .el-checkbox__input.is-checked + .el-checkbox__label {
        color: #333;
      }
      
      .agreement-link {
        color: #409EFF;
        text-decoration: none;
        transition: all 0.3s;
        
        &:hover {
          opacity: 0.8;
          text-decoration: underline;
        }
      }
      
      .register-button {
        width: 100%;
        height: 44px;
        font-size: 16px;
        border-radius: 8px;
        background: linear-gradient(90deg, #409EFF, #36D1DC);
        border: none;
        margin-top: 10px;
        transition: all 0.3s;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
        }
      }
    }
    
    .register-actions {
      margin-top: 15px;
      text-align: center;
      font-size: 14px;
      
      .login-link {
        font-weight: 600;
        color: #409EFF;
        
        &:hover {
          text-decoration: underline;
        }
      }
    }
    
    .register-footer {
      margin-top: 20px;
      text-align: center;
      color: #909399;
      font-size: 12px;
    }
  }
}

/* 装饰元素 */
.decoration-element {
  position: absolute;
  z-index: 1;
  pointer-events: none;
  opacity: 0.7;
}

.airplane-large {
  width: 120px;
  height: 120px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M21.5,15.5c-0.83,0-1.5-0.67-1.5-1.5V8.25L5.5,11.47V14c0,0.55-0.45,1-1,1h0c-0.55,0-1-0.45-1-1v-1.53L1,13v-2l2.5-0.5V9c0-0.55,0.45-1,1-1h0c0.55,0,1,0.45,1,1v2.53l14.5-3.22V7.5C20,6.67,20.67,6,21.5,6S23,6.67,23,7.5v6C23,14.33,22.33,15,21.5,15.5z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  top: 15%;
  right: -60px;
  transform: rotate(-20deg);
  animation: fly-large 40s linear infinite;
}

.airplane-small {
  width: 60px;
  height: 60px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M21.5,15.5c-0.83,0-1.5-0.67-1.5-1.5V8.25L5.5,11.47V14c0,0.55-0.45,1-1,1h0c-0.55,0-1-0.45-1-1v-1.53L1,13v-2l2.5-0.5V9c0-0.55,0.45-1,1-1h0c0.55,0,1,0.45,1,1v2.53l14.5-3.22V7.5C20,6.67,20.67,6,21.5,6S23,6.67,23,7.5v6C23,14.33,22.33,15,21.5,15.5z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  bottom: 30%;
  left: 10%;
  transform: rotate(15deg);
  animation: fly-small 25s linear infinite;
  animation-delay: -10s;
}

.boarding-pass {
  width: 80px;
  height: 50px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 5px;
  top: 25%;
  left: 5%;
  transform: rotate(-15deg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: float-pass 6s ease-in-out infinite;
  
  &::after {
    content: "";
    position: absolute;
    top: 50%;
    left: 0;
    width: 100%;
    height: 1px;
    background: rgba(0, 0, 0, 0.1);
  }
  
  &::before {
    content: "";
    position: absolute;
    top: 30%;
    right: -5px;
    width: 10px;
    height: 10px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 50%;
  }
}

.luggage {
  width: 40px;
  height: 60px;
  background-color: rgba(255, 255, 255, 0.6);
  border-radius: 4px;
  bottom: 10%;
  right: 15%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: float-luggage 5s ease-in-out infinite;
  
  &::after {
    content: "";
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 20px;
    height: 10px;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 10px 10px 0 0;
  }
}

.cloud-decoration {
  position: absolute;
  background-color: rgba(255, 255, 255, 0.4);
  border-radius: 50px;
  filter: blur(5px);
  z-index: 0;
}

.cloud-1 {
  width: 150px;
  height: 50px;
  top: 10%;
  left: 30%;
  animation: cloud-float-1 40s linear infinite;
}

.cloud-2 {
  width: 100px;
  height: 40px;
  bottom: 20%;
  right: 10%;
  animation: cloud-float-2 30s linear infinite;
}

.cloud-3 {
  width: 180px;
  height: 60px;
  top: 70%;
  left: 15%;
  animation: cloud-float-3 50s linear infinite;
}

.runway-decoration {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 40px;
  background: repeating-linear-gradient(90deg, 
    rgba(255, 255, 255, 0.3), 
    rgba(255, 255, 255, 0.3) 50px, 
    transparent 50px, 
    transparent 100px);
  z-index: 0;
}

@keyframes fly-large {
  0% {
    transform: translate(0, 0) rotate(-20deg);
  }
  100% {
    transform: translate(-120vw, 30vh) rotate(-10deg);
  }
}

@keyframes fly-small {
  0% {
    transform: translate(0, 0) rotate(15deg);
  }
  100% {
    transform: translate(120vw, -20vh) rotate(20deg);
  }
}

@keyframes float-pass {
  0%, 100% {
    transform: translate(0, 0) rotate(-15deg);
  }
  50% {
    transform: translate(10px, -10px) rotate(-10deg);
  }
}

@keyframes float-luggage {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-5px, -15px);
  }
}

@keyframes cloud-float-1 {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(100vw);
  }
}

@keyframes cloud-float-2 {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-100vw);
  }
}

@keyframes cloud-float-3 {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(100vw);
  }
}

/* 淡入动画 */
.fade-in-enter-active {
  animation: fadeIn 0.6s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式调整 */
@media screen and (max-width: 600px) {
  .register-container {
    .register-box {
      width: 90%;
      padding: 20px;
      
      .register-form {
        .form-row {
          flex-direction: column;
          gap: 0;
        }
      }
    }
    
    .decoration-element {
      opacity: 0.4;
    }
  }
}
</style>