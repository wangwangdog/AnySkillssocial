<template>
  <div class="page">
    <van-nav-bar title="订单详情" left-arrow @click-left="$router.back()" />

    <div v-if="loading" class="loading-wrap"><van-loading /></div>

    <template v-else-if="order">
      <!-- Status header -->
      <div class="status-header" :style="{ background: statusBg }">
        <van-icon :name="statusIcon" size="40" />
        <div class="status-text">{{ statusLabel }}</div>
        <div class="status-hint">{{ statusHint }}</div>
      </div>

      <!-- Order info -->
      <div class="section-card">
        <div class="section-title">订单信息</div>
        <div class="info-row"><span class="info-label">订单号</span><span>{{ order.order_no }}</span></div>
        <div class="info-row"><span class="info-label">类型</span><span>{{ order.order_type === 'service' ? '服务下单' : '需求匹配' }}</span></div>
        <div class="info-row"><span class="info-label">金额</span><span style="color:#ee0a24;font-weight:600">¥{{ order.amount }}</span></div>
        <div class="info-row"><span class="info-label">状态</span><van-tag :type="tagType(order.status)">{{ statusText(order.status) }}</van-tag></div>
        <div class="info-row"><span class="info-label">创建时间</span><span>{{ formatTime(order.created_at) }}</span></div>
      </div>

      <!-- Buyer/Seller -->
      <div class="section-card">
        <div class="section-title">参与方</div>
        <div class="party-row" @click="$router.push(`/users/${order.seller?.id}`)">
          <van-image round width="36" height="36" :src="order.seller?.avatar || defaultAvatar" />
          <div class="party-info">
            <div class="party-name">{{ order.seller?.nickname || '卖家' }}</div>
            <div class="party-role">服务方</div>
          </div>
          <van-icon name="arrow" style="color:#ccc" />
        </div>
        <div class="party-divider"></div>
        <div class="party-row" @click="$router.push(`/users/${order.buyer?.id}`)">
          <van-image round width="36" height="36" :src="order.buyer?.avatar || defaultAvatar" />
          <div class="party-info">
            <div class="party-name">{{ order.buyer?.nickname || '买家' }}</div>
            <div class="party-role">需求方</div>
          </div>
          <van-icon name="arrow" style="color:#ccc" />
        </div>
      </div>

      <!-- Visual flow chart -->
      <div class="section-card">
        <div class="section-title">订单进度</div>
        <div class="flow-chart">
          <div
            v-for="(step, idx) in flowSteps"
            :key="idx"
            :class="['flow-node', step.status]"
          >
            <div class="flow-icon">
              <van-icon :name="step.icon" :color="stepColor(step.status)" />
            </div>
            <div class="flow-label">{{ step.label }}</div>
            <div class="flow-time">{{ step.time || step.hint }}</div>
            <!-- Connector line -->
            <div v-if="idx < flowSteps.length - 1" :class="['flow-line', step.status]"></div>
          </div>
        </div>
      </div>

      <!-- Detailed checkin/checkout info -->
      <div class="section-card">
        <div class="section-title">服务记录</div>
        <div class="record-row">
          <span class="record-label"><van-icon name="orders-o" /> 订单号</span>
          <span class="record-value">{{ order.order_no }}</span>
        </div>
        <div class="record-row">
          <span class="record-label"><van-icon name="clock-o" /> 创建时间</span>
          <span class="record-value">{{ formatTime(order.created_at) }}</span>
        </div>
        <div class="record-divider"></div>
        <div class="record-row">
          <span class="record-label"><van-icon name="location-o" /> 买家签到</span>
          <span class="record-value">{{ formatTime(order.buyer_checkin_time) || '—' }}</span>
        </div>
        <div class="record-row">
          <span class="record-label"><van-icon name="location-o" /> 卖家签到</span>
          <span class="record-value">{{ formatTime(order.seller_checkin_time) || '—' }}</span>
        </div>
        <div class="record-divider"></div>
        <div class="record-row">
          <span class="record-label"><van-icon name="success" /> 买家完成</span>
          <span class="record-value">{{ formatTime(order.buyer_checkout_time) || '—' }}</span>
        </div>
        <div class="record-row">
          <span class="record-label"><van-icon name="success" /> 卖家完成</span>
          <span class="record-value">{{ formatTime(order.seller_checkout_time) || '—' }}</span>
        </div>
        <div v-if="order.settled_at" class="record-row settled">
          <span class="record-label"><van-icon name="gold-coin-o" /> 结算时间</span>
          <span class="record-value">{{ formatTime(order.settled_at) }}</span>
        </div>
      </div>

      <!-- Action buttons -->
      <div class="action-bar">
        <!-- 签到 -->
        <van-button
          v-if="canCheckin"
          round
          block
          type="primary"
          size="large"
          :loading="actionLoading"
          @click="handleCheckin"
        >
          📍 签到开始服务
        </van-button>
        <!-- 完成 -->
        <van-button
          v-if="canCheckout"
          round
          block
          style="background:linear-gradient(135deg,#ff4757,#ff6b81);color:#fff;border:none"
          size="large"
          :loading="actionLoading"
          @click="handleCheckout"
        >
          ✅ 确认完成服务
        </van-button>
        <!-- 私信 -->
        <van-button
          v-if="otherUserId"
          round
          block
          plain
          size="large"
          style="margin-top:8px;border-color:#ff4757;color:#ff4757"
          @click="contactOther"
        >
          💬 联系对方
        </van-button>
      </div>

      <!-- Rating card (completed orders only) -->
      <div v-if="order.status === 'completed'" class="section-card rating-card">
        <div class="section-title">服务评价</div>
        
        <!-- Already rated -->
        <div v-if="myRating" class="rated-section">
          <div class="rated-stars">
            <van-icon v-for="s in 5" :key="s" :name="s <= myRating.score ? 'star' : 'star-o'" :color="s <= myRating.score ? '#ff6b81' : '#dcdee0'" size="22" />
          </div>
          <div class="rated-label">你的评分：{{ myRating.score }} 分</div>
          <div v-if="myRating.comment" class="rated-comment">「{{ myRating.comment }}」</div>
        </div>
        
        <!-- Not yet rated -->
        <div v-else class="to-rate-section">
          <div class="rate-prompt">服务已结束，请给服务方评分</div>
          <van-button 
            round 
            size="small" 
            style="background:linear-gradient(135deg,#ff4757,#ff6b81);color:#fff;border:none"
            @click="showRateSheet = true"
          >
            ⭐ 去评价
          </van-button>
        </div>
      </div>

      <!-- Rating sheet -->
      <van-action-sheet v-model:show="showRateSheet" title="给服务方评分" closeable>
        <div class="rate-sheet-body">
          <div class="rate-ratee">
            评价对象：<strong>{{ otherNickname }}</strong>
          </div>
          <div class="rate-stars">
            <van-icon
              v-for="s in 5"
              :key="s"
              :name="s <= rateScore ? 'star' : 'star-o'"
              :color="s <= rateScore ? '#ff6b81' : '#dcdee0'"
              size="36"
              style="cursor:pointer"
              @click="rateScore = s"
            />
          </div>
          <div class="rate-score-label">{{ scoreLabels[rateScore - 1] }}</div>
          <van-field
            v-model="rateComment"
            type="textarea"
            placeholder="说说你的体验（选填）"
            rows="3"
            maxlength="200"
            show-word-limit
          />
          <div style="margin:16px 0">
            <van-button 
              round 
              block
              style="background:linear-gradient(135deg,#ff4757,#ff6b81);color:#fff;border:none"
              @click="submitRating"
            >
              提交评价
            </van-button>
          </div>
        </div>
      </van-action-sheet>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast, showConfirmDialog } from 'vant'
