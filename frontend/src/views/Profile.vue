<template>
  <div class="page profile-page">
    <!-- 蓝色渐变横幅 -->
    <div class="hero-banner">
      <div class="hero-bg">
        <div class="hero-top">
          <span class="hero-back" @click="$router.back()">
            <van-icon name="arrow-left" />
          </span>
          <span class="hero-title">个人中心</span>
          <span class="hero-spacer"></span>
        </div>
      </div>
      <svg class="banner-wave" viewBox="0 0 375 20" preserveAspectRatio="none">
        <path d="M0,8 Q47,0 94,8 T188,8 T282,8 T375,8 L375,20 L0,20 Z" fill="#f5f5f5"/>
      </svg>
    </div>

    <!-- Login prompt -->
    <div v-if="!isLoggedIn" class="login-prompt">
      <van-image round width="64" height="64" src="https://randomuser.me/api/portraits/women/44.jpg" />
      <div class="login-text">登录后查看更多内容</div>
      <van-button round type="primary" @click="$router.push('/login')">去登录</van-button>
    </div>

    <!-- Profile header card -->
    <div v-else class="profile-card-wrap">
      <div class="profile-card">
        <!-- Avatar + Info row -->
        <div class="profile-header-row">
          <div class="avatar-wrap" @click="$router.push('/profile')">
            <van-image round width="60" height="60" :src="user.avatar || defaultAvatar" />
          </div>
          <div class="profile-info">
            <div class="profile-name">{{ user.nickname || user.phone }}</div>
            <div class="profile-sub">{{ user.phone || '' }}</div>
            <div class="profile-tags">
              <div v-if="user.is_verified" class="verify-box">
                <van-icon name="certificate" /> 实名认证
              </div>
              <van-tag v-if="user.is_skill_verified" plain style="border-color:#667eea;color:#667eea">技能认证</van-tag>
              <div class="star-box">
                <van-icon v-for="s in 5" :key="s" :name="s <= (userRating)" color="#ff6b81" size="14" />
                <span class="star-text">{{ userRating.toFixed(1) }}</span>
              </div>
            </div>
          </div>
        </div>
        <!-- Stats -->
        <div class="stats-row">
          <div class="stat-item">
            <div class="stat-val">¥{{ user.cash_balance || 0 }}</div>
            <div class="stat-label">余额</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-val">{{ user.points_balance || 0 }}</div>
            <div class="stat-label">积分</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-val">{{ user.checkin_streak || 0 }}</div>
            <div class="stat-label">连续签到</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Menu list -->
    <van-cell-group :border="false" class="menu-group">
      <van-cell title="充值" icon="balance-pay" is-link @click="showRecharge = true" />
      <van-cell title="诚信认证" icon="star-o" is-link @click="$router.push('/certification')">
        <template #value>
          <span v-if="user.is_verified" style="color:#07c160">已认证</span>
          <span v-else style="color:#ee0a24">未认证</span>
        </template>
      </van-cell>
      <van-cell title="我的订单" icon="orders-o" is-link @click="$router.push('/orders')" />
      <van-cell title="发布的需求" icon="chat-o" is-link @click="$router.push('/demands')" />
      <van-cell title="发布的服务" icon="shop-o" is-link @click="$router.push('/services')" />
      <van-cell title="系统通知" icon="bell-o" is-link @click="$router.push('/notifications')" />
      <van-cell title="签到" icon="records-o" is-link @click="handleCheckin">
        <template #value>
          <span v-if="checkedIn" style="color:#07c160">已签到</span>
          <span v-else style="color:var(--primary)">去签到</span>
        </template>
      </van-cell>
    </van-cell-group>

    <!-- 充值弹窗 -->
    <van-action-sheet v-model:show="showRecharge" title="充值" close-on-popstate>
      <div class="recharge-sheet">
        <div class="recharge-presets">
          <div
            v-for="amt in rechargeAmounts"
            :key="amt"
            :class="['recharge-card', { active: selectedAmount === amt }]"
            @click="selectedAmount = amt"
          >
            <div class="recharge-amount">¥{{ amt }}</div>
            <div v-if="amt >= 100" class="recharge-bonus">送 ¥{{ Math.floor(amt * 0.05) }}</div>
          </div>
        </div>
        <div class="recharge-input-row">
          <span class="recharge-label">自定义金额</span>
          <div class="recharge-input-wrap">
            <span class="recharge-sign">¥</span>
            <input v-model.number="customAmount" class="recharge-input" placeholder="其他金额" type="number" min="1" />
          </div>
        </div>
        <van-button
          round
          block
          class="recharge-btn"
          :loading="recharging"
          @click="handleRecharge"
        >{{ recharging ? '充值中...' : '确认充值' }}</van-button>
        <div class="recharge-tip">⚡ 充值后金额实时到账，可用于下单支付</div>
      </div>
    </van-action-sheet>

    <!-- Sign out button -->
    <div v-if="isLoggedIn" style="margin: 24px 16px">
      <van-button round block plain type="danger" @click="handleLogout">
        退出登录
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast, showConfirmDialog } from 'vant'
import { getMe, doCheckin, getCheckinStatus, recharge } from '@/utils/api'

