<template>
  <div class="page service-detail-page">
    <van-nav-bar title="服务详情" left-arrow @click-left="$router.back()" />

    <div v-if="loading" class="loading-wrap"><van-loading size="24px">加载中...</van-loading></div>

    <template v-else-if="svc">
      <!-- 封面/头像大图 -->
      <div class="cover-section">
        <van-image width="100%" height="220" fit="cover" :src="svc.seller?.avatar || defaultAvatar" />
        <div v-if="svc.is_booked" class="booked-stamp">已被约</div>
        <div class="cover-overlay">
          <div class="cover-price">¥{{ svc.price }}</div>
          <div class="cover-unit">/次</div>
        </div>
      </div>

      <!-- 基本信息 -->
      <div class="info-card">
        <div class="info-title">{{ svc.title }}</div>
        <div class="info-tags">
          <van-tag plain style="border-color:#ff4757;color:#ff4757">{{ svc.skill_type }}</van-tag>
          <span v-if="svc.location" class="info-tag">📍 {{ svc.location }}</span>
          <span v-if="svc.duration" class="info-tag">⏱ {{ svc.duration }}</span>
        </div>
      </div>

      <!-- 卖家信息 -->
      <div class="seller-card" @click="$router.push(`/users/${svc.seller.id}`)">
        <van-image round width="52" height="52" :src="svc.seller?.avatar || defaultAvatar" />
        <div class="seller-info">
          <div class="seller-name">
            {{ svc.seller.nickname }}
            <van-icon v-if="svc.seller.is_skill_verified" name="verified" color="#667eea" />
          </div>
          <div class="seller-sub">
            {{ sellerAge }}岁 · {{ genderLabel }}
            <template v-if="svc.seller.residence_city"> · {{ svc.seller.residence_city }}</template>
          </div>
          <div class="seller-stats">
            <span>⭐ {{ svc.seller_rating_avg || '暂无' }}</span>
            <span class="stat-divider">|</span>
            <span>{{ svc.seller_service_count || 0 }} 服务</span>
            <span class="stat-divider">|</span>
            <span>{{ svc.order_count || 0 }} 单成交</span>
          </div>
        </div>
        <van-icon name="arrow" style="color:#ccc" />
      </div>

      <!-- 服务描述 -->
      <div class="section-card">
        <div class="section-title">服务描述</div>
        <div class="desc-text">{{ svc.description }}</div>
      </div>

      <!-- 图片 -->
      <div v-if="svc.images && svc.images.length > 0" class="section-card">
        <div class="section-title">服务展示</div>
        <div class="image-grid">
          <van-image v-for="(img, idx) in svc.images" :key="idx"
            width="100%" height="180" fit="cover" :src="img"
            class="svc-image" @click="previewImage(idx)" />
        </div>
      </div>

      <!-- 评价 -->
      <div v-if="svc.ratings && svc.ratings.length > 0" class="section-card">
        <div class="section-title">用户评价 ({{ svc.seller_rating_count }})</div>
        <div class="rating-summary">
          <div class="rating-score">{{ svc.seller_rating_avg }}</div>
          <div class="rating-stars">
            <van-icon v-for="s in fullStars" :key="s" name="star" color="#ff6b81" size="16" />
            <van-icon v-if="hasHalfStar" name="star-half" color="#ff6b81" size="16" />
            <van-icon v-for="s in emptyStars" :key="'e'+s" name="star-o" color="#dcdee0" size="16" />
          </div>
        </div>
        <div v-for="r in svc.ratings" :key="r.id" class="rating-item">
          <div class="rating-header">
            <van-image round width="24" height="24" :src="r.rater_avatar || defaultAvatar" />
            <span class="rating-user">{{ r.rater_nickname }}</span>
            <span class="rating-date">{{ formatTime(r.created_at) }}</span>
          </div>
          <div class="rating-stars-row">
            <van-icon v-for="s in r.score" :key="s" name="star" color="#ff6b81" size="12" />
            <van-icon v-for="s in (5 - r.score)" :key="'e'+s" name="star-o" color="#dcdee0" size="12" />
          </div>
          <div v-if="r.comment" class="rating-comment">「{{ r.comment }}」</div>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="bottom-actions">
        <div class="action-btn" @click="handleFavorite">
          <van-icon :name="isFav ? 'like' : 'like-o'" :color="isFav ? '#ff4757' : '#666'" size="22" />
          <span>{{ isFav ? '已收藏' : '收藏' }}</span>
        </div>
        <template v-if="svc.is_booked && svc.is_self_order">
          <van-button round class="order-btn-big progress-btn" @click="goToProgress">
            查看服务进度
          </van-button>
        </template>
        <template v-else-if="svc.is_booked">
          <van-button round class="order-btn-big disabled-btn" disabled>
            已被预约
          </van-button>
        </template>
        <template v-else>
          <van-button round class="order-btn-big" @click="handleOrder">
            立即预约 · ¥{{ svc.price }}
          </van-button>
        </template>
      </div>

      <!-- 图片预览 -->
      <van-image-preview v-model:show="showPreview" :start-position="previewIdx" :images="svc.images || []" />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { getService, toggleFavorite, checkFavorite } from '@/utils/api'

const route = useRoute()
const router = useRouter()
const svc = ref(null)
const loading = ref(true)
const isFav = ref(false)
const showPreview = ref(false)
const previewIdx = ref(0)
const defaultAvatar = 'https://randomuser.me/api/portraits/women/44.jpg'

