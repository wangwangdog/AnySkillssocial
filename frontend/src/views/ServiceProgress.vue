<template>
  <div class="page progress-page">
    <van-nav-bar title="服务进度" left-arrow @click-left="$router.back()" />

    <div v-if="loading" class="loading-wrap"><van-loading size="24px">加载中...</van-loading></div>

    <div v-else-if="error" class="error-wrap">
      <van-empty :description="error" />
      <van-button round plain style="margin-top:16px;border-color:#667eea;color:#667eea" @click="$router.push('/')">返回首页</van-button>
    </div>

    <template v-else-if="order">
      <!-- 服务摘要 -->
      <div class="order-summary">
        <van-image width="56" height="56" fit="cover" :src="order.seller?.avatar || defaultAvatar" round />
        <div class="order-summary-info">
          <div class="order-service-title">{{ order.service?.title || '服务订单' }}</div>
          <div class="order-meta">{{ order.buyer.nickname }} → {{ order.seller.nickname }}</div>
          <div class="order-price">¥{{ order.amount }}</div>
        </div>
      </div>

      <!-- 进度时间线 -->
      <div class="timeline-card">
        <div class="timeline-title">服务进展</div>
        <div class="timeline-steps">
          <div v-for="(step, idx) in steps" :key="idx" :class="['step-item', { active: step.done }]">
            <div class="step-dot">
              <van-icon v-if="step.done" name="success" />
              <span v-else>{{ idx + 1 }}</span>
            </div>
            <div class="step-content">
              <div class="step-label">{{ step.label }}</div>
              <div v-if="step.time" class="step-time">{{ step.time }}</div>
              <div v-if="step.sub" class="step-sub">{{ step.sub }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 角色标识 -->
      <div class="role-tag-card">
        <div class="role-row">
          <span class="role-badge buyer">买方</span>
          <span>{{ order.buyer.nickname }}</span>
        </div>
        <div class="role-row">
          <span class="role-badge seller">卖方</span>
          <span>{{ order.seller.nickname }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'
import { getService } from '@/utils/api'
import api from '@/utils/api'

const route = useRoute()
const router = useRouter()
const order = ref(null)
const loading = ref(true)
const error = ref('')
const defaultAvatar = 'https://randomuser.me/api/portraits/women/44.jpg'

const steps = computed(() => {
  if (!order.value) return []
  const o = order.value
  return [
    { label: '已预约', done: true, time: o.created_at ? formatTime(o.created_at) : '', sub: '预约已提交' },
    { label: '已确认', done: o.status !== 'pending', time: o.created_at ? formatTime(o.created_at) : '', sub: '双方确认中' },
    { label: '服务中', done: !!(o.buyer_checkin_time || o.seller_checkin_time), time: formatTime(o.buyer_checkin_time || o.seller_checkin_time), sub: '已打卡开始服务' },
    { label: '已完成', done: o.status === 'completed', time: formatTime(o.buyer_checkout_time || o.seller_checkout_time), sub: '双方打卡结束' },
  ]
})

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) { showToast('请先登录'); return router.push('/login') }
  await loadOrder()
})

async function loadOrder() {
  try {
    const svcRes = await getService(route.params.id)
    const svc = svcRes.data || svcRes

    if (!svc.is_booked) {
      error.value = '该服务尚未被预约'
      loading.value = false
      return
    }

    if (!svc.is_self_order) {
      showToast('已被邀约')
      router.replace('/')
      return
    }

    // 获取订单详情
    const ordRes = await api.get(`/orders/${svc.order_id}`)
    const orderData = ordRes.data || ordRes
    if (!orderData) {
      error.value = '订单数据加载失败'
      loading.value = false
      return
    }
    order.value = orderData
  } catch (err) {
    error.value = err.response?.data?.detail || '加载失败'
  } finally { loading.value = false }
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getMonth() + 1}/${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
</script>

<style scoped>
.progress-page { padding-bottom: 20px; }
.loading-wrap { display: flex; justify-content: center; padding: 60px 0; }
.error-wrap { padding: 40px 0; text-align: center; }

/* Order summary */
.order-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  padding: 20px 16px;
  margin-bottom: 10px;
}
.order-summary-info { flex: 1; }
.order-service-title { font-size: 16px; font-weight: 700; }
.order-meta { font-size: 12px; color: #999; margin-top: 3px; }
.order-price { font-size: 20px; font-weight: 800; color: #ee0a24; margin-top: 4px; }

/* Timeline */
.timeline-card {
  background: #fff;
  padding: 20px 16px;
  margin-bottom: 10px;
}
.timeline-title { font-size: 16px; font-weight: 700; margin-bottom: 20px; padding-left: 10px; border-left: 3px solid #667eea; }

.timeline-steps {
  position: relative;
  padding-left: 8px;
}
.step-item {
  display: flex;
  gap: 14px;
  padding-bottom: 24px;
  position: relative;
}
.step-item:last-child { padding-bottom: 0; }
.step-item::before {
  content: '';
  position: absolute;
  left: 20px;
  top: 30px;
  bottom: 0;
  width: 2px;
  background: #e8e8e8;
}
.step-item:last-child::before { display: none; }
.step-item.active::before { background: #667eea; }

.step-dot {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: #999;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}
.step-item.active .step-dot {
  background: #667eea;
  color: #fff;
}

.step-content { flex: 1; padding-top: 4px; }
.step-label { font-size: 15px; font-weight: 600; color: #999; }
.step-item.active .step-label { color: #333; }
.step-time { font-size: 12px; color: #999; margin-top: 2px; }
.step-sub { font-size: 12px; color: #999; margin-top: 1px; }

/* Roles */
.role-tag-card {
  background: #fff;
  padding: 14px 16px;
  margin-bottom: 10px;
}
.role-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 0;
  font-size: 14px;
}
.role-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}
.role-badge.buyer { background: #e8f5e9; color: #2e7d32; }
.role-badge.seller { background: #fff3e0; color: #e65100; }
</style>
