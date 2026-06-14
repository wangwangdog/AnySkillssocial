<template>
  <div class="page">
    <van-nav-bar title="需求列表" left-arrow @click-left="$router.back()" />

    <!-- Skill type filter -->
    <div class="filter-bar">
      <van-dropdown-menu>
        <van-dropdown-item v-model="filters.skill_type" :options="skillOptions" @change="loadDemands" />
      </van-dropdown-menu>
    </div>

    <!-- Demand list -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="loadDemands"
      >
        <div v-for="item in list" :key="item.id" class="demand-card" @click="$router.push(`/demands/${item.id}`)">
          <div class="demand-title">{{ item.title }}</div>
          <div v-if="item.description" class="demand-desc van-multi-ellipsis--l2">{{ item.description }}</div>
          <div class="demand-meta">
            <van-tag type="danger">¥{{ item.budget || 0 }}</van-tag>
            <span>{{ item.location || '未指定' }}</span>
          </div>
          <van-tag v-if="item.skill_type" plain class="skill-tag">{{ item.skill_type }}</van-tag>
          <!-- Creator info -->
          <div class="demand-creator" @click.stop="$router.push(`/users/${item.creator?.id}`)">
            <van-image round width="28" height="28" :src="item.creator?.avatar || 'https://randomuser.me/api/portraits/women/44.jpg'" />
            <span class="creator-name">{{ item.creator?.nickname || item.creator?.phone || '匿名' }}</span>
            <van-icon name="arrow" class="creator-arrow" />
          </div>
        </div>
        <div v-if="list.length === 0 && !loading" class="empty">暂无需求</div>
      </van-list>
    </van-pull-refresh>

    <div class="fab">
      <van-button round type="primary" icon="plus" @click="$router.push('/demands/create')" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { showToast } from 'vant'
import { listDemands } from '@/utils/api'

const filters = reactive({ skill_type: '' })
const skillOptions = [
  { text: '全部', value: '' },
  { text: '按摩', value: '按摩' },
  { text: '理疗', value: '理疗' },
  { text: '跳舞', value: '跳舞' },
  { text: '唱歌', value: '唱歌' },
  { text: '健身', value: '健身' },
  { text: '摄影', value: '摄影' },
  { text: '化妆', value: '化妆' },
  { text: '烹饪', value: '烹饪' },
  { text: '陪玩', value: '陪玩' },
  { text: '其他', value: '其他' }
]

const list = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
let page = 1
const pageSize = 10

async function loadDemands() {
  if (refreshing.value) {
    page = 1
    list.value = []
    finished.value = false
    refreshing.value = false
  }

  if (finished.value) return

  loading.value = true
  try {
    const params = { page, page_size: pageSize }
    if (filters.skill_type) params.skill_type = filters.skill_type
    const res = await listDemands(params)
    const data = res.data || res
    const items = data.items || data || []
    list.value.push(...items)
    page++

    const total = data.total || data.total_count || items.length
    if (list.value.length >= total || items.length < pageSize) {
      finished.value = true
    }
  } catch (err) {
    showToast('加载失败')
  } finally {
    loading.value = false
  }
}

function onRefresh() {
  finished.value = false
  loading.value = true
  page = 1
  list.value = []
  loadDemands()
}
</script>

<style scoped>
.filter-bar {
  margin-bottom: 8px;
}
.demand-card {
  background: #fff;
  border-radius: 8px;
  padding: 14px;
  margin-bottom: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.demand-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
}
.demand-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}
.demand-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 12px;
  align-items: center;
}
.skill-tag {
  margin-top: 6px;
}
.empty {
  text-align: center;
  padding: 40px 0;
  color: #999;
  font-size: 14px;
}
.demand-creator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 6px 8px;
  background: #fff5f7;
  border-radius: 20px;
  cursor: pointer;
  width: fit-content;
}
.demand-creator:active {
  opacity: 0.7;
}
.creator-name {
  font-size: 12px;
  color: #ff4757;
  font-weight: 500;
}
.creator-arrow {
  color: #ff6b81;
  font-size: 10px;
}
.fab {
  position: fixed;
  bottom: 80px;
  right: 16px;
  z-index: 100;
}
</style>