const router = useRouter()
const user = ref({})
const checkedIn = ref(false)
const defaultAvatar = 'https://randomuser.me/api/portraits/women/44.jpg'
const userRating = ref(4.8)
const showRecharge = ref(false)
const recharging = ref(false)
const selectedAmount = ref(0)
const customAmount = ref(null)
const rechargeAmounts = [50, 100, 200, 500, 1000]

const isLoggedIn = computed(() => !!localStorage.getItem('token'))

onMounted(async () => {
  if (isLoggedIn.value) {
    await loadUser()
    await loadCheckinStatus()
  }
})

async function loadUser() {
  try {
    const res = await getMe()
    const u = res.data || res
    user.value = u
    localStorage.setItem('user', JSON.stringify(u))
  } catch { /* ignore */ }
}

async function loadCheckinStatus() {
  try {
    const res = await getCheckinStatus()
    const d = res.data || res
    checkedIn.value = d.checked_in === true
  } catch { /* ignore */ }
}

async function handleCheckin() {
  if (checkedIn.value) {
    showToast('今日已签到')
    return
  }
  showLoadingToast({ message: '签到中...', forbidClick: true })
  try {
    await doCheckin()
    checkedIn.value = true
    showToast('签到成功')
    await loadUser()
  } catch (err) {
    const msg = err.response?.data?.message || err.message || '签到失败'
    showToast(msg)
  } finally {
    closeToast()
  }
}

async function handleLogout() {
  try {
    await showConfirmDialog({ message: '确定要退出登录吗？' })
  } catch { return }
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  showToast('已退出')
  router.push('/login')
}

async function handleRecharge() {
  const amount = selectedAmount.value || customAmount.value
  if (!amount || amount <= 0) {
    showToast('请选择或输入充值金额')
    return
  }
  recharging.value = true
  showLoadingToast({ message: '充值中...', forbidClick: true })
  try {
    const res = await recharge(amount)
    const data = res.data || res
    showToast(data.message || '充值成功')
    user.value.cash_balance = data.balance
    localStorage.setItem('user', JSON.stringify(user.value))
    showRecharge.value = false
    selectedAmount.value = 0
    customAmount.value = null
  } catch (err) {
    const msg = err.response?.data?.detail || err.response?.data?.message || err.message || '充值失败'
    showToast(msg)
  } finally {
    recharging.value = false
    closeToast()
  }
}
</script>

<style scoped>
.profile-page {
  padding-bottom: 12px;
}

