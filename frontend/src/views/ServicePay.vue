<template>
  <div class="page pay-page">
    <van-nav-bar title="确认预约" left-arrow @click-left="$router.back()" />

    <div v-if="loading" class="loading-wrap"><van-loading size="24px">加载中...</van-loading></div>

    <template v-else-if="svc">
      <!-- 服务摘要 -->
      <div class="summary-card">
        <van-image width="72" height="72" fit="cover" :src="svc.seller?.avatar || defaultAvatar" round />
        <div class="summary-info">
          <div class="summary-title">{{ svc.title }}</div>
          <div class="summary-seller">{{ svc.seller.nickname }} · {{ svc.skill_type }}</div>
          <div class="summary-price">¥{{ svc.price }}</div>
        </div>
      </div>

      <!-- 余额信息 -->
      <div class="balance-card">
        <div class="balance-row">
          <span>当前余额</span>
          <span class="balance-amount">¥{{ userBalance }}</span>
        </div>
        <div class="balance-row">
          <span>服务费用</span>
          <span class="cost-amount">- ¥{{ svc.price }}</span>
        </div>
        <div class="balance-divider"></div>
        <div class="balance-row balance-total">
          <span>支付后余额</span>
          <span :class="['total-amount', { 'negative': remaining < 0 }]">
            ¥{{ remaining }}
          </span>
        </div>
        <div v-if="remaining < 0" class="insufficient">⚠️ 余额不足，请先充值</div>
      </div>

      <!-- 确认按钮 -->
      <div style="padding: 20px 16px;">
        <van-button
          round
          block
          class="confirm-btn"
          :disabled="remaining < 0"
          :loading="submitting"
          @click="handlePay"
        >确认支付 ¥{{ svc.price }}</van-button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { getService, createOrder } from '@/utils/api'

const route = useRoute()
const router = useRouter()
const svc = ref(null)
const loading = ref(true)
const submitting = ref(false)
const userBalance = ref(0)
const defaultAvatar = 'https://randomuser.me/api/portraits/women/44.jpg'

const remaining = computed(() => userBalance.value - (svc.value?.price || 0))

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) { showToast('请先登录'); return router.push('/login') }
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  userBalance.value = user.cash_balance || 0
  await loadService()
})

async function loadService() {
  try {
    const res = await getService(route.params.id)
    svc.value = res.data || res
  } catch {
    showToast('服务不存在')
    router.back()
  } finally { loading.value = false }
}

async function handlePay() {
  submitting.value = true
  showLoadingToast({ message: '支付中...', forbidClick: true })
  try {
    const res = await createOrder({
      order_type: 'service',
      service_id: svc.value.id,
      seller_id: svc.value.seller.id,
    })
    const orderData = res.data || res
    closeToast()
    showToast('预约成功！')

    // 更新本地余额
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    user.cash_balance = (user.cash_balance || 0) - svc.value.price
    localStorage.setItem('user', JSON.stringify(user))

    router.replace(`/orders/${orderData.id}`)
  } catch (err) {
    closeToast()
    const msg = err.response?.data?.detail || '支付失败'
    showToast(msg)
  } finally { submitting.value = false }
}
</script>

<style scoped>
.pay-page { padding-bottom: 20px; }
.loading-wrap { display: flex; justify-content: center; padding: 60px 0; }

.summary-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  padding: 20px 16px;
  margin-bottom: 10px;
}
.summary-info { flex: 1; }
.summary-title { font-size: 16px; font-weight: 700; }
.summary-seller { font-size: 13px; color: #999; margin-top: 3px; }
.summary-price { font-size: 20px; font-weight: 800; color: #ee0a24; margin-top: 4px; }

.balance-card {
  background: #fff;
  padding: 16px;
  margin: 0 0 10px;
}
.balance-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 14px;
  color: #333;
}
.balance-amount { font-size: 18px; font-weight: 700; color: #07c160; }
.cost-amount { font-size: 16px; font-weight: 600; color: #ee0a24; }
.balance-divider { height: 1px; background: #f0f0f0; margin: 6px 0; }
.balance-total { padding: 8px 0; }
.total-amount { font-size: 18px; font-weight: 700; color: #07c160; }
.total-amount.negative { color: #ee0a24; }
.insufficient { font-size: 12px; color: #ee0a24; text-align: center; margin-top: 4px; }

.confirm-btn {
  background: linear-gradient(135deg, #ff4757, #ff6b81) !important;
  color: #fff !important;
  border: none !important;
  height: 48px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
}
.confirm-btn[disabled] { opacity: 0.5 !important; }
</style>
