<template>
  <div class="bounty-page">
    <!-- ===== Header ===== -->
    <div class="bounty-header">
      <div class="bh-left">
        <div class="bh-logo">T</div>
      </div>
      <div class="bh-title">悬赏大厅</div>
      <div class="bh-right">
        <div class="bh-phone" @click="onCall">
          <van-icon name="phone" size="14" color="#FFF" />
        </div>
        <div class="bh-bell" @click="$router.push('/notifications')">
          <van-icon name="bell" size="20" color="#FFF" />
          <span class="bh-bell-badge">2</span>
        </div>
      </div>
    </div>

    <!-- ===== Tab 切换：付费悬赏 / 找人陪 ===== -->
    <div class="bh-tabs">
      <div
        :class="['bh-tab', { active: activeTab === 'bounty' }]"
        @click="activeTab = 'bounty'"
      >付费悬赏</div>
      <div
        :class="['bh-tab', { active: activeTab === 'companion' }]"
        @click="activeTab = 'companion'"
      >找人陪</div>
    </div>

    <!-- ===== 二级分类标签云（仅 bounty 显示） ===== -->
    <div v-if="activeTab === 'bounty'" class="bh-tags">
      <div class="bh-tags-scroll">
        <span
          v-for="tag in tagList"
          :key="tag.value"
          :class="['bh-tag', { active: activeTag === tag.value }]"
          @click="activeTag = tag.value; reloadList()"
        >{{ tag.label }}</span>
      </div>
    </div>

    <!-- ===== 筛选排序栏 ===== -->
    <div class="bh-sort-bar">
      <div class="bh-sort-item" @click="onNearby">
        <span>📍 附近</span>
      </div>
      <div class="bh-sort-item" @click="showFilter = true">
        <span>🔽 筛选</span>
      </div>
      <div class="bh-sort-item" @click="toggleSort">
        <span>⇅ {{ sortLabel }}</span>
      </div>
    </div>

    <!-- ===== 内容列表 ===== -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list v-model:loading="loading" :finished="finished" finished-text="没有更多了" @load="loadList">
        <div v-if="list.length === 0 && !loading" class="empty">暂无悬赏</div>
        <div
          v-for="item in list"
          :key="item.id"
          class="bounty-card"
          @click="$router.push(`/demands/${item.id}`)"
        >
          <!-- 用户信息行 -->
          <div class="bc-user">
            <div class="bc-user-left">
              <van-image round width="36" height="36" fit="cover" :src="item.creator?.avatar || defaultAvatar" />
              <div class="bc-user-info">
                <div class="bc-user-name-row">
                  <span class="bc-user-name">{{ item.creator?.nickname || item.creator_nickname || '匿名' }}</span>
                  <span class="bc-gender" :class="item.creator?.gender || 'female'">
                    {{ (item.creator?.gender || 'female') === 'male' ? '♂' : '♀' }}
                  </span>
                  <span v-if="item.creator?.verified || item.creator?.is_verified" class="bc-badge">已认证</span>
                </div>
              </div>
            </div>
            <div class="bc-price">¥{{ item.budget || item.price || 0 }}</div>
          </div>

          <!-- 标题 -->
          <div class="bc-title van-multi-ellipsis--l2">{{ item.title }}</div>

          <!-- 标签区 -->
          <div class="bc-tags" v-if="item.skill_type || item.tags">
            <span class="bc-tag" v-for="tag in parseTags(item)" :key="tag">{{ tag }}</span>
          </div>

          <!-- 位置时间 -->
          <div class="bc-meta">
            <span v-if="item.location">📍 {{ item.location }}</span>
            <span>📅 {{ formatTime(item.created_at) }}</span>
          </div>

          <!-- 报名状态 -->
          <div class="bc-signup">
            <div class="bc-avatars" v-if="applicantAvatars(item).length > 0">
              <van-image
                v-for="(av, ai) in applicantAvatars(item).slice(0, 3)"
                :key="ai"
                round
                width="24"
                height="24"
                fit="cover"
                :src="av"
                class="bc-av-overlap"
              />
              <span v-if="applicantCount(item) > 3" class="bc-av-more">+{{ applicantCount(item) - 3 }}</span>
            </div>
            <div class="bc-time">已报名：{{ applicantCount(item) }}人</div>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 发布按钮 -->
    <div class="fab" @click="onCreate">
      <van-button round type="primary" icon="plus" />
    </div>

    <!-- 筛选面板 -->
    <van-action-sheet v-model:show="showFilter" title="筛选" close-on-popstate>
      <div class="filter-sheet">
        <div class="filter-group">
          <div class="filter-label">💰 预算范围</div>
          <div class="price-inputs">
            <input v-model.number="filters.priceMin" class="price-input" placeholder="最低" type="number" />
            <span class="price-sep">-</span>
            <input v-model.number="filters.priceMax" class="price-input" placeholder="最高" type="number" />
          </div>
        </div>
        <div class="filter-group">
          <div class="filter-label">📍 地区</div>
          <div class="tag-group">
            <span v-for="c in cityOptions" :key="c.value"
              :class="['tag-chip', { active: filters.city === c.value }]"
              @click="filters.city = filters.city === c.value ? '' : c.value">
              {{ c.label }}
            </span>
          </div>
        </div>
        <div class="filter-actions">
          <van-button plain block round @click="resetFilters" style="border-color:#999;color:#999;flex:1">重置</van-button>
          <van-button block round @click="applyFilters" style="background:#00BCD4;color:#fff;border:none;flex:1">确定</van-button>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { listDemands } from '@/utils/api'

