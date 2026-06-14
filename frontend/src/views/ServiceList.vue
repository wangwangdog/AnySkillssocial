<template>
  <div class="page service-list-page">
    <van-nav-bar title="服务市场" left-arrow @click-left="$router.back()" />

    <!-- 搜索框 -->
    <div class="search-box">
      <van-search
        v-model="keyword"
        shape="round"
        placeholder="搜索服务或达人..."
        @search="onSearch"
        @clear="onSearch"
      />
    </div>

    <!-- 快捷技能标签 -->
    <div class="quick-tags">
      <span
        v-for="tag in skillTags"
        :key="tag.value"
        :class="['tag-chip', { active: filters.skill_type === tag.value }]"
        @click="toggleTag(tag)"
      >{{ tag.label }}</span>
    </div>

    <!-- 排序 + 筛选按钮 -->
    <div class="filter-bar">
      <div class="sort-row">
        <span
          v-for="s in sortOptions"
          :key="s.key"
          :class="['sort-chip', { active: sortBy === s.key }]"
          @click="sortBy = s.key; reload()"
        >{{ s.label }}</span>
      </div>
      <div class="filter-btn" @click="showFilter = true">
        <van-icon name="filter-o" />
        <span>筛选</span>
        <van-icon v-if="activeFilterCount" name="warning" color="#ff4757" style="font-size:12px" />
      </div>
    </div>

    <!-- 服务列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="loadServices"
      >
        <!-- 人物优先卡片 -->
        <div
          v-for="item in list"
          :key="item.id"
          class="person-card"
          @click="$router.push(`/services/${item.id}`)"
        >
          <div class="card-top-row">
            <div class="seller-row">
              <van-image round width="44" height="44" :src="item.seller?.avatar || defaultAvatar" class="seller-avatar" />
              <div class="seller-meta">
                <div class="seller-nick">{{ item.seller?.nickname || '匿名' }}
                  <van-icon v-if="item.seller_rating_avg > 0" name="star" color="#ff6b81" size="12" />
                  <span v-if="item.seller_rating_avg > 0" class="rating-text">{{ item.seller_rating_avg }}</span>
                </div>
                <div class="seller-sub">
                  {{ sellerAge(item) }}岁 · {{ genderLabel(item.seller?.gender) }}
                  <template v-if="item.seller?.residence_city"> · {{ item.seller.residence_city }}</template>
                </div>
              </div>
            </div>
            <van-tag plain class="skill-badge">{{ item.skill_type }}</van-tag>
          </div>
          <div class="card-title">{{ item.title }}</div>
          <div class="card-desc van-multi-ellipsis--l2">{{ item.description }}</div>
          <div class="card-bottom-row">
            <div class="card-info-tags">
              <span v-if="item.location" class="info-tag">📍 {{ item.location }}</span>
              <span v-if="item.duration" class="info-tag">⏱ {{ item.duration }}</span>
              <span v-if="item.order_count" class="info-tag">已接{{ item.order_count }}单</span>
            </div>
            <div class="card-action">
              <span class="card-price">¥{{ item.price }}</span>
              <van-button size="mini" round class="order-btn" @click.stop="handleOrder(item)">立即预约</van-button>
            </div>
          </div>
        </div>
        <div v-if="list.length === 0 && !loading" class="empty">暂无服务</div>
      </van-list>
    </van-pull-refresh>

    <!-- FAB 发布 -->
    <div class="fab">
      <van-button round type="primary" icon="plus" @click="$router.push('/services/create')" />
    </div>

    <!-- ===== 筛选弹窗 ===== -->
    <van-action-sheet v-model:show="showFilter" title="筛选" close-on-popstate>
      <div class="filter-sheet">
        <div class="filter-group">
          <div class="filter-label">💰 价格范围</div>
          <div class="price-inputs">
            <input v-model.number="filters.priceMin" class="price-input" placeholder="最低价" type="number" />
            <span class="price-sep">-</span>
            <input v-model.number="filters.priceMax" class="price-input" placeholder="最高价" type="number" />
          </div>
        </div>
        <div class="filter-group">
          <div class="filter-label">📍 城市</div>
          <div class="tag-group">
            <span v-for="c in cityOptions" :key="c.value"
              :class="['tag-chip', { active: filters.city === c.value }]"
              @click="filters.city = filters.city === c.value ? '' : c.value">
              {{ c.label }}
            </span>
          </div>
        </div>
        <div class="filter-group">
          <div class="filter-label">👤 性别</div>
          <div class="tag-group">
            <span v-for="g in genderOptions" :key="g.value"
              :class="['tag-chip', { active: filters.gender === g.value }]"
              @click="filters.gender = filters.gender === g.value ? '' : g.value">
              {{ g.label }}
            </span>
          </div>
        </div>
        <div class="filter-actions">
          <van-button plain block round @click="resetFilters" style="border-color:#999;color:#999;flex:1">重置</van-button>
          <van-button block round @click="applyFilters" style="background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;flex:1">确定</van-button>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { listServices, createOrder } from '@/utils/api'