import { getOrder, checkinOrder, checkoutOrder, sendMessage, rateOrder } from '@/utils/api'

const route = useRoute()
const router = useRouter()
const order = ref(null)
const loading = ref(true)
const actionLoading = ref(false)
const showRateSheet = ref(false)
const rateScore = ref(5)
const rateComment = ref('')
const defaultAvatar = 'https://randomuser.me/api/portraits/women/44.jpg'

const me = computed(() => {
  const stored = localStorage.getItem('user')
  return stored ? JSON.parse(stored) : null
})

const otherUserId = computed(() => {
  if (!order.value || !me.value) return null
  return order.value.seller?.id === me.value.id ? order.value.buyer?.id : order.value.seller?.id
})

const canCheckin = computed(() => {
  if (!order.value) return false
  return order.value.status === 'confirmed' || order.value.status === 'in_progress'
})

const canCheckout = computed(() => {
  if (!order.value) return false
  return order.value.status === 'in_progress'
})



const statusIcon = computed(() => {
  const map = { pending: 'clock-o', confirmed: 'passed', in_progress: 'smile-o', completed: 'success', cancelled: 'fail' }
  return map[order.value?.status] || 'info-o'
})

const statusLabel = computed(() => {
  const map = { pending: '等待处理', confirmed: '已确认', in_progress: '服务中', completed: '已完成', cancelled: '已取消' }
  return map[order.value?.status] || order.value?.status
})

