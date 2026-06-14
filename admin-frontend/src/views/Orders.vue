<template>
  <div class="orders-page">
    <el-card>
      <div class="filter-bar">
        <el-select v-model="statusFilter" placeholder="订单状态">
          <el-option label="全部" value="" />
          <el-option label="待接单" value="pending" />
          <el-option label="已确认" value="confirmed" />
          <el-option label="服务中" value="in_progress" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <el-date-picker v-model="dateRange" type="daterange" placeholder="选择日期" style="width: 240px" />
        <el-button type="primary" @click="loadOrders">查询</el-button>
      </div>
      
      <el-table :data="orders" border>
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column label="买家" width="120">
          <template #default="{ row }">{{ row.buyer.nickname }}</template>
        </el-table-column>
        <el-table-column label="卖家" width="120">
          <template #default="{ row }">{{ row.seller.nickname }}</template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="{ row }">¥{{ row.amount }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const orders = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const statusFilter = ref('')
const dateRange = ref([])

const loadOrders = () => {
  orders.value = Array.from({ length: 10 }, (_, i) => ({
    order_no: `ORD${Date.now()}-${i}`,
    buyer: { nickname: '用户 A' },
    seller: { nickname: '用户 B' },
    amount: (Math.random() * 500).toFixed(2),
    status: ['pending', 'confirmed', 'in_progress', 'completed', 'cancelled'][Math.floor(Math.random() * 5)],
    created_at: new Date().toISOString()
  }))
  total.value = 3421
}

const getStatusType = (status) => {
  return status === 'completed' ? 'success' : status === 'cancelled' ? 'danger' : status === 'in_progress' ? 'warning' : 'info'
}

const handleView = (row) => {
  console.log('查看详情', row)
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
</style>