const router = useRouter()
const defaultAvatar = 'https://randomuser.me/api/portraits/women/44.jpg'

// Search
const keyword = ref('')

// Sort
const sortBy = ref('newest')
const sortOptions = [
  { key: 'newest', label: '最新' },
  { key: 'price_asc', label: '价格从低' },
  { key: 'price_desc', label: '价格从高' },
  { key: 'popular', label: '人气' },
]

// Skill tags
const skillTags = [
  { label: '全部', value: '' },
  { label: '陪玩', value: '陪玩' },
  { label: '按摩', value: '按摩' },
  { label: '跳舞', value: '跳舞' },
  { label: '唱歌', value: '唱歌' },
  { label: '健身', value: '健身' },
  { label: '摄影', value: '摄影' },
  { label: '化妆', value: '化妆' },
  { label: '烹饪', value: '烹饪' },
  { label: '其他', value: '其他' },
]

// Filters
const showFilter = ref(false)
const filters = reactive({
  skill_type: '',
  city: '',
  priceMin: null,
  priceMax: null,
  gender: '',
})

const cityOptions = [
  { label: '深圳', value: '深圳' },
  { label: '北京', value: '北京' },
  { label: '上海', value: '上海' },
  { label: '广州', value: '广州' },
  { label: '杭州', value: '杭州' },
  { label: '成都', value: '成都' },
]

const genderOptions = [
  { label: '女', value: 'female' },
  { label: '男', value: 'male' },
  { label: '不限', value: '' },
]

const activeFilterCount = computed(() => {
  let count = 0
  if (filters.city) count++
  if (filters.priceMin) count++
  if (filters.priceMax) count++
  if (filters.gender) count++
  return count
})

// Data
const list = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
let page = 1
const pageSize = 10

function toggleTag(tag) {
  filters.skill_type = filters.skill_type === tag.value ? '' : tag.value
  reload()
}

function reload() {
  page = 1
  list.value = []
  finished.value = false
  loading.value = true
  loadServices()
}

async function loadServices() {
  if (refreshing.value) {
    page = 1
    list.value = []
    finished.value = false
    refreshing.value = false
  }
  if (finished.value) return

  loading.value = true
  try {
    const params = { page, page_size: pageSize, sort_by: sortBy.value }
    if (filters.skill_type) params.skill_type = filters.skill_type
    if (filters.city) params.city = filters.city
    if (filters.priceMin) params.price_min = filters.priceMin
    if (filters.priceMax) params.price_max = filters.priceMax
    if (filters.gender) params.gender = filters.gender
    if (keyword.value) params.keyword = keyword.value

    const res = await listServices(params)
    const data = res.data || res
    const items = data.items || data || []
    list.value.push(...items)
    page++

    const total = data.total || data.total_count || items.length
    if (list.value.length >= total || items.length < pageSize) {
      finished.value = true
    }
  } catch {
    showToast('加载失败')
  } finally {
    loading.value = false
  }
}

function onRefresh() {
  refreshing.value = true
  reload()
}

function onSearch() {
  reload()
}

function resetFilters() {
  filters.city = ''
  filters.priceMin = null
  filters.priceMax = null
  filters.gender = ''
}

function applyFilters() {
  showFilter.value = false
  reload()
}

function genderLabel(g) {
  return g === 'female' ? '女' : g === 'male' ? '男' : ''
}