const isBuyer = computed(() => me.value?.id === order.value?.buyer?.id)
const myRating = computed(() => {
  if (!order.value?.rating) return null
  return order.value.rating
})
const otherNickname = computed(() => {
  if (!order.value) return ''
  return isBuyer.value ? order.value.seller?.nickname : order.value.buyer?.nickname
})
const scoreLabels = ['很差', '较差', '一般', '满意', '非常满意']

// Flow chart stages
const flowSteps = computed(() => {
  if (!order.value) return []
  const stages = [
    { key: 'placed', icon: 'passed', label: '下单成功', status: 'done', time: '', hint: '' },
    { key: 'confirmed', icon: 'records-o', label: '已确认接单', status: 'pending', time: '', hint: '' },
    { key: 'checked_in', icon: 'location-o', label: '服务签到', status: 'pending', time: '', hint: '' },
    { key: 'checked_out', icon: 'success', label: '确认完成', status: 'pending', time: '', hint: '' },
    { key: 'settled', icon: 'gold-coin-o', label: '订单结算', status: 'pending', time: '', hint: '' },
  ]

  const s = order.value.status

  // Stage 1: placed - always done
  stages[0].status = 'done'
  stages[0].time = formatTime(order.value.created_at)

  // Stage 2: confirmed
  if (s === 'confirmed' || s === 'in_progress' || s === 'completed') {
    stages[1].status = 'done'
    stages[1].time = formatTime(order.value.created_at)
  } else {
    stages[1].status = 'active'
    stages[1].hint = '等待接单'
  }

  // Stage 3: checked in
  const checkedIn = order.value.buyer_checkin_time || order.value.seller_checkin_time
  if (checkedIn) {
    stages[2].status = 'done'
    stages[2].time = formatTime(checkedIn)
  } else if (s === 'confirmed' || s === 'in_progress') {
    stages[2].status = 'active'
    stages[2].hint = '等待签到'
  }

  // Stage 4: checked out
  const bothCheckedOut = order.value.buyer_checkout_time && order.value.seller_checkout_time
  if (bothCheckedOut) {
    stages[3].status = 'done'
    stages[3].time = formatTime(order.value.buyer_checkout_time)
  } else if (s === 'in_progress') {
    stages[3].status = 'active'
    stages[3].hint = '等待确认完成'
  }

  // Stage 5: settled
  if (s === 'completed') {
    stages[4].status = 'done'
    stages[4].time = formatTime(order.value.settled_at || order.value.buyer_checkout_time)
    // Mark all previous as done too
    stages.forEach(st => { if (st.status === 'pending') st.status = 'done' })
  }

  return stages
})

