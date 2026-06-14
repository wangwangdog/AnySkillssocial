<template>
  <div class="page">
    <van-nav-bar title="系统通知" left-arrow @click-left="$router.back()">
      <template #right>
        <span v-if="hasUnread" class="read-all" @click="markAllRead">全部已读</span>
      </template>
    </van-nav-bar>

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <div v-if="loading" class="loading-tip"><van-loading /></div>
      <div v-else-if="list.length === 0" class="empty">暂无通知</div>
      <div
        v-for="item in list"
        :key="item.id"
        class="notif-card"
        :class="{ unread: !item.is_read }"
        @click="handleClick(item)"
      >
        <div class="notif-dot" v-if="!item.is_read"></div>
        <div class="notif-icon">
          <van-icon :name="iconMap[item.type] || 'info-o'" :color="iconColor(item)" size="22" />
        </div>
        <div class="notif-content">
          <div class="notif-title">{{ item.title }}</div>
          <div v-if="item.content" class="notif-text van-multi-ellipsis--l2">{{ item.content }}</div>
          <div class="notif-time">{{ formatTime(item.created_at) }}</div>
        </div>
        <van-icon v-if="item.related_id" name="arrow" class="notif-arrow" />
      </div>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { getNotifications, markNotificationRead, markAllNotificationsRead } from '@/utils/api'

const router = useRouter()
const list = ref([])
const loading = ref(true)
const refreshing = ref(false)

const iconMap = { system: 'info-o', message: 'chat-o', order: 'bill-o' }

const hasUnread = computed(() => list.value.some(n => !n.is_read))

onMounted(() => load())

async function load() {
  try {
    const res = await getNotifications()
    list.value = res.data || res || []
  } catch {
    // ignore
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

function onRefresh() {
  loading.value = true
  load()
}

function iconColor(item) {
  if (item.is_read) return '#999'
  if (item.type === 'order') return '#ff4757'
  if (item.type === 'message') return '#ff6b81'
  return '#1989fa'
}

function handleClick(item) {
  // 标记已读
  if (!item.is_read) {
    markNotificationRead(item.id).catch(() => {})
    item.is_read = true
  }
  // 消息通知跳转到聊天
  if (item.type === 'message' && item.related_id) {
    router.push(`/chat/${item.related_id}`)
  }
}

async function markAllRead() {
  try {
    await markAllNotificationsRead()
    list.value.forEach(n => (n.is_read = true))
    showToast('已全部标记已读')
  } catch {
    showToast('操作失败')
  }
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  const now = new Date()
  const pad = n => String(n).padStart(2, '0')
  const diff = now - d
  if (diff < 60 * 1000) return '刚刚'
  if (diff < 60 * 60 * 1000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 24 * 60 * 60 * 1000) return `${Math.floor(diff / 3600000)}小时前`
  if (d.toDateString() === now.toDateString()) return '今天'
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (d.toDateString() === yesterday.toDateString()) return '昨天'
  return `${pad(d.getMonth() + 1)}/${pad(d.getDate())}`
}
</script>

<style scoped>
.loading-tip {
  text-align: center;
  padding: 40px 0;
}
.read-all {
  font-size: 13px;
  color: #ff4757;
}
.empty {
  text-align: center;
  padding: 60px 0;
  color: #999;
  font-size: 14px;
}
.notif-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #fff;
  padding: 14px;
  margin-bottom: 1px;
  position: relative;
}
.notif-card.unread {
  background: #fff8f8;
}
.notif-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ff4757;
  flex-shrink: 0;
  margin-top: 6px;
}
.notif-icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff5f7;
  border-radius: 50%;
}
.notif-content {
  flex: 1;
  min-width: 0;
}
.notif-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 2px;
}
.notif-card.unread .notif-title {
  font-weight: 600;
}
.notif-text {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 4px;
}
.notif-time {
  font-size: 11px;
  color: #999;
}
.notif-arrow {
  color: #ccc;
  margin-top: 4px;
}
</style>