function sellerAge(item) {
  if (item.seller?.birth_date) {
    const birth = new Date(item.seller.birth_date)
    const age = new Date().getFullYear() - birth.getFullYear()
    return age
  }
  return '??'
}

async function handleOrder(item) {
  if (!localStorage.getItem('token')) {
    showToast('请先登录')
    return router.push('/login')
  }
  if (!item.seller?.id) {
    showToast('卖家信息缺失')
    return
  }
  showLoadingToast({ message: '创建订单中...', forbidClick: true })
  try {
    const res = await createOrder({
      order_type: 'service',
      service_id: item.id,
      seller_id: item.seller.id,
    })
    const orderData = res.data || res
    closeToast()
    showToast('下单成功')
    setTimeout(() => router.push(`/orders/${orderData.id}`), 800)
  } catch (err) {
    const msg = err.response?.data?.detail || err.response?.data?.message || err.message || '下单失败'
    showToast(msg)
    closeToast()
  }
}
</script>

<style scoped>
.service-list-page {
  padding-bottom: 80px;
}
.search-box { margin-bottom: 8px; }
.search-box :deep(.van-search) { padding: 8px 0; }

/* Quick tags */
.quick-tags {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  margin-bottom: 8px;
  -webkit-overflow-scrolling: touch;
}
.quick-tags::-webkit-scrollbar { display: none; }
.tag-chip {
  flex-shrink: 0;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 12px;
  background: #f5f5f5;
  color: #666;
  cursor: pointer;
  white-space: nowrap;
  border: 1px solid transparent;
  transition: all 0.15s;
}
.tag-chip.active {
  background: rgba(102,126,234,0.1);
  color: #667eea;
  border-color: #667eea;
}

/* Filter bar */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.sort-row {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  flex: 1;
  -webkit-overflow-scrolling: touch;
}
.sort-row::-webkit-scrollbar { display: none; }
.sort-chip {
  flex-shrink: 0;
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 14px;
  background: #f0f0f0;
  color: #666;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
}
.sort-chip.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}
.filter-btn {
  display: flex;
  align-items: center;
  gap: 3px;
  flex-shrink: 0;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 14px;
  background: #f0f0f0;
  color: #666;
  cursor: pointer;
  margin-left: 8px;
  white-space: nowrap;
}
.filter-btn:active { opacity: 0.7; }

/* Person-first card */
.person-card {
  background: #fff;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 10px;
  box-shadow: 0 1px 5px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: transform 0.15s;
}
.person-card:active { transform: scale(0.98); }
.card-top-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}
.seller-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.seller-avatar {
  flex-shrink: 0;
  border: 2px solid #667eea;
}
.seller-meta { }
.seller-nick {
  font-size: 15px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
}
.rating-text {
  font-size: 11px;
  color: #ff6b81;
}
.seller-sub {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}
.skill-badge {
  border-color: #ff4757 !important;
  color: #ff4757 !important;
  font-size: 11px;
  flex-shrink: 0;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
}
.card-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 8px;
}
.card-bottom-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 8px;
}
.card-info-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
}
.info-tag {
  font-size: 11px;
  color: #999;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
}
.card-action {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.card-price {
  font-size: 17px;
  font-weight: 700;
  color: #ee0a24;
}
.order-btn {
  background: linear-gradient(135deg, #ff4757, #ff6b81) !important;
  color: #fff !important;
  border: none !important;
  font-size: 11px !important;
}
.fab {
  position: fixed;
  bottom: 80px;
  right: 16px;
  z-index: 100;
}
.empty {
  text-align: center;
  padding: 40px 0;
  color: #999;
  font-size: 14px;
}

/* Filter sheet */
.filter-sheet {
  padding: 16px;
  max-height: 70vh;
  overflow-y: auto;
}
.filter-group { margin-bottom: 18px; }
.filter-label { font-size: 14px; font-weight: 600; margin-bottom: 8px; color: #333; }
.price-inputs { display: flex; align-items: center; gap: 8px; }
.price-input {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
  text-align: center;
  outline: none;
  transition: border 0.15s;
}
.price-input:focus { border-color: #667eea; }
.price-sep { color: #999; font-size: 14px; }
.tag-group { display: flex; flex-wrap: wrap; gap: 8px; }
.filter-actions { display: flex; gap: 12px; margin-top: 24px; padding-bottom: 20px; }
</style>
