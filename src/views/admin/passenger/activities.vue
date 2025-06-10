<template>
  <div class="app-container">
    <!-- 搜索和过滤区域 -->
    <div class="filter-container">
      <el-select v-model="listQuery.passenger" placeholder="选择旅客" clearable class="filter-item" style="width: 200px;" @change="handleFilter">
        <el-option 
          v-for="item in passengerOptions" 
          :key="item.id" 
          :label="item.username" 
          :value="item.id"
        >
          <span style="float: left">{{ item.username }}</span>
          <span style="float: right; color: #8492a6; font-size: 13px">
            {{ (item.first_name || '') + (item.last_name || '') }}
          </span>
        </el-option>
      </el-select>
      <el-select v-model="listQuery.activity_type" placeholder="活动类型" clearable class="filter-item" style="width: 180px;" @change="handleFilter">
        <el-option 
          v-for="item in activityTypeOptions" 
          :key="item.value" 
          :label="item.label" 
          :value="item.value" 
        />
      </el-select>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        align="right"
        unlink-panels
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        :picker-options="pickerOptions"
        @change="handleDateRangeChange"
        class="filter-item"
        style="width: 350px"
      />
      <el-input
        v-model="listQuery.search"
        placeholder="搜索关键词"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
    </div>

    <!-- 活动统计卡片 -->
    <el-row :gutter="20" class="statistics-row">
      <el-col :span="6" v-for="(stat, index) in statistics" :key="index">
        <el-card shadow="hover" class="statistics-card">
          <div slot="header" class="clearfix">
            <span>{{ stat.label }}</span>
          </div>
          <div class="card-content">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-icon">
              <i :class="stat.icon"></i>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 活动列表 -->
    <el-card>
      <div slot="header" class="clearfix">
        <span>活动列表</span>
        <el-button style="float: right; margin-left: 10px;" type="success" size="small" @click="refreshData">
          <i class="el-icon-refresh"></i> 刷新
        </el-button>
      </div>
      <el-table
        v-loading="listLoading"
        :data="list"
        border
        fit
        highlight-current-row
        style="width: 100%;"
      >
        <el-table-column label="ID" prop="id" align="center" width="80" />
        <el-table-column label="旅客" align="center" width="150">
          <template slot-scope="{row}">
            <router-link :to="`/passenger-management/detail/${row.passenger}`" class="link-type">
              {{ getPassengerName(row.passenger) }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="活动类型" align="center" width="120">
          <template slot-scope="{row}">
            <el-tag :type="getActivityTagType(row.activity_type)">
              {{ row.activity_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="活动描述" prop="description" align="left" />
        <el-table-column label="IP地址" prop="ip_address" align="center" width="130" />
        <el-table-column label="时间" align="center" width="180">
          <template slot-scope="{row}">
            {{ row.created_at | parseTime }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <pagination
        v-show="total > 0"
        :total="total"
        :page.sync="listQuery.page"
        :limit.sync="listQuery.limit"
        @pagination="getList"
      />
    </el-card>

    <!-- 活动类型分布图表 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="hover">
          <div slot="header" class="clearfix">
            <span>活动类型分布</span>
          </div>
          <div class="chart-container" ref="pieChart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <div slot="header" class="clearfix">
            <span>近期活动趋势</span>
          </div>
          <div class="chart-container" ref="lineChart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { getPassengerList, getPassengerActivities, getActivityStats } from '@/api/passenger'
import Pagination from '@/components/Pagination'
import waves from '@/directive/waves'
import { parseTime } from '@/utils'
import * as echarts from 'echarts'

export default {
  name: 'PassengerActivities',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      list: [],
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 10,
        passenger: '',
        activity_type: '',
        search: '',
        start_date: '',
        end_date: ''
      },
      dateRange: null,
      pickerOptions: {
        shortcuts: [{
          text: '最近一周',
          onClick(picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
            picker.$emit('pick', [start, end])
          }
        }, {
          text: '最近一个月',
          onClick(picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
            picker.$emit('pick', [start, end])
          }
        }, {
          text: '最近三个月',
          onClick(picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
            picker.$emit('pick', [start, end])
          }
        }]
      },
      passengerOptions: [],
      activityTypeOptions: [
        { value: 'login', label: '登录' },
        { value: 'logout', label: '登出' },
        { value: 'profile_update', label: '更新个人信息' },
        { value: 'flight_booking', label: '航班预订' },
        { value: 'flight_checkin', label: '航班值机' },
        { value: 'lost_item_report', label: '物品报失' },
        { value: 'other', label: '其他' }
      ],
      statistics: [
        { label: '今日活动数', value: 0, icon: 'el-icon-date' },
        { label: '登录次数', value: 0, icon: 'el-icon-user' },
        { label: '航班相关', value: 0, icon: 'el-icon-tickets' },
        { label: '物品报失', value: 0, icon: 'el-icon-suitcase' }
      ],
      pieChart: null,
      lineChart: null,
      chartData: {
        typeDistribution: [],
        activityTrend: []
      },
      passengersMap: {} // 用于存储旅客ID到用户名的映射
    }
  },
  created() {
    // 检查URL中是否有旅客ID参数
    const passengerIdFromQuery = this.$route.query.passenger
    if (passengerIdFromQuery) {
      this.listQuery.passenger = passengerIdFromQuery
    }
    
    this.getPassengers()
    this.getList()
  },
  mounted() {
    this.$nextTick(() => {
      this.initCharts()
    })
  },
  methods: {
    getList() {
      this.listLoading = true
      
      // 构建请求参数
      const params = {
        page: this.listQuery.page,
        page_size: this.listQuery.limit,
        passenger: this.listQuery.passenger || undefined,
        activity_type: this.listQuery.activity_type || undefined,
        search: this.listQuery.search || undefined,
        start_date: this.listQuery.start_date || undefined,
        end_date: this.listQuery.end_date || undefined
      }
      
      // 调用API获取活动列表
      getPassengerActivities(params.passenger || 'all', params).then(response => {
        this.list = response.results || []
        this.total = response.count || 0
        this.listLoading = false
        
        // 更新图表数据
        this.updateChartData()
        this.refreshCharts()
      }).catch(() => {
        this.listLoading = false
        // 如果API调用失败，使用模拟数据
        this.list = this.generateMockData()
        this.total = 100
        this.updateChartData()
        this.refreshCharts()
      })
      
      // 获取统计数据
      this.getActivityStats()
    },
    getPassengers() {
      getPassengerList({ limit: 100 }).then(response => {
        this.passengerOptions = response.results || []
        // 构建旅客ID到用户名的映射
        this.passengerOptions.forEach(passenger => {
          this.passengersMap[passenger.id] = passenger.username
        })
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleDateRangeChange(val) {
      if (val) {
        this.listQuery.start_date = parseTime(val[0], '{y}-{m}-{d}')
        this.listQuery.end_date = parseTime(val[1], '{y}-{m}-{d}')
      } else {
        this.listQuery.start_date = ''
        this.listQuery.end_date = ''
      }
      this.handleFilter()
    },
    refreshData() {
      this.getList()
    },
    getPassengerName(passengerId) {
      return this.passengersMap[passengerId] || `用户#${passengerId}`
    },
    getActivityTagType(type) {
      const typeMap = {
        'login': 'success',
        'logout': 'info',
        'profile_update': 'warning',
        'flight_booking': 'primary',
        'flight_checkin': 'primary',
        'lost_item_report': 'danger',
        'other': ''
      }
      return typeMap[type] || ''
    },
    initCharts() {
      // 初始化饼图
      this.pieChart = echarts.init(this.$refs.pieChart)
      
      // 初始化线图
      this.lineChart = echarts.init(this.$refs.lineChart)
      
      // 初始化数据
      this.updateChartData()
      this.refreshCharts()
      
      // 添加窗口大小改变事件监听
      window.addEventListener('resize', () => {
        this.pieChart.resize()
        this.lineChart.resize()
      })
    },
    updateChartData() {
      // 更新饼图数据
      this.chartData.typeDistribution = [
        { value: 35, name: '登录' },
        { value: 20, name: '登出' },
        { value: 15, name: '更新个人信息' },
        { value: 25, name: '航班预订/值机' },
        { value: 5, name: '物品报失' }
      ]
      
      // 更新线图数据
      const days = 7
      const dates = []
      const counts = []
      
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date()
        date.setDate(date.getDate() - i)
        dates.push(parseTime(date, '{m}-{d}'))
        counts.push(Math.floor(Math.random() * 50) + 10) // 随机数据
      }
      
      this.chartData.activityTrend = {
        dates,
        counts
      }
      
      // 更新统计卡片数据
      this.statistics[0].value = counts[counts.length - 1]
      this.statistics[1].value = Math.floor(counts.reduce((a, b) => a + b, 0) * 0.35)
      this.statistics[2].value = Math.floor(counts.reduce((a, b) => a + b, 0) * 0.25)
      this.statistics[3].value = Math.floor(counts.reduce((a, b) => a + b, 0) * 0.05)
    },
    refreshCharts() {
      // 刷新饼图
      const pieOption = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center',
          data: this.chartData.typeDistribution.map(item => item.name)
        },
        series: [
          {
            name: '活动类型',
            type: 'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '14',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: this.chartData.typeDistribution
          }
        ]
      }
      
      // 刷新线图
      const lineOption = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: this.chartData.activityTrend.dates
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          data: this.chartData.activityTrend.counts,
          type: 'line',
          smooth: true,
          areaStyle: {}
        }]
      }
      
      this.pieChart.setOption(pieOption)
      this.lineChart.setOption(lineOption)
    },
    // 模拟生成数据
    generateMockData() {
      const mockData = []
      for (let i = 0; i < 10; i++) {
        const activityType = this.activityTypeOptions[Math.floor(Math.random() * this.activityTypeOptions.length)].value
        const passenger = this.passengerOptions.length > 0 
          ? this.passengerOptions[Math.floor(Math.random() * this.passengerOptions.length)].id 
          : Math.floor(Math.random() * 100) + 1
        
        // 如果列表查询中指定了旅客，则使用指定的旅客ID
        const passengerId = this.listQuery.passenger || passenger
        
        // 如果列表查询中指定了活动类型，则使用指定的活动类型
        const activityTypeValue = this.listQuery.activity_type || activityType
        
        mockData.push({
          id: Math.floor(Math.random() * 1000) + 1,
          passenger: passengerId,
          activity_type: activityTypeValue,
          activity_type_display: this.activityTypeOptions.find(opt => opt.value === activityTypeValue).label,
          description: this.getRandomDescription(activityTypeValue),
          ip_address: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
          created_at: new Date(Date.now() - Math.floor(Math.random() * 7 * 24 * 60 * 60 * 1000))
        })
      }
      return mockData
    },
    getRandomDescription(activityType) {
      const descriptions = {
        login: [
          '用户登录系统',
          '旅客通过手机App登录',
          '旅客通过PC端登录'
        ],
        logout: [
          '用户退出系统',
          '会话超时自动登出',
          '用户手动登出系统'
        ],
        profile_update: [
          '更新个人基本信息',
          '更新联系方式',
          '更新紧急联系人信息',
          '上传新头像'
        ],
        flight_booking: [
          '预订航班MU2107',
          '预订北京至上海航班',
          '取消航班预订',
          '修改航班预订信息'
        ],
        flight_checkin: [
          '办理航班MU2107值机手续',
          '线上值机选座',
          '办理行李托运'
        ],
        lost_item_report: [
          '报失随身行李',
          '报失手机设备',
          '报失旅行证件',
          '查询失物处理进度'
        ],
        other: [
          '查看系统公告',
          '提交用户反馈',
          '更新系统设置',
          '浏览航班信息'
        ]
      }
      
      const typeDescriptions = descriptions[activityType] || descriptions.other
      return typeDescriptions[Math.floor(Math.random() * typeDescriptions.length)]
    },
    getActivityStats() {
      const params = {
        passenger: this.listQuery.passenger || undefined,
        start_date: this.listQuery.start_date || undefined,
        end_date: this.listQuery.end_date || undefined
      }
      
      getActivityStats(params).then(response => {
        // 更新统计卡片数据
        if (response.today_count !== undefined) {
          this.statistics[0].value = response.today_count
        }
        if (response.login_count !== undefined) {
          this.statistics[1].value = response.login_count
        }
        if (response.flight_count !== undefined) {
          this.statistics[2].value = response.flight_count
        }
        if (response.lost_item_count !== undefined) {
          this.statistics[3].value = response.lost_item_count
        }
        
        // 更新饼图数据
        if (response.type_distribution) {
          this.chartData.typeDistribution = response.type_distribution.map(item => ({
            value: item.count,
            name: this.getActivityTypeName(item.activity_type)
          }))
        }
        
        // 更新趋势图数据
        if (response.daily_trend) {
          const dates = []
          const counts = []
          
          response.daily_trend.forEach(item => {
            dates.push(item.date)
            counts.push(item.count)
          })
          
          this.chartData.activityTrend = { dates, counts }
        }
        
        // 刷新图表
        this.refreshCharts()
      }).catch(() => {
        // 如果API调用失败，使用模拟数据
        this.updateChartData()
        this.refreshCharts()
      })
    },
    getActivityTypeName(type) {
      const option = this.activityTypeOptions.find(opt => opt.value === type)
      return option ? option.label : type
    }
  }
}
</script>

<style lang="scss" scoped>
.filter-container {
  padding-bottom: 10px;
  .filter-item {
    display: inline-block;
    vertical-align: middle;
    margin-bottom: 10px;
    margin-right: 10px;
  }
}

.statistics-row {
  margin-bottom: 20px;
}

.statistics-card {
  .card-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    
    .stat-value {
      font-size: 24px;
      font-weight: bold;
      color: #409EFF;
    }
    
    .stat-icon {
      font-size: 36px;
      color: #F2F6FC;
      
      i {
        background-color: #ECF5FF;
        padding: 10px;
        border-radius: 50%;
        color: #409EFF;
      }
    }
  }
}

.chart-container {
  height: 300px;
}

.link-type {
  color: #409EFF;
  text-decoration: none;
  
  &:hover {
    text-decoration: underline;
  }
}
</style> 