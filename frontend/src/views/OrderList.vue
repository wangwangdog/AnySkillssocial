<template>
  <div class="page">
    <van-nav-bar title="我的订单" left-arrow @click-left="$router.back()" />

    <!-- Tab switching -->
    <van-tabs v-model:active="activeTab" @change="onTabChange">
      <van-tab title="全部" name="all" />
      <van-tab title="待处理" name="pending" />
      <van-tab title="进行中" name="active" />
      <van-tab title="已完成" name="completed" />
    </van-tabs>

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="loadOrders"
      >
        <div v-for="item in list" :key="item.id" class="order-card" @click="$router.push(`/orders/${item.id}`)">
          <div class="order-header">
            <div class="order-title">{{ item.service?.title || item.demand?.title || '订单' }}</div>
            <van-tag :type="tagType(item.status)">
              {{ statusText(item.status) }}
            </van-tag>
          </div>
          <div class="order-meta">
            <span v-if="item.order_type === 'service' && item.service">
              <van-icon name="shop-o" /> {{ item.service.seller?.nickname || item.seller?.nickname || '卖家' }}
            </span>
            <span v-else-if="item.order_type === 'demand' && item.demand">
              <van-icon name="contact" /> {{ item.demand.creator?.nickname || item.buyer?.nickname || '发布者' }}
            </span>
            <span v-else>
              <van-icon name="contact" /> {{ item.seller?.nickname || '对方' }}
            </span>
            <span>¥{{ item.amount || 0 }}</span>
          </div>
          <div v-if="item.created_at" class="order-time">{{ formatTime(item.created_at) }}</div>

          <!-- Action buttons -->
          <div class="order-actions">
            <van-button
              v-if="canCheckin(item)"
              size="small"
              round
              type="primary"
              @click="handleCheckin(item)"
            >
              签到
            </van-button>
            <van-button
              v-if="canCheckout(item)"
              size="small"
              round
              type="success"
              @click="handleCheckout(item)"
            >
              完成
            </van-button>
            <van-button
              v-if="item.status === 'pending'"
              size="small"
              round
              plain
              type="danger"
              @click="showToast('取消功能开发中')"
            >
              取消
            </van-button>
          </div>
        </div>
        <div v-if="list.length === 0 && !loading" class="empty">暂无订单</div>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { listOrders, checkinOrder, checkoutOrder } from '@/utils/api'

const activeTab = ref('all')
const list = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
let page = 1
const pageSize = 10

async function loadOrders() {
  if (refreshing.value) {
    page = 1
    list.value = []
    finished.value = false
    refreshing.value = false
  }

  if (finished.value) return

  loading.value = true
  try {
    const res = await listOrders()
    const data = res.data || res || []
    const items = Array.isArray(data) ? data : (data.items || data || [])

    // Filter by tab
    let filtered = items
    if (activeTab.value === 'pending') {
      filtered = items.filter(o => o.status === 'pending')
    } else if (activeTab.value === 'active') {
      filtered = items.filter(o => o.status === 'active' || o.status === 'checked_in')
    } else if (activeTab.value === 'completed') {
      filtered = items.filter(o => o.status === 'completed' || o.status === 'checked_out')
    }

    list.value = filtered
    finished.value = true
  } catch {
    showToast('加载失败')
  } finally {
    loading.value = false
  }
}

function onRefresh() {
  finished.value = false
  page = 1
  list.value = []
  loadOrders()
}

function onTabChange() {
  finished.value = false
  page = 1
  list.value = []
  loadOrders()
}

function tagType(status) {
  const map = { pending: 'warning', active: 'primary', checked_in: 'primary', checked_out: 'success', completed: 'success', cancelled: 'danger' }
  return map[status] || 'default'
}

function statusText(status) {
  const map = { pending: '待处理', active: '进行中', checked_in: '已签到', checked_out: '已完成', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}

function canCheckin(item) {
  return item.status === 'active' || item.status === 'pending'
}

function canCheckout(item) {
  return item.status === 'checked_in'
}

async function handleCheckin(item) {
  showLoadingToast({ message: '签到中...', forbidClick: true })
  try {
    await checkinOrder(item.id, {})
    showToast('签到成功')
    onRefresh()
  } catch (err) {
    const msg = err.response?.data?.message || err.message || '签到失败'
    showToast(msg)
  } finally {
    closeToast()
  }
}

async function handleCheckout(item) {
  showLoadingToast({ message: '完成中...', forbidClick: true })
  try {
    await checkoutOrder(item.id, {})
    showToast('已完成')
    onRefresh()
  } catch (err) {
    const msg = err.response?.data?.message || err.message || '操作失败'
    showToast(msg)
  } finally {
    closeToast()
  }
}

function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString()
}
</script>

<style scoped>
.order-card {
  background: #fff;
  border-radius: 8px;
  padding: 14px;
  margin-bottom: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.order-title {
  font-size: 15px;
  font-weight: 600;
  flex: 1;
  margin-right: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.order-meta {
  font-size: 13px;
  color: #666;
  display: flex;
  gap: 16px;
  margin-bottom: 4px;
}
.order-meta span {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}
.order-time {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}
.order-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
.empty {
  text-align: center;
  padding: 40px 0;
  color: #999;
  font-size: 14px;
}
</style>