const router = useRouter()
const defaultAvatar = 'https://randomuser.me/api/portraits/women/44.jpg'

// Tab
const activeTab = ref('bounty')

// Tags
const tagList = [
  { label: '全部', value: '' },
  { label: '演员', value: '演员' },
  { label: '模特', value: '模特' },
  { label: '线下陪玩', value: '陪玩' },
  { label: '运动搭子', value: '运动搭子' },
  { label: '摄影师', value: '摄影师' },
  { label: '化妆师', value: '化妆师' },
  { label: '主持人', value: '主持人' },
  { label: '歌手', value: '歌手' },
  { label: '短视频', value: '短视频' },
]
const activeTag = ref('')

// Sort
const sortBy = ref('newest')
const sortLabel = computed(() => {
  const map = { newest: '最新发布', popular: '最热', price_asc: '价格从低', price_desc: '价格从高' }
  return map[sortBy.value] || '最新发布'
})
function toggleSort() {
  const order = ['newest', 'popular', 'price_asc', 'price_desc']
  const idx = order.indexOf(sortBy.value)
  sortBy.value = order[(idx + 1) % order.length]
  reloadList()
}

// Filter
const showFilter = ref(false)
const filters = ref({ priceMin: null, priceMax: null, city: '' })
const cityOptions = [
  { label: '不限', value: '' },
  { label: '北京', value: '北京' },
  { label: '上海', value: '上海' },
  { label: '广州', value: '广州' },
  { label: '深圳', value: '深圳' },
  { label: '杭州', value: '杭州' },
  { label: '成都', value: '成都' },
]
function resetFilters() {
  filters.value = { priceMin: null, priceMax: null, city: '' }
}
function applyFilters() {
  showFilter.value = false
  reloadList()
}

// Data
const list = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
let page = 1

function reloadList() {
  page = 1
  list.value = []
  finished.value = false
  loading.value = true
  loadList()
}

async function loadList() {
  if (refreshing.value) {
    page = 1; list.value = []; finished.value = false; refreshing.value = false
  }
  if (finished.value) return
  loading.value = true
  try {
    const params = { page, page_size: 10, sort_by: sortBy.value }
    if (activeTag.value) params.skill_type = activeTag.value
    if (filters.value.priceMin) params.price_min = filters.value.priceMin
    if (filters.value.priceMax) params.price_max = filters.value.priceMax
    if (filters.value.city) params.location = filters.value.city
    const res = await listDemands(params)
    const body = res.data || res
    const items = body.data || body.items || body || []
    if (Array.isArray(items)) list.value.push(...items)
    page++
    if (!Array.isArray(items) || items.length < 10) finished.value = true
  } catch {
    showToast('加载失败')
  } finally {
    loading.value = false
  }
}

function onRefresh() {
  refreshing.value = true
  loading.value = true
  loadList()
}

// Helpers
function parseTags(item) {
  const tags = []
  if (item.skill_type) tags.push(item.skill_type)
  if (Array.isArray(item.tags)) tags.push(...item.tags)
  return tags.length > 0 ? tags : ['悬赏']
}

function applicantAvatars(item) {
  if (item.applicants && Array.isArray(item.applicants)) {
    return item.applicants.map(a => a.avatar || defaultAvatar)
  }
  // Generate fake avatars based on applicant_count
  const count = Math.min(item.applicant_count || 3, 6)
  return Array.from({length: count}, (_, i) =>
    `https://api.dicebear.com/7.x/avataaars/svg?seed=bounty_${item.id}_${i}`
  )
}

function applicantCount(item) {
  return item.applicant_count || (item.applicants ? item.applicants.length : Math.floor(Math.random() * 8) + 2)
}

function formatTime(t) {
  if (!t) return '今天'
  const d = new Date(t)
  const now = new Date()
  const diff = Math.floor((now - d) / 1000)
  if (diff < 3600) return Math.floor(diff / 60) + '分钟前'
  if (diff < 86400) return Math.floor(diff / 3600) + '小时前'
  if (diff < 604800) return Math.floor(diff / 86400) + '天前'
  return d.toLocaleDateString('zh-CN')
}

function onNearby() {
  showToast('正在获取位置...')
}

function onCall() {
  showToast('客服热线: 400-888-8888')
}