function stepColor(status) {
  if (status === 'done') return '#07c160'
  if (status === 'active') return '#ff4757'
  return '#dcdee0'
}

const statusHint = computed(() => {
  if (!order.value) return ''
  const s = order.value.status
  const buyer = order.value.buyer?.nickname || '买家'
  const seller = order.value.seller?.nickname || '卖家'
  const role = isBuyer.value ? buyer : seller

  if (s === 'confirmed') {
    return isBuyer.value
      ? `订单已确认，请签到开始服务（卖家 ${seller} 将收到通知）`
      : `订单已确认，买家 ${buyer} 签到后服务开始`
  }
  if (s === 'in_progress') {
    const buyerChecked = !!order.value.buyer_checkin_time
    const sellerChecked = !!order.value.seller_checkin_time
    if (isBuyer.value) {
      return buyerChecked
        ? `已签到，等待 ${seller} 确认完成服务`
        : '请签到开始服务'
    } else {
      return sellerChecked
        ? `已签到，等待 ${buyer} 确认完成服务`
        : '请签到开始服务'
    }
  }
  if (s === 'completed') return '服务已结束，感谢使用'
  return ''
})

const statusBg = computed(() => {
  if (order.value?.status === 'completed') return 'linear-gradient(135deg, #07c160, #10b981)'
  if (order.value?.status === 'in_progress') return 'linear-gradient(135deg, #ff4757, #ff6b81)'
  return 'linear-gradient(135deg, #ff4757, #ff6b81)'
})

function tagType(s) {
  const map = { pending: 'warning', confirmed: 'primary', in_progress: 'primary', completed: 'success', cancelled: 'danger' }
  return map[s] || 'default'
}

function statusText(s) {
  const map = { pending: '待处理', confirmed: '已确认', in_progress: '服务中', completed: '已完成', cancelled: '已取消' }
  return map[s] || s
}

onMounted(async () => {
  await loadOrder()
})

async function loadOrder() {
  try {
    const res = await getOrder(route.params.id)
    order.value = res.data || res
  } catch {
    showToast('订单不存在')
  } finally {
    loading.value = false
  }
}

async function handleCheckin() {
  actionLoading.value = true
  showLoadingToast({ message: '签到中...', forbidClick: true })
  try {
    await checkinOrder(route.params.id, {})
    closeToast()
    showToast('签到成功，服务开始')
    await loadOrder()
  } catch (err) {
    const msg = err.response?.data?.detail || err.response?.data?.message || err.message || '签到失败'
    showToast(msg)
  } finally {
    closeToast()
    actionLoading.value = false
  }
}

async function handleCheckout() {
  try {
    await showConfirmDialog({ message: '确定已完成服务？确认后等待对方也确认即完成结算。' })
  } catch {
    return
  }
  actionLoading.value = true
  showLoadingToast({ message: '确认中...', forbidClick: true })
  try {
    const res = await checkoutOrder(route.params.id, {})
    closeToast()
    const rs = res.data || res
    if (rs.order_status === 'completed') {
      showToast('双方确认完成，服务已结算')
    } else {
      showToast('已确认完成，等待对方确认')
    }
    await loadOrder()
  } catch (err) {
    const msg = err.response?.data?.detail || err.response?.data?.message || err.message || '操作失败'
    showToast(msg)
  } finally {
    closeToast()
    actionLoading.value = false
  }
}

async function contactOther() {
  if (!otherUserId.value) return
  showLoadingToast({ message: '正在连接...', forbidClick: true })
  try {
    const res = await sendMessage(otherUserId.value, '您好，关于订单 #' + order.value.order_no)
    const d = res.data || res
    closeToast()
    router.push(`/chat/${d.conversation_id}`)
  } catch {
    closeToast()
    showToast('连接失败')
  }
}