/* ============ 蓝色渐变横幅 ============ */
.hero-banner {
  position: relative;
}
.hero-bg {
  background: linear-gradient(135deg, #f9536c 0%, #ff6f91 100%);
  padding: 12px 16px 18px;
}
.hero-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #fff;
}
.hero-back {
  font-size: 20px;
  cursor: pointer;
  padding: 4px;
}
.hero-title {
  font-size: 17px;
  font-weight: 700;
}
.hero-spacer { width: 28px; }
.banner-wave {
  display: block;
  width: 100%;
  height: 16px;
  margin-bottom: -1px;
}

/* ============ 登录提示 ============ */
.login-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 0;
  gap: 12px;
}
.login-text { font-size: 14px; color: #999; }

/* ============ 用户资料卡片 ============ */
.profile-card-wrap {
  margin: -8px 12px 12px;
  position: relative;
  z-index: 2;
}
.profile-card {
  background: #fff;
  border-radius: 14px;
  padding: 20px 16px;
  box-shadow: 0 2px 12px rgba(102,126,234,0.15);
}

/* Avatar + Info */
.profile-header-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}
.avatar-wrap {
  flex-shrink: 0;
  cursor: pointer;
}
.profile-info {
  flex: 1;
}
.profile-name {
  font-size: 17px;
  font-weight: 700;
}
.profile-sub {
  font-size: 13px;
  color: #999;
  margin-top: 3px;
}
.profile-tags {
  display: flex;
  gap: 6px;
  margin-top: 6px;
  flex-wrap: wrap;
}

/* Stats — blue gradient */
.stats-row {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #f9536c 0%, #ff6f91 100%);
  border-radius: 10px;
  padding: 14px 0;
}
.stat-item {
  flex: 1;
  text-align: center;
  color: #fff;
}
.stat-val {
  font-size: 18px;
  font-weight: 700;
}
.stat-label {
  font-size: 11px;
  opacity: 0.75;
  margin-top: 3px;
}
.stat-divider {
  width: 1px;
  height: 28px;
  background: rgba(255,255,255,0.25);
}

/* ============ 菜单 ============ */
.menu-group {
  margin: 0 12px;
  border-radius: 12px;
  overflow: hidden;
}
.menu-group :deep(.van-cell) {
  align-items: center;
}

/* ============ 认证标签 ============ */
.verify-box {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: #667eea;
  background: rgba(102,126,234,0.08);
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid rgba(102,126,234,0.2);
}
.star-box {
  display: inline-flex;
  align-items: center;
  gap: 1px;
}
.star-text {
  font-size: 11px;
  color: #ff6b81;
  margin-left: 2px;
  font-weight: 600;
}

/* ============ 充值弹窗 ============ */
.recharge-sheet {
  padding: 16px;
}
.recharge-presets {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  margin-bottom: 16px;
}
.recharge-card {
  background: #f5f5f5;
  border-radius: 10px;
  padding: 14px 8px;
  text-align: center;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.15s;
}
.recharge-card.active {
  background: rgba(249,83,108,0.06);
  border-color: #f9536c;
}
.recharge-amount {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}
.recharge-card.active .recharge-amount {
  color: #f9536c;
}
.recharge-bonus {
  font-size: 11px;
  color: #ff6b81;
  margin-top: 3px;
}
.recharge-input-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.recharge-label {
  font-size: 14px;
  color: #666;
  flex-shrink: 0;
}
.recharge-input-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 0 12px;
}
.recharge-sign {
  font-size: 16px;
  color: #999;
  margin-right: 4px;
}
.recharge-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
  padding: 10px 0;
  width: 100%;
}
.recharge-btn {
  background: linear-gradient(135deg, #f9536c, #ff6f91) !important;
  color: #fff !important;
  border: none !important;
  height: 44px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
}
.recharge-tip {
  text-align: center;
  font-size: 12px;
  color: #999;
  margin-top: 12px;
  margin-bottom: 20px;
}
</style>