function onCreate() {
  const token = localStorage.getItem('token')
  if (!token) return router.push('/login')
  router.push('/demands/create')
}
</script>

<style scoped>
.bounty-page {
  background: #F5F5F5;
  min-height: 100vh;
  padding-bottom: 70px;
}

/* ===== Header ===== */
.bounty-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #00BCD4, #0097A7);
  color: #FFF;
}
.bh-logo {
  width: 32px;
  height: 32px;
  background: #FFF;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 800;
  color: #00BCD4;
}
.bh-title {
  font-size: 18px;
  font-weight: 700;
}
.bh-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.bh-phone {
  width: 30px;
  height: 30px;
  background: #F44336;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.bh-bell {
  position: relative;
  cursor: pointer;
}
.bh-bell-badge {
  position: absolute;
  top: -4px;
  right: -8px;
  min-width: 16px;
  height: 16px;
  background: #F44336;
  border-radius: 8px;
  font-size: 10px;
  color: #FFF;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  font-weight: 600;
}

/* ===== Tab 切换 ===== */
.bh-tabs {
  display: flex;
  margin: 0 16px;
  margin-top: 12px;
  background: #FFF;
  border-radius: 22px;
  overflow: hidden;
  border: 1px solid #00BCD4;
}
.bh-tab {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  color: #999;
  background: #FFF;
  transition: all 0.2s;
}
.bh-tab.active {
  background: #00BCD4;
  color: #FFF;
  font-weight: 600;
}

/* ===== 标签云 ===== */
.bh-tags {
  margin: 10px 16px 0;
}
.bh-tags-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: none;
}
.bh-tags-scroll::-webkit-scrollbar { display: none; }
.bh-tag {
  flex-shrink: 0;
  padding: 5px 14px;
  font-size: 13px;
  color: #666;
  background: #F0F0F0;
  border-radius: 16px;
  cursor: pointer;
  white-space: nowrap;
}
.bh-tag.active {
  background: #00BCD4;
  color: #FFF;
  font-weight: 600;
}

/* ===== 筛选排序栏 ===== */
.bh-sort-bar {
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin: 10px 16px;
  background: #FFF;
  border-radius: 10px;
  padding: 8px 0;
}
.bh-sort-item {
  font-size: 13px;
  color: #666;
  cursor: pointer;
  padding: 2px 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.bh-sort-item + .bh-sort-item {
  border-left: 1px solid #EEE;
}

/* ===== 悬赏卡片 ===== */
.bounty-card {
  background: #FFF;
  margin: 0 16px 12px;
  border-radius: 14px;
  padding: 14px;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

/* 用户信息 */
.bc-user {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.bc-user-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.bc-user-name-row {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}
.bc-user-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}
.bc-gender {
  font-size: 12px;
  font-weight: 600;
}
.bc-gender.male { color: #2196F3; }
.bc-gender.female { color: #FF4081; }
.bc-badge {
  font-size: 10px;
  color: #00BCD4;
  background: #E0F7FA;
  padding: 1px 6px;
  border-radius: 8px;
}
.bc-price {
  font-size: 16px;
  font-weight: 700;
  color: #FF9800;
}

/* 标题 */
.bc-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
  margin-bottom: 8px;
}

/* 标签区 */
.bc-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}
.bc-tag {
  padding: 2px 10px;
  font-size: 12px;
  color: #0097A7;
  background: #E0F7FA;
  border-radius: 10px;
}

/* 位置时间 */
.bc-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #999;
  margin-bottom: 10px;
}

/* 报名状态 */
.bc-signup {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 10px;
  border-top: 1px solid #F0F0F0;
}
.bc-avatars {
  display: flex;
  align-items: center;
}
.bc-av-overlap {
  margin-right: -8px;
  border: 2px solid #FFF;
}
.bc-av-more {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #E0F7FA;
  color: #00BCD4;
  font-size: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #FFF;
}
.bc-time {
  font-size: 12px;
  color: #999;
}

/* ===== 通用 ===== */
.empty {
  text-align: center;
  color: #999;
  padding: 40px 0;
  font-size: 14px;
}
.fab {
  position: fixed;
  bottom: 80px;
  right: 16px;
  z-index: 100;
}

/* 筛选弹窗 */
.filter-sheet { padding: 16px; }
.filter-group { margin-bottom: 16px; }
.filter-label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}
.price-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}
.price-input {
  flex: 1;
  height: 36px;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 0 10px;
  font-size: 14px;
  outline: none;
}
.price-input:focus { border-color: #00BCD4; }
.price-sep { color: #999; }
.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.tag-chip {
  padding: 5px 14px;
  font-size: 13px;
  color: #666;
  background: #f0f0f0;
  border-radius: 16px;
  cursor: pointer;
}
.tag-chip.active {
  background: #E0F7FA;
  color: #00BCD4;
  font-weight: 600;
}
.filter-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}
</style>
