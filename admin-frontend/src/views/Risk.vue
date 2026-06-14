<template>
  <div class="risk-page">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>异常订单</span>
          </template>
          <el-table :data="abnormalOrders" size="small">
            <el-table-column prop="order_no" label="订单号" />
            <el-table-column prop="risk_level" label="风险" width="80">
              <template #default="{ row }">
                <el-tag :type="row.risk_level === 'high' ? 'danger' : 'warning'">{{ row.risk_level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="原因" />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button size="small" @click="handleInvestigate(row)">调查</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>封禁用户</span>
          </template>
          <el-table :data="bannedUsers" size="small">
            <el-table-column prop="nickname" label="用户" />
            <el-table-column prop="ban_reason" label="原因" />
            <el-table-column prop="ban_time" label="时间" />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button type="success" size="small" @click="handleUnban(row)">解封</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>风控规则</span>
          </template>
          <el-form label-position="top">
            <el-form-item label="单笔订单上限">
              <el-input-number v-model="rules.maxOrderAmount" :min="0" :max="100000" />
            </el-form-item>
            <el-form-item label="每日下单上限">
              <el-input-number v-model="rules.dailyOrderLimit" :min="0" :max="100" />
            </el-form-item>
            <el-form-item label="自动封禁阈值">
              <el-switch v-model="rules.autoBanEnabled" />
            </el-form-item>
            <el-button type="primary" @click="saveRules">保存规则</el-button>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const abnormalOrders = ref([
  { order_no: 'ORD001', risk_level: 'high', reason: '金额异常' },
  { order_no: 'ORD002', risk_level: 'medium', reason: '频繁下单' }
])

const bannedUsers = ref([
  { nickname: '恶意用户', ban_reason: '欺诈行为', ban_time: '2024-01-01' }
])

const rules = reactive({
  maxOrderAmount: 5000,
  dailyOrderLimit: 10,
  autoBanEnabled: true
})

const handleInvestigate = (row) => {
  console.log('调查订单', row)
}

const handleUnban = (row) => {
  console.log('解封用户', row)
}

const saveRules = () => {
  console.log('保存规则', rules)
}
</script>

<style scoped>
</style>
