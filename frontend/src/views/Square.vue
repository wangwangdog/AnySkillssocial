<template>
  <div class="page square-page">
    <!-- Tab options -->
    <div class="square-tabs">
      <div
        v-for="tab in tabs"
        :key="tab.key"
        :class="['tab-item', { active: activeTab === tab.key }]"
        @click="switchTab(tab.key)"
      >
        <van-icon :name="tab.icon" />
        <span>{{ tab.label }}</span>
      </div>
    </div>

    <!-- 需求广场 -->
    <div v-show="activeTab === 'demands'" class="tab-content">
      <div class="filter-bar">
        <div class="sort-row">
          <span
            v-for="s in sortOptions"
            :key="s.key"
            :class="['sort-chip', { active: demandSortBy === s.key }]"
            @click="demandSortBy = s.key; reloadDemands()"
          >{{ s.label }}</span>
        </div>
        <div class="filter-btn" @click="showDemandFilter = true">
          <van-icon name="filter-o" />
          <span>筛选</span>
          <van-icon v-if="demandActiveFilterCount" name="warning" color="#FF9800" style="font-size:12px" />
        </div>
      </div>

      <div class="quick-tags">
        <span
          v-for="tag in demandTags"
          :key="tag.value"
          :class="['tag-chip', { active: demandFilter.skill_type === tag.value }]"
          @click="demandFilter.skill_type = demandFilter.skill_type === tag.value ? '' : tag.value; reloadDemands()"
        >{{ tag.label }}</span>
      </div>

      <van-pull-refresh v-model="demandRefreshing" @refresh="onDemandRefresh">
        <van-list v-model:loading="demandLoading" :finished="demandFinished" finished-text="没有更多了" @load="loadDemands">
          <div v-show="demands.length === 0 && !demandLoading" class="empty">暂无需求</div>
          <div class="grid-2col">
            <div
              v-for="item in demands"
              :key="item.id"
              class="person-card"
              @click="$router.push(`/demands/${item.id}`)"
            >
              <div class="person-img-wrap">
                <van-image width="100%" height="100%" fit="cover" :src="item.creator?.avatar || defaultAvatar" class="person-img" />
                <div class="person-nick-overlay">
                  <span class="person-nick-text">{{ item.creator_nickname || item.creator?.nickname || '匿名' }}</span>
                  <span class="person-online online"></span>
                </div>
                <div class="person-price-badge">¥{{ item.budget || 0 }}</div>
              </div>
              <div class="person-info">
                <div class="person-meta-row">
                  <span class="van-multi-ellipsis--l1" style="flex:1">{{ item.title }}</span>
                </div>
                <div class="person-meta-row">
                  <span v-if="item.location">📍 {{ item.location }}</span>
                  <van-tag v-if="item.skill_type" plain size="mini" class="person-skill-tag">{{ item.skill_type }}</van-tag>
                </div>
              </div>
            </div>
          </div>
        </van-list>
      </van-pull-refresh>

      <div class="fab" @click="$router.push('/demands/create')">
        <van-button round type="primary" icon="plus" />
      </div>
    </div>

    <!-- 服务广场 -->
    <div v-show="activeTab === 'services'" class="tab-content">
      <div class="filter-bar">
        <div class="sort-row">
          <span
            v-for="s in sortOptions"
            :key="s.key"
            :class="['sort-chip', { active: svcSortBy === s.key }]"
            @click="svcSortBy = s.key; reloadServices()"
          >{{ s.label }}</span>
        </div>
        <div class="filter-btn" @click="showSvcFilter = true">
          <van-icon name="filter-o" />
          <span>筛选</span>
          <van-icon v-if="svcActiveFilterCount" name="warning" color="#FF9800" style="font-size:12px" />
        </div>
      </div>

      <div class="quick-tags">
        <span
          v-for="tag in serviceTags"
          :key="tag.value"
          :class="['tag-chip', { active: serviceFilter.skill_type === tag.value }]"
          @click="serviceFilter.skill_type = serviceFilter.skill_type === tag.value ? '' : tag.value; reloadServices()"
        >{{ tag.label }}</span>
      </div>

      <van-pull-refresh v-model="serviceRefreshing" @refresh="onServiceRefresh">
        <van-list v-model:loading="serviceLoading" :finished="serviceFinished" finished-text="没有更多了" @load="loadServices">
          <div v-show="services.length === 0 && !serviceLoading" class="empty">暂无服务</div>
          <div class="grid-2col">
            <div
              v-for="item in services"
              :key="item.id"
              class="person-card"
              @click="$router.push(`/services/${item.id}`)"
            >
              <div class="person-img-wrap">
                <van-image width="100%" height="100%" fit="cover" :src="item.seller?.avatar || defaultAvatar" class="person-img" />
                <div class="person-nick-overlay">
                  <span class="person-nick-text">{{ item.seller?.nickname || '匿名' }}</span>
                  <span class="person-online" :class="{ online: true }"></span>
                </div>
                <div class="person-price-badge">¥{{ item.price }}</div>
              </div>
              <div class="person-info">
                <div class="person-meta-row">
                  <span>{{ sellerAge(item) }}岁</span>
                  <span v-if="item.seller?.residence_city">{{ item.seller.residence_city }}</span>
                </div>
                <div class="person-meta-row">
                  <span v-if="item.seller_rating_avg > 0">⭐ {{ item.seller_rating_avg }}</span>
                  <span v-if="item.order_count" style="display:flex;align-items:center;gap:2px">
                    <van-icon name="bag-o" size="11" />{{ item.order_count }}
                  </span>
                </div>
                <van-tag v-if="item.skill_type" plain size="mini" class="person-skill-tag">{{ item.skill_type }}</van-tag>
              </div>
            </div>
          </div>
        </van-list>
      </van-pull-refresh>

      <div class="fab" @click="$router.push('/services/create')">
        <van-button round type="primary" icon="plus" />
      </div>
    </div>

    <!-- 社区广场 -->
    <div v-show="activeTab === 'community'" class="tab-content">
      <van-pull-refresh v-model="feedRefreshing" @refresh="onFeedRefresh">
        <van-list v-model:loading="feedLoading" :finished="feedFinished" finished-text="没有更多了" @load="loadFeedPosts">
          <div v-show="feed.length === 0 && !feedLoading" class="empty">暂无动态</div>
          <div v-for="(item, idx) in feed" :key="'p'+idx" class="post-card" @click="$router.push(`/users/${item.user_id}`)">
            <div class="post-header">
              <van-image round width="40" height="40" :src="item.user_avatar || defaultAvatar" />
              <div class="post-user">
                <div class="post-nick">{{ item.user_nickname }}</div>
                <div class="post-time">{{ formatTime(item.created_at) }}</div>
              </div>
              <van-icon name="arrow" style="color:#ccc;font-size:12px" />
            </div>
            <div class="post-body">
              <div class="post-text">{{ item.content }}</div>
              <div v-if="item.images && item.images.length > 0" class="post-imgs">
                <van-image
                  v-for="(img, imgIdx) in item.images"
                  :key="imgIdx"
                  width="100%"
                  height="auto"
                  fit="cover"
                  :src="img"
                  class="post-img"
                />
              </div>
            </div>
          </div>
        </van-list>
      </van-pull-refresh>
    </div>

    <!-- 服务筛选弹窗 -->
    <van-action-sheet v-model:show="showSvcFilter" title="筛选" close-on-popstate>
      <div class="filter-sheet">
        <div class="filter-group">
          <div class="filter-label">💰 价格范围</div>
          <div class="price-inputs">
            <input v-model.number="svcFilters.priceMin" class="price-input" placeholder="最低价" type="number" />
            <span class="price-sep">-</span>
            <input v-model.number="svcFilters.priceMax" class="price-input" placeholder="最高价" type="number" />
          </div>
        </div>
        <div class="filter-group">
          <div class="filter-label">📍 城市</div>
          <div class="tag-group">
            <span v-for="c in cityOptions" :key="c.value"
              :class="['tag-chip', { active: svcFilters.city === c.value }]"
              @click="svcFilters.city = svcFilters.city === c.value ? '' : c.value">
              {{ c.label }}
            </span>
          </div>
        </div>
        <div class="filter-group">
          <div class="filter-label">👤 性别</div>
          <div class="tag-group">
            <span v-for="g in genderOptions" :key="g.value"
              :class="['tag-chip', { active: svcFilters.gender === g.value }]"
              @click="svcFilters.gender = svcFilters.gender === g.value ? '' : g.value">
              {{ g.label }}
            </span>
          </div>
        </div>
        <div class="filter-actions">
          <van-button plain block round @click="resetSvcFilters" style="border-color:#999;color:#999;flex:1">重置</van-button>
          <van-button block round @click="applySvcFilters" style="background:#4CAF50;color:#fff;border:none;flex:1">确定</van-button>
        </div>
      </div>
    </van-action-sheet>

    <!-- 需求筛选弹窗 -->
    <van-action-sheet v-model:show="showDemandFilter" title="筛选" close-on-popstate>
      <div class="filter-sheet">
        <div class="filter-group">
          <div class="filter-label">💰 预算范围</div>
          <div class="price-inputs">
            <input v-model.number="demandFilters.priceMin" class="price-input" placeholder="最低" type="number" />
            <span class="price-sep">-</span>
            <input v-model.number="demandFilters.priceMax" class="price-input" placeholder="最高" type="number" />
          </div>
        </div>
        <div class="filter-group">
          <div class="filter-label">📍 目的地</div>
          <div class="tag-group">
            <span v-for="c in cityOptions" :key="c.value"
              :class="['tag-chip', { active: demandFilters.location === c.value }]"
              @click="demandFilters.location = demandFilters.location === c.value ? '' : c.value">
              {{ c.label }}
            </span>
          </div>
        </div>
        <div class="filter-actions">
          <van-button plain block round @click="resetDemandFilters" style="border-color:#999;color:#999;flex:1">重置</van-button>
          <van-button block round @click="applyDemandFilters" style="background:#4CAF50;color:#fff;border:none;flex:1">确定</van-button>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'
