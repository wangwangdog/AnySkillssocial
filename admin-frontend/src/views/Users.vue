<template>
  <div class="users-page">
    <el-card>
      <div class="toolbar">
        <el-input v-model="searchQuery" placeholder="搜索用户..." style="width: 300px" />
        <el-button type="primary" @click="loadUsers">搜索</el-button>
        <el-button type="danger" @click="handleBan">批量封禁</el-button>
      </div>
      
      <el-table :data="users" style="width: 100%" border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="用户信息" width="200">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 10px">
              <el-avatar :src="row.avatar" style="width: 40px; height: 40px">{{ row.nickname?.[0] }}</el-avatar>
              <div>
                <div>{{ row.nickname }}</div>
                <div style="font-size: 12px; color: #909399">{{ row.phone }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="member_level" label="会员等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.member_level)">{{ row.member_level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="资产" width="120">
          <template #default="{ row }">
            <div>现金：¥{{ row.cash_balance }}</div>
            <div style="font-size: 12px; color: #409EFF">积分：{{ row.points_balance }}</div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_verified" type="success">已认证</el-tag>
            <el-tag v-else type="info">未认证</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleToggleBan(row)">
              {{ row.is_banned ? '解封' : '封禁' }}
            </el-button>
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

const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')

const loadUsers = () => {
  // 模拟数据
  users.value = Array.from({ length: 10 }, (_, i) => ({
    id: i + 1,
    nickname: `用户${i + 1}`,
    phone: '138****1234',
    member_level: i % 3 === 0 ? 'gold' : i % 2 === 0 ? 'silver' : 'free',
    cash_balance: (Math.random() * 1000).toFixed(2),
    points_balance: Math.floor(Math.random() * 1000),
    is_verified: Math.random() > 0.3,
    is_banned: false,
    created_at: new Date().toISOString()
  }))
  total.value = 1258
}

const getLevelType = (level) => {
  return level === 'gold' ? 'warning' : level === 'silver' ? 'success' : 'info'
}

const handleEdit = (row) => {
  console.log('编辑用户', row)
}

const handleToggleBan = (row) => {
  row.is_banned = !row.is_banned
}

const handleBan = () => {
  console.log('批量封禁')
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
</style>