async function submitRating() {
  showLoadingToast({ message: '提交评价...', forbidClick: true })
  try {
    await rateOrder(order.value.id, rateScore.value, rateComment.value)
    closeToast()
    showToast('评价成功')
    showRateSheet.value = false
    await loadOrder()
  } catch (err) {
    const msg = err.response?.data?.detail || err.response?.data?.message || err.message || '评价失败'
    showToast(msg)
  } finally {
    closeToast()
  }
}

function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN')
}
</script>

<style scoped>
.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}
.status-header {
  border-radius: 12px;
  padding: 24px;
  color: #fff;
  text-align: center;
  margin-bottom: 12px;
}
.status-text {
  font-size: 20px;
  font-weight: 700;
  margin-top: 8px;
}
.status-hint {
  font-size: 13px;
  opacity: 0.85;
  margin-top: 4px;
}
.section-card {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
}
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 13px;
}
.info-label {
  color: #999;
}
.party-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  cursor: pointer;
}
.party-info {
  flex: 1;
}
.party-name {
  font-size: 14px;
  font-weight: 500;
}
.party-role {
  font-size: 11px;
  color: #999;
}
.party-divider {
  height: 1px;
  background: #f0f0f0;
  margin: 4px 0;
}
.action-bar {
  padding: 16px 0;
}
/* Flow chart */
.flow-chart {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 8px 0;
  position: relative;
}
.flow-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
  text-align: center;
}
.flow-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  border: 2px solid #dcdee0;
  z-index: 1;
  transition: all 0.3s;
}
.flow-node.done .flow-icon {
  border-color: #07c160;
  background: #e8f5e9;
}
.flow-node.active .flow-icon {
  border-color: #ff4757;
  background: #fff5f7;
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255,71,87,0.3); }
  50% { box-shadow: 0 0 0 8px rgba(255,71,87,0); }
}
.flow-label {
  font-size: 11px;
  color: #999;
  margin-top: 6px;
  font-weight: 500;
}
.flow-node.done .flow-label { color: #07c160; }
.flow-node.active .flow-label { color: #ff4757; font-weight: 600; }
.flow-time {
  font-size: 9px;
  color: #ccc;
  margin-top: 2px;
}
.flow-node.done .flow-time { color: #07c160; }
.flow-line {
  position: absolute;
  top: 20px;
  left: 50%;
  width: 100%;
  height: 2px;
  background: #dcdee0;
  z-index: 0;
}
.flow-line.done {
  background: #07c160;
}
/* Record rows */
.record-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 13px;
}
.record-label {
  color: #999;
  display: flex;
  align-items: center;
  gap: 4px;
}
.record-value {
  color: #333;
  font-size: 12px;
}
.record-divider {
  height: 1px;
  background: #f5f5f5;
  margin: 4px 0;
}
.record-row.settled .record-value {
  color: #07c160;
  font-weight: 600;
}
/* Rating */
.rating-card {
  text-align: center;
}
.rated-section {
  padding: 8px 0;
}
.rated-stars {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-bottom: 8px;
}
.rated-label {
  font-size: 14px;
  color: #ff6b81;
  font-weight: 600;
}
.rated-comment {
  font-size: 13px;
  color: #666;
  margin-top: 6px;
  padding: 8px;
  background: #fff5f7;
  border-radius: 8px;
  font-style: italic;
}
.to-rate-section {
  padding: 12px 0;
}
.rate-prompt {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
}
.rate-sheet-body {
  padding: 16px 20px 30px;
}
.rate-ratee {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
}
.rate-stars {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 8px;
}
.rate-score-label {
  text-align: center;
  font-size: 13px;
  color: #ff6b81;
  margin-bottom: 16px;
}
</style>