import { listDemands, listServices, getCommunityPosts } from '@/utils/api'

const route = useRoute()
const router = useRouter()
const defaultAvatar = 'https://randomuser.me/api/portraits/women/44.jpg'

const tabs = [
  { key: 'demands', label: '需求广场', icon: 'records-o' },
  { key: 'services', label: '服务广场', icon: 'cluster-o' },
  { key: 'community', label: '社区广场', icon: 'friends-o' },
]
const activeTab = ref(route.query.tab || 'services')

// ====== 排序选项 ======
const sortOptions = [
  { key: 'newest', label: '最新' },
  { key: 'price_asc', label: '价格从低' },
  { key: 'price_desc', label: '价格从高' },
  { key: 'popular', label: '人气' },
]

// ====== 服务广场 ======
const serviceTags = [
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
const svcSortBy = ref('newest')
const showSvcFilter = ref(false)
const svcFilters = reactive({ city: '', priceMin: null, priceMax: null, gender: '' })
const cityOptions = [
  { label: '深圳', value: '深圳' }, { label: '北京', value: '北京' },
  { label: '上海', value: '上海' }, { label: '广州', value: '广州' },
  { label: '杭州', value: '杭州' }, { label: '成都', value: '成都' },
]
const genderOptions = [
  { label: '女', value: 'female' }, { label: '男', value: 'male' }, { label: '不限', value: '' },
]
const svcActiveFilterCount = computed(() => {
  let c = 0; if (svcFilters.city) c++; if (svcFilters.priceMin) c++; if (svcFilters.priceMax) c++; if (svcFilters.gender) c++; return c
})
const services = ref([])
const serviceLoading = ref(false)
const serviceFinished = ref(false)
const serviceRefreshing = ref(false)
const serviceFilter = reactive({ skill_type: '' })
let servicePage = 1

function reloadServices() { servicePage = 1; services.value = []; serviceFinished.value = false; serviceLoading.value = true; loadServices() }
function sellerAge(item) {
  if (item.seller?.birth_date) return new Date().getFullYear() - new Date(item.seller.birth_date).getFullYear()
  return '??'
}
function resetSvcFilters() { svcFilters.city = ''; svcFilters.priceMin = null; svcFilters.priceMax = null; svcFilters.gender = '' }
function applySvcFilters() { showSvcFilter.value = false; reloadServices() }

async function loadServices() {
  if (serviceRefreshing.value) { servicePage = 1; services.value = []; serviceFinished.value = false; serviceRefreshing.value = false }
  if (serviceFinished.value) return
  serviceLoading.value = true
  try {
    const params = { page: servicePage, page_size: 10, sort_by: svcSortBy.value }
    if (serviceFilter.skill_type) params.skill_type = serviceFilter.skill_type
    if (svcFilters.city) params.city = svcFilters.city
    if (svcFilters.priceMin) params.price_min = svcFilters.priceMin
    if (svcFilters.priceMax) params.price_max = svcFilters.priceMax
    if (svcFilters.gender) params.gender = svcFilters.gender
    const res = await listServices(params)
    const body = res.data || res
    const items = body.data || body.items || body || []
    if (Array.isArray(items)) services.value.push(...items)
    servicePage++
    if (!Array.isArray(items) || items.length < 10) serviceFinished.value = true
  } catch { showToast('加载失败') } finally { serviceLoading.value = false }
}
function onServiceRefresh() { serviceRefreshing.value = true; serviceLoading.value = true; loadServices() }

// ====== 需求广场 ======
const demandSortBy = ref('newest')
const showDemandFilter = ref(false)
const demandTags = [
  { label: '全部', value: '' }, { label: '旅游服务', value: '旅游服务' },
  { label: '陪玩', value: '陪玩' }, { label: '按摩', value: '按摩' },
  { label: '化妆', value: '化妆' }, { label: '健身', value: '健身' },
  { label: '摄影', value: '摄影' }, { label: '烹饪', value: '烹饪' }, { label: '其他', value: '其他' },
]
const demandFilters = reactive({ priceMin: null, priceMax: null, location: '' })
const demandActiveFilterCount = computed(() => { let c=0; if (demandFilters.priceMin) c++; if (demandFilters.priceMax) c++; if (demandFilters.location) c++; return c })
const demands = ref([])
const demandLoading = ref(false)
const demandFinished = ref(false)
const demandRefreshing = ref(false)
const demandFilter = reactive({ skill_type: '' })
let demandPage = 1

function reloadDemands() { demandPage = 1; demands.value = []; demandFinished.value = false; demandLoading.value = true; loadDemands() }
function resetDemandFilters() { demandFilters.priceMin = null; demandFilters.priceMax = null; demandFilters.location = '' }
function applyDemandFilters() { showDemandFilter.value = false; reloadDemands() }

async function loadDemands() {
  if (demandRefreshing.value) { demandPage = 1; demands.value = []; demandFinished.value = false; demandRefreshing.value = false }
  if (demandFinished.value) return
  demandLoading.value = true
  try {
    const params = { page: demandPage, page_size: 10, sort_by: demandSortBy.value }
    if (demandFilter.skill_type) params.skill_type = demandFilter.skill_type
    if (demandFilters.priceMin) params.price_min = demandFilters.priceMin
    if (demandFilters.priceMax) params.price_max = demandFilters.priceMax
    if (demandFilters.location) params.location = demandFilters.location
    const res = await listDemands(params)
    const body = res.data || res
    const items = body.data || body.items || body || []
    if (Array.isArray(items)) demands.value.push(...items)
    demandPage++
    if (!Array.isArray(items) || items.length < 10) demandFinished.value = true
  } catch { showToast('加载失败') } finally { demandLoading.value = false }
}
function onDemandRefresh() { demandRefreshing.value = true; demandLoading.value = true; loadDemands() }

// ====== 社区广场 ======
const feed = ref([])
const feedLoading = ref(false)
const feedFinished = ref(false)
const feedRefreshing = ref(false)
let feedPage = 1

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t); const now = new Date(); const diff = Math.floor((now - d) / 1000)
  if (diff < 60) return '刚刚'
  if (diff < 3600) return Math.floor(diff / 60) + '分钟前'
  if (diff < 86400) return Math.floor(diff / 3600) + '小时前'
  if (diff < 604800) return Math.floor(diff / 86400) + '天前'
  return d.toLocaleDateString('zh-CN')
}

