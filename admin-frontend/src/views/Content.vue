<template>
  <div class="content-page">
    <el-tabs v-model="activeTab" @tab-click="onTabChange">
      <!-- 服务审核 Tab -->
      <el-tab-pane label="服务审核" name="services">
        <el-table :data="pendingServices" border v-loading="loading.services">
          <el-table-column label="服务信息" width="300">
            <template #default="{ row }">
              <div>
                <div style="font-weight: 600">{{ row.title }}</div>
                <div style="font-size: 12px; color: #909399; margin-top: 4px">{{ row.description?.substring(0, 60) }}...</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="seller.nickname" label="发布者" width="120" />
          <el-table-column prop="skill_type" label="技能类型" width="100" />
          <el-table-column label="价格" width="80">
            <template #default="{ row }">¥{{ row.price }}</template>
          </el-table-column>
          <el-table-column prop="created_at" label="提交时间" width="180" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button type="success" size="small" :loading="loading.approve === row.id" @click="handleApprove(row)">通过</el-button>
              <el-button type="danger" size="small" :loading="loading.reject === row.id" @click="handleReject(row)">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="pendingTotal === 0 && !loading.services" style="text-align:center;padding:40px;color:#909399">暂无待审核服务</div>
      </el-tab-pane>
      
      <!-- 内容管理 Tab（用户动态） -->
      <el-tab-pane label="用户动态" name="posts">
        <el-table :data="posts" border v-loading="loading.posts">
          <el-table-column label="发布者" width="160">
            <template #default="{ row }">
              <div style="display:flex;align-items:center;gap:8px">
                <el-avatar :size="28" :src="row.author.avatar" />
                <span>{{ row.author.nickname }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="动态内容" min-width="300">
            <template #default="{ row }">
              <div>
                <div style="white-space:pre-wrap;line-height:1.6">{{ row.content.substring(0, 120) }}{{ row.content.length > 120 ? '...' : '' }}</div>
                <div v-if="row.images && row.images.length > 0" style="display:flex;gap:4px;margin-top:6px">
                  <el-image v-for="(img, idx) in row.images.slice(0, 3)" :key="idx" :src="img" style="width:60px;height:60px;border-radius:4px" fit="cover" />
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="发布时间" width="180" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-popconfirm title="确定删除此动态？" @confirm="handleDeletePost(row)">
                <template #reference>
                  <el-button type="danger" size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="postsTotal === 0 && !loading.posts" style="text-align:center;padding:40px;color:#909399">暂无用户动态</div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('services')

const loading = reactive({
  services: false,
  posts: false,
  approve: null,
  reject: null,
  delete: false
})

const pendingServices = ref([])
const pendingTotal = ref(0)
const posts = ref([])
const postsTotal = ref(0)

const API_BASE = '/api/admin'

function getToken() {
  return localStorage.getItem('admin_token') || ''
}

async function fetchPendingServices() {
  loading.services = true
  try {
    const res = await fetch(`${API_BASE}/services/pending?page=1&page_size=50`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    const data = await res.json()
    pendingServices.value = data.data || []
    pendingTotal.value = data.total || 0
  } catch {
    ElMessage.error('加载待审核服务失败')
  } finally {
    loading.services = false
  }
}

async function fetchPosts() {
  loading.posts = true
  try {
    const res = await fetch(`${API_BASE}/posts/list?page=1&page_size=50`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    const data = await res.json()
    posts.value = data.data || []
    postsTotal.value = data.total || 0
  } catch {
    ElMessage.error('加载用户动态失败')
  } finally {
    loading.posts = false
  }
}

async function handleApprove(row) {
  loading.approve = row.id
  try {
    const res = await fetch(`${API_BASE}/services/approve/${row.id}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    if (!res.ok) throw new Error()
    ElMessage.success('已通过')
    pendingServices.value = pendingServices.value.filter(s => s.id !== row.id)
    pendingTotal.value--
  } catch {
    ElMessage.error('操作失败')
  } finally {
    loading.approve = null
  }
}

async function handleReject(row) {
  loading.reject = row.id
  try {
    const res = await fetch(`${API_BASE}/services/reject/${row.id}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    if (!res.ok) throw new Error()
    ElMessage.success('已拒绝')
    pendingServices.value = pendingServices.value.filter(s => s.id !== row.id)
    pendingTotal.value--
  } catch {
    ElMessage.error('操作失败')
  } finally {
    loading.reject = null
  }
}

async function handleDeletePost(row) {
  try {
    const res = await fetch(`${API_BASE}/posts/${row.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    if (!res.ok) throw new Error()
    ElMessage.success('已删除')
    posts.value = posts.value.filter(p => p.id !== row.id)
    postsTotal.value--
  } catch {
    ElMessage.error('删除失败')
  }
}

function onTabChange() {
  if (activeTab.value === 'services' && pendingServices.value.length === 0) {
    fetchPendingServices()
  } else if (activeTab.value === 'posts' && posts.value.length === 0) {
    fetchPosts()
  }
}

onMounted(() => {
  fetchPendingServices()
})
</script>

<style scoped>
.content-page {
  padding: 20px;
}
</style>