const sellerAge = computed(() => {
  if (svc.value?.seller?.birth_date) {
    const birth = new Date(svc.value.seller.birth_date)
    return new Date().getFullYear() - birth.getFullYear()
  }
  return '??'
})

const genderLabel = computed(() => {
  const g = svc.value?.seller?.gender
  return g === 'female' ? '女' : g === 'male' ? '男' : ''
})

const fullStars = computed(() => Math.floor(svc.value?.seller_rating_avg || 0))
const hasHalfStar = computed(() => (svc.value?.seller_rating_avg || 0) % 1 >= 0.5)
const emptyStars = computed(() => 5 - fullStars.value - (hasHalfStar.value ? 1 : 0))

onMounted(async () => {
  await loadService()
  await checkFavStatus()
})

async function loadService() {
  try {
    const res = await getService(route.params.id)
    svc.value = res.data || res
  } catch {
    showToast('服务不存在')
    router.back()
  } finally {
    loading.value = false
  }
}

async function checkFavStatus() {
  const token = localStorage.getItem('token')
  if (!token) return
  try {
    const res = await checkFavorite('service', Number(route.params.id))
    isFav.value = res.status === 'favorited' || res.favorited === true
  } catch { /* ignore */ }
}

function previewImage(idx) {
  previewIdx.value = idx
  showPreview.value = true
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  const now = new Date()
  const pad = n => String(n).padStart(2, '0')
  const diff = now - d
  const min = 60 * 1000
  const hour = 60 * min
  const day = 24 * hour
  if (diff < min) return '刚刚'
  if (diff < hour) return `${Math.floor(diff / min)}分钟前`
  if (diff < day) return `${Math.floor(diff / hour)}小时前`
  if (diff < 2 * day) return '昨天'
  return `${pad(d.getMonth() + 1)}/${pad(d.getDate())}`
}

async function handleFavorite() {
  if (!localStorage.getItem('token')) {
    showToast('请先登录')
    return router.push('/login')
  }
  try {
    const res = await toggleFavorite('service', svc.value.id)
    const status = res.status || (res.data && res.data.status)
    isFav.value = status === 'favorited'
    showToast(isFav.value ? '已收藏' : '取消收藏')
  } catch {
    showToast('操作失败')
  }
}

async function handleOrder() {
  if (!localStorage.getItem('token')) {
    showToast('请先登录')
    return router.push('/login')
  }
  router.push(`/services/${svc.value.id}/pay`)
}

function goToProgress() {
  router.push(`/services/${svc.value.id}/progress`)
}
</script>

<style scoped>
.service-detail-page {
  padding-bottom: 80px;
}
.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

/* Cover */
.cover-section {
  position: relative;
  margin: 0;
}
.booked-stamp {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 2;
  transform: rotate(15deg);
  background: rgba(238, 10, 36, 0.85);
  color: #fff;
  font-size: 18px;
  font-weight: 800;
  padding: 6px 18px;
  border-radius: 4px;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  letter-spacing: 2px;
}
.cover-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: linear-gradient(transparent, rgba(0,0,0,0.7));
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.cover-price {
  font-size: 28px;
  font-weight: 800;
  color: #fff;
  text-shadow: 0 2px 6px rgba(0,0,0,0.3);
}
.cover-unit {
  font-size: 14px;
  color: rgba(255,255,255,0.8);
}

/* Info card */
.info-card {
  background: #fff;
  padding: 16px;
  margin-bottom: 10px;
}
.info-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
}
.info-tags {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.info-tag {
  font-size: 12px;
  color: #999;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 4px;
}

/* Seller card */
.seller-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  padding: 14px 16px;
  margin-bottom: 10px;
  cursor: pointer;
}
.seller-card:active { opacity: 0.8; }
.seller-info { flex: 1; }
.seller-name {
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
}
.seller-sub {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}
.seller-stats {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}
.stat-divider { color: #ddd; }

/* Section */
.section-card {
  background: #fff;
  padding: 16px;
  margin-bottom: 10px;
}
.section-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 10px;
  padding-left: 10px;
  border-left: 3px solid #667eea;
}
.desc-text {
  font-size: 14px;
  color: #333;
  line-height: 1.8;
  white-space: pre-wrap;
}

/* Images */
.image-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}
.svc-image { border-radius: 6px; overflow: hidden; cursor: pointer; }
.svc-image:active { opacity: 0.8; }

/* Ratings */
.rating-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.rating-score {
  font-size: 28px;
  font-weight: 800;
  color: #ff6b81;
  line-height: 1;
}
.rating-stars { display: flex; gap: 2px; }
.rating-item {
  padding: 10px 0;
  border-top: 1px solid #f5f5f5;
}
.rating-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.rating-user { font-size: 13px; font-weight: 500; }
.rating-date { font-size: 11px; color: #999; margin-left: auto; }
.rating-stars-row { display: flex; gap: 1px; margin-bottom: 4px; }
.rating-comment {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

/* Bottom actions */
.bottom-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  padding: 10px 16px;
  padding-bottom: calc(10px + env(safe-area-inset-bottom));
  box-shadow: 0 -2px 8px rgba(0,0,0,0.06);
  z-index: 100;
}
.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  cursor: pointer;
  padding: 0 8px;
}
.action-btn span { font-size: 11px; color: #666; }
.order-btn-big {
  flex: 1;
  background: linear-gradient(135deg, #ff4757, #ff6b81) !important;
  color: #fff !important;
  border: none !important;
  height: 44px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
}
</style>