async function loadFeedPosts() {
  if (feedRefreshing.value) { feedPage = 1; feed.value = []; feedFinished.value = false; feedRefreshing.value = false }
  if (feedFinished.value) return
  feedLoading.value = true
  try {
    const res = await getCommunityPosts({ page: feedPage, page_size: 10 })
    const body = res.data || res
    const items = body.data || body.items || body || []
    if (Array.isArray(items)) feed.value.push(...items)
    feedPage++
    if (!Array.isArray(items) || items.length < 10) feedFinished.value = true
  } catch { showToast('加载失败') } finally { feedLoading.value = false }
}
function onFeedRefresh() { feedRefreshing.value = true; feedLoading.value = true; loadFeedPosts() }

// ====== Tab 切换 ======
function switchTab(key) {
  activeTab.value = key
  router.replace(`/square?tab=${key}`)
  if (key === 'community' && feed.value.length === 0 && !feedLoading.value) loadFeedPosts()
  if (key === 'services' && services.value.length === 0 && !serviceLoading.value) loadServices()
  if (key === 'demands' && demands.value.length === 0 && !demandLoading.value) loadDemands()
}

onMounted(() => {
  if (activeTab.value === 'services') loadServices()
  else if (activeTab.value === 'community') loadFeedPosts()
  else loadDemands()
})
</script>

