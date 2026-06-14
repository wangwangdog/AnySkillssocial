<template>
  <div class="page">
    <van-nav-bar title="消息" left-arrow @click-left="$router.back()" />

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <div v-if="loading" class="loading-tip"><van-loading /></div>
      <div v-else-if="list.length === 0" class="empty">暂无消息</div>
      <div
        v-for="item in list"
        :key="item.id"
        class="conv-card"
        @click="$router.push(`/chat/${item.id}`)"
      >
        <div class="conv-avatar">
          <van-image round width="48" height="48" :src="item.other_user?.avatar || defaultAvatar" />
          <van-badge v-if="item.unread > 0" :content="item.unread > 99 ? '99+' : item.unread" />
        </div>
        <div class="conv-info">
          <div class="conv-header">
            <div class="conv-name">{{ item.other_user?.nickname || '未知' }}</div>
            <div class="conv-time">{{ formatTime(item.last_time) }}</div>
          </div>
          <div class="conv-last">{{ item.last_message || '暂无消息' }}</div>
        </div>
      </div>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast } from 'vant'
import { getConversations } from '@/utils/api'

const list = ref([])
const loading = ref(true)
const refreshing = ref(false)
const defaultAvatar = 'https://randomuser.me/api/portraits/women/44.jpg'

onMounted(() => load())

async function load() {
  try {
    const res = await getConversations()
    list.value = res.data || res || []
  } catch {
    showToast('加载失败')
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

function onRefresh() {
  loading.value = true
  load()
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  const now = new Date()
  const pad = n => String(n).padStart(2, '0')
  const diff = now - d
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour

  if (diff < minute) return '刚刚'
  if (diff < hour) return `${Math.floor(diff / minute)}分钟前`
  if (diff < day) return `${Math.floor(diff / hour)}小时前`
  if (diff < 2 * day) return '昨天'
  if (diff < 7 * day) return `${Math.floor(diff / day)}天前`
  return `${pad(d.getMonth() + 1)}/${pad(d.getDate())}`
}
</script>

<style scoped>
.loading-tip {
  text-align: center;
  padding: 40px 0;
}
.empty {
  text-align: center;
  padding: 60px 0;
  color: #999;
  font-size: 14px;
}
.conv-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  padding: 14px;
  margin-bottom: 1px;
}
.conv-avatar {
  position: relative;
  flex-shrink: 0;
}
.conv-info {
  flex: 1;
  overflow: hidden;
}
.conv-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.conv-name {
  font-size: 15px;
  font-weight: 600;
}
.conv-time {
  font-size: 11px;
  color: #999;
}
.conv-last {
  font-size: 13px;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
