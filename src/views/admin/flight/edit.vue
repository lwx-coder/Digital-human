<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>编辑航班信息</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="goBack">返回列表</el-button>
      </div>
      
      <div v-loading="loading">
        <el-form ref="flightForm" :model="flightForm" :rules="rules" label-width="120px" class="flight-form">
          <el-form-item label="航班号" prop="flight_number">
            <el-input v-model="flightForm.flight_number" placeholder="请输入航班号"></el-input>
          </el-form-item>
          
          <el-form-item label="航空公司" prop="airline">
            <el-input v-model="flightForm.airline" placeholder="请输入航空公司"></el-input>
          </el-form-item>
          
          <el-form-item label="出发城市" prop="departure_city">
            <el-input v-model="flightForm.departure_city" placeholder="请输入出发城市"></el-input>
          </el-form-item>
          
          <el-form-item label="到达城市" prop="arrival_city">
            <el-input v-model="flightForm.arrival_city" placeholder="请输入到达城市"></el-input>
          </el-form-item>
          
          <el-form-item label="出发机场" prop="departure_airport">
            <el-input v-model="flightForm.departure_airport" placeholder="请输入出发机场"></el-input>
          </el-form-item>
          
          <el-form-item label="到达机场" prop="arrival_airport">
            <el-input v-model="flightForm.arrival_airport" placeholder="请输入到达机场"></el-input>
          </el-form-item>
          
          <el-form-item label="计划出发时间" prop="scheduled_departure_time">
            <el-date-picker
              v-model="flightForm.scheduled_departure_time"
              type="datetime"
              placeholder="选择日期时间"
              align="right"
              :picker-options="pickerOptions">
            </el-date-picker>
          </el-form-item>
          
          <el-form-item label="计划到达时间" prop="scheduled_arrival_time">
            <el-date-picker
              v-model="flightForm.scheduled_arrival_time"
              type="datetime"
              placeholder="选择日期时间"
              align="right"
              :picker-options="pickerOptions">
            </el-date-picker>
          </el-form-item>
          
          <el-form-item label="实际出发时间" prop="actual_departure_time">
            <el-date-picker
              v-model="flightForm.actual_departure_time"
              type="datetime"
              placeholder="选择日期时间"
              align="right"
              :picker-options="pickerOptions">
            </el-date-picker>
          </el-form-item>
          
          <el-form-item label="实际到达时间" prop="actual_arrival_time">
            <el-date-picker
              v-model="flightForm.actual_arrival_time"
              type="datetime"
              placeholder="选择日期时间"
              align="right"
              :picker-options="pickerOptions">
            </el-date-picker>
          </el-form-item>
          
          <el-form-item label="航站楼" prop="terminal">
            <el-input v-model="flightForm.terminal" placeholder="请输入航站楼"></el-input>
          </el-form-item>
          
          <el-form-item label="登机口" prop="gate">
            <el-input v-model="flightForm.gate" placeholder="请输入登机口"></el-input>
          </el-form-item>
          
          <el-form-item label="航班状态" prop="status">
            <el-select v-model="flightForm.status" placeholder="请选择航班状态" style="width: 100%">
              <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="submitForm('flightForm')">保存</el-button>
            <el-button @click="resetForm('flightForm')">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script>
import { getFlightDetail, updateFlight } from '@/api/flight'

export default {
  name: 'EditFlight',
  data() {
    return {
      loading: true,
      flightId: null,
      flightForm: {
        flight_number: '',
        airline: '',
        departure_city: '',
        arrival_city: '',
        departure_airport: '',
        arrival_airport: '',
        scheduled_departure_time: '',
        scheduled_arrival_time: '',
        actual_departure_time: '',
        actual_arrival_time: '',
        gate: '',
        terminal: '',
        status: ''
      },
      statusOptions: [
        { label: '计划', value: 'scheduled' },
        { label: '延误', value: 'delayed' },
        { label: '登机中', value: 'boarding' },
        { label: '已起飞', value: 'departed' },
        { label: '已到达', value: 'arrived' },
        { label: '取消', value: 'cancelled' }
      ],
      pickerOptions: {
        shortcuts: [{
          text: '今天',
          onClick(picker) {
            picker.$emit('pick', new Date())
          }
        }, {
          text: '明天',
          onClick(picker) {
            const date = new Date()
            date.setTime(date.getTime() + 3600 * 1000 * 24)
            picker.$emit('pick', date)
          }
        }, {
          text: '一周后',
          onClick(picker) {
            const date = new Date()
            date.setTime(date.getTime() + 3600 * 1000 * 24 * 7)
            picker.$emit('pick', date)
          }
        }]
      },
      rules: {
        flight_number: [
          { required: true, message: '请输入航班号', trigger: 'blur' },
          { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ],
        airline: [
          { required: true, message: '请输入航空公司', trigger: 'blur' }
        ],
        departure_city: [
          { required: true, message: '请输入出发城市', trigger: 'blur' }
        ],
        arrival_city: [
          { required: true, message: '请输入到达城市', trigger: 'blur' }
        ],
        departure_airport: [
          { required: true, message: '请输入出发机场', trigger: 'blur' }
        ],
        arrival_airport: [
          { required: true, message: '请输入到达机场', trigger: 'blur' }
        ],
        scheduled_departure_time: [
          { required: true, message: '请选择计划出发时间', trigger: 'change' }
        ],
        scheduled_arrival_time: [
          { required: true, message: '请选择计划到达时间', trigger: 'change' }
        ],
        status: [
          { required: true, message: '请选择航班状态', trigger: 'change' }
        ]
      }
    }
  },
  created() {
    this.flightId = this.$route.params.id
    this.getFlightInfo()
  },
  methods: {
    getFlightInfo() {
      this.loading = true
      getFlightDetail(this.flightId).then(response => {
        // 将接口返回的数据赋值给表单
        this.flightForm = { ...response }
        this.loading = false
      }).catch(error => {
        console.error(error)
        this.$message.error('获取航班信息失败')
        this.loading = false
      })
    },
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          // 提交表单
          updateFlight(this.flightId, this.flightForm).then(response => {
            this.$message({
              message: '更新航班成功！',
              type: 'success'
            })
            this.goBack()
          }).catch(error => {
            console.error(error)
            this.$message({
              message: '更新航班失败，请重试！',
              type: 'error'
            })
          })
        } else {
          this.$message({
            message: '请完善表单信息！',
            type: 'warning'
          })
          return false
        }
      })
    },
    resetForm(formName) {
      this.getFlightInfo()
    },
    goBack() {
      this.$router.push({ name: 'AdminFlightManagement' })
    }
  }
}
</script>

<style lang="scss" scoped>
.flight-form {
  max-width: 600px;
  margin: 0 auto;
}
</style> 