<template>
  <div class="page companions-page">
    <div class="cp-header">
      <div class="cp-title">找人陪</div>
      <div class="cp-subtitle">找到合适的陪伴，让生活更精彩</div>
    </div>

    <!-- 快速分类 -->
    <div class="cp-tags">
      <span
        v-for="tag in tagList"
        :key="tag.value"
        :class="['cp-tag', { active: activeTag === tag.value }]"
        @click="activeTag = tag.value; reloadCompanions()"
      >{{ tag.label }}</span>
    </div>

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list v-model:loading="loading" :finished="finished" finished-text="没有更多了" @load="loadCompanions">
        <div v-show="list.length === 0 && !loading" class="empty">暂无数据</div>
        <div class="grid-2col">
          <div
            v-for="item in list"
            :key="item.id"
            class="person-card"
            @click="$router.push(`/services/${item.id}`)"
          >
            <div class="person-img-wrap">
              <van-image width="100%" height="100%" fit="cover" :src="item.seller?.avatar || defaultAvatar" class="person-img" />
              <div class="person-nick-overlay">
                <span class="person-nick-text">{{ item.seller?.nickname || '匿名' }}</span>
                <span class="person-online online"></span>
              </div>
              <div class="person-price-badge">¥{{ item.price }}/次</div>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast } from 'vant'
import { listServices } from '@/utils/api'

const defaultAvatar = 'https://randomuser.me/api/portraits/women/44.jpg'

const tagList = [
  { label: '全部', value: '' },
  { label: '陪玩', value: '陪玩' },
  { label: '陪游', value: '陪游' },
  { label: '陪读', value: '陪读' },
  { label: '跳舞', value: '跳舞' },
  { label: '唱歌', value: '唱歌' },
  { label: '桌游', value: '桌游' },
  { label: '摄影', value: '摄影' },
]

const activeTag = ref('')
const list = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
let page = 1

function reloadCompanions() {
  page = 1
  list.value = []
  finished.value = false
  loading.value = true
  loadCompanions()
}

function sellerAge(item) {
  if (item.seller?.birth_date) {
    const birth = new Date(item.seller.birth_date)
    return new Date().getFullYear() - birth.getFullYear()
  }
  return '??'
}

onMounted(() => {
  loadCompanions()
})

async function loadCompanions() {
  if (refreshing.value) {
    page = 1
    list.value = []
    finished.value = false
    refreshing.value = false
  }
  if (finished.value) return
  loading.value = true
  try {
    const params = { page, page_size: 10, sort_by: 'popular' }
    if (activeTag.value) params.skill_type = activeTag.value
    const res = await listServices(params)
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
  loadCompanions()
}
</script>

<style scoped>
.companions-page { padding: 12px; padding-bottom: 70px; }
.cp-header { margin-bottom: 16px; }
.cp-title { font-size: 20px; font-weight: 700; color: #333; }
.cp-subtitle { font-size: 13px; color: #999; margin-top: 4px; }
.cp-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}
.cp-tag {
  padding: 5px 14px;
  font-size: 13px;
  color: #666;
  background: #f0f0f0;
  border-radius: 16px;
  cursor: pointer;
}
.cp-tag.active {
  background: #E8F5E9;
  color: #4CAF50;
  font-weight: 600;
}
.grid-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.person-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.person-img-wrap {
  position: relative;
  width: 100%;
  height: 160px;
}
.person-img { display: block; }
.person-nick-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 6px 8px;
  background: linear-gradient(transparent, rgba(0,0,0,0.6));
  display: flex;
  align-items: center;
  gap: 6px;
}
.person-nick-text {
  font-size: 13px;
  color: #fff;
  font-weight: 600;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.person-online {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
}
.person-online.online { background: #4CAF50; }
.person-price-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0,0,0,0.55);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
}
.person-info { padding: 8px; }
.person-meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}
.person-skill-tag { margin-top: 4px; }
.empty {
  text-align: center;
  color: #999;
  padding: 40px 0;
  font-size: 14px;
}
</style>