<style scoped>
.square-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 12px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}
.tab-item {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.tab-item.active {
  background: #4CAF50;
  color: #fff;
  font-weight: 600;
}
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.sort-row { display: flex; gap: 8px; }
.sort-chip {
  padding: 4px 10px; font-size: 12px; color: #666;
  background: #f0f0f0; border-radius: 14px; cursor: pointer;
}
.sort-chip.active { background: #4CAF50; color: #fff; }
.filter-btn {
  display: flex; align-items: center; gap: 4px; font-size: 12px;
  color: #666; cursor: pointer; padding: 4px 10px; border: 1px solid #eee; border-radius: 14px;
}
.quick-tags {
  display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;
}
.tag-chip {
  padding: 4px 12px; font-size: 12px; color: #666;
  background: #f0f0f0; border-radius: 14px; cursor: pointer;
}
.tag-chip.active { background: #E8F5E9; color: #4CAF50; }
.grid-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.person-card {
  background: #fff; border-radius: 12px; overflow: hidden;
  cursor: pointer; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.person-img-wrap {
  position: relative; width: 100%; height: 160px;
}
.person-img { display: block; }
.person-nick-overlay {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 6px 8px; background: linear-gradient(transparent, rgba(0,0,0,0.6));
  display: flex; align-items: center; gap: 6px;
}
.person-nick-text {
  font-size: 13px; color: #fff; font-weight: 600;
  flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.person-online { width: 8px; height: 8px; border-radius: 50%; background: #ccc; }
.person-online.online { background: #4CAF50; }
.person-price-badge {
  position: absolute; top: 8px; right: 8px;
  background: rgba(0,0,0,0.55); color: #fff; font-size: 12px;
  font-weight: 600; padding: 2px 8px; border-radius: 10px;
}
.person-info { padding: 8px; }
.person-meta-row { display: flex; justify-content: space-between; font-size: 12px; color: #666; margin-bottom: 4px; }
.person-skill-tag { margin-top: 4px; }
.fab { position: fixed; bottom: 80px; right: 16px; z-index: 100; }
.empty { text-align: center; color: #999; padding: 40px 0; font-size: 14px; }

/* 社区 */
.post-card { background: #fff; border-radius: 12px; padding: 12px; margin-bottom: 10px; }
.post-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.post-user { flex: 1; }
.post-nick { font-size: 14px; font-weight: 600; color: #333; }
.post-time { font-size: 11px; color: #999; margin-top: 2px; }
.post-body { }
.post-text { font-size: 14px; color: #555; line-height: 1.5; margin-bottom: 8px; }
.post-imgs { }
.post-img { border-radius: 8px; margin-bottom: 6px; }

/* 筛选弹窗 */
.filter-sheet { padding: 16px; }
.filter-group { margin-bottom: 16px; }
.filter-label { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 8px; }
.price-inputs { display: flex; align-items: center; gap: 8px; }
.price-input { flex: 1; height: 36px; border: 1px solid #ddd; border-radius: 8px; padding: 0 10px; font-size: 14px; outline: none; }
.price-input:focus { border-color: #4CAF50; }
.price-sep { color: #999; }
.tag-group { display: flex; flex-wrap: wrap; gap: 8px; }
.filter-actions { display: flex; gap: 12px; margin-top: 20px; }
</style>
