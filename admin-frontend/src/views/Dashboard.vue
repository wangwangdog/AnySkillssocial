<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="icon" style="background: #409EFF">
              <el-icon :size="30"><User /></el-icon>
            </div>
            <div class="info">
              <div class="label">总用户数</div>
              <div class="value">{{ stats.users?.total || 0 }}</div>
              <div class="sub">今日新增：{{ stats.users?.today || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="icon" style="background: #67C23A">
              <el-icon :size="30"><List /></el-icon>
            </div>
            <div class="info">
              <div class="label">总订单数</div>
              <div class="value">{{ stats.orders?.total || 0 }}</div>
              <div class="sub">今日：{{ stats.orders?.today || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="icon" style="background: #E6A23C">
              <el-icon :size="30"><Document /></el-icon>
            </div>
            <div class="info">
              <div class="label">活跃服务</div>
              <div class="value">{{ stats.services?.active || 0 }}</div>
              <div class="sub">需求：{{ stats.services?.demands || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="icon" style="background: #F56C6C">
              <el-icon :size="30"><Money /></el-icon>
            </div>
            <div class="info">
              <div class="label">今日收入</div>
              <div class="value">¥{{ stats.revenue?.today || 0 }}</div>
              <div class="sub">完成订单</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <span>订单趋势（近 30 天）</span>
          </template>
          <div ref="chartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <span>快捷操作</span>
          </template>
          <el-button type="primary" block style="margin-bottom: 10px">查看待审核内容</el-button>
          <el-button type="warning" block style="margin-bottom: 10px">异常订单处理</el-button>
          <el-button type="success" block>导出财务报表</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { User, List, Document, Money } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const stats = ref({})
const chartRef = ref(null)

const loadStats = async () => {
  // 模拟数据
  stats.value = {
    users: { total: 1258, today: 23 },
    orders: { total: 3421, today: 45, completed: 3200 },
    services: { active: 892, demands: 156 },
    revenue: { today: 12580.50 }
  }
  
  // 初始化图表
  initChart()
}

const initChart = () => {
  const chart = echarts.init(chartRef.value)
  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['1', '2', '3', '4', '5', '6', '7'] },
    yAxis: { type: 'value' },
    series: [
      { data: [120, 200, 150, 80, 70, 110, 130], type: 'line', smooth: true, areaStyle: {} }
    ]
  }
  chart.setOption(option)
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
}
.icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.info {
  flex: 1;
}
.label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 5px;
}
.value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}
.sub {
  color: #909399;
  font-size: 12px;
}
</style>
