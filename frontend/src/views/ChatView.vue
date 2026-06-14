<template>
  <div class="page chat-page">
    <van-nav-bar :title="otherUser?.nickname || '聊天'" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon v-if="otherUser" name="contact" size="20" @click="$router.push(`/users/${otherUser.id}`)" />
      </template>
    </van-nav-bar>

    <div ref="msgContainer" class="msg-container" id="msg-container">
      <div v-if="loading" class="loading-tip"><van-loading /></div>
      <div v-for="msg in messages" :key="msg.id" :class="['msg-row', msg.sender_id === me?.id ? 'msg-right' : 'msg-left']">
        <div class="msg-bubble">{{ msg.content }}</div>
        <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
      </div>
    </div>

    <!-- Input bar -->
    <div class="input-bar">
      <van-field
        v-model="inputText"
        placeholder="输入消息..."
        :border="false"
        @keypress.enter="sendMsg"
        autosize
        type="textarea"
        rows="1"
      />
      <van-button
        :disabled="!inputText.trim()"
        type="primary"
        size="small"
        round
        style="margin-left:8px;flex-shrink:0"
        @click="sendMsg"
      >发送</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { showToast } from 'vant'
import { getMessages, sendMessage } from '@/utils/api'

const route = useRoute()
const messages = ref([])
const otherUser = ref(null)
const inputText = ref('')
const loading = ref(true)
const msgContainer = ref(null)
const me = computed(() => {
  const stored = localStorage.getItem('user')
  return stored ? JSON.parse(stored) : null
})

onMounted(async () => {
  await loadMessages()
})

async function loadMessages() {
  try {
    const res = await getMessages(route.params.id)
    const data = res.data || res
    messages.value = data.messages || []
    otherUser.value = data.other_user
  } catch {
    showToast('加载失败')
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

async function sendMsg() {
  const text = inputText.value.trim()
  if (!text || !otherUser.value) return
  inputText.value = ''

  // 临时显示
  messages.value.push({
    id: `temp-${Date.now()}`,
    sender_id: me.value?.id,
    content: text,
    is_read: false,
    created_at: new Date().toISOString(),
  })
  scrollToBottom()

  try {
    await sendMessage(otherUser.value.id, text)
  } catch (err) {
    showToast('发送失败')
  }
}

function scrollToBottom() {
  nextTick(() => {
    setTimeout(() => {
      const el = document.getElementById('msg-container')
      if (el) el.scrollTop = el.scrollHeight
    }, 50)
  })
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  const now = new Date()
  const pad = n => String(n).padStart(2, '0')
  if (d.toDateString() === now.toDateString()) {
    return `${pad(d.getHours())}:${pad(d.getMinutes())}`
  }
  return `${pad(d.getMonth() + 1)}/${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 0;
  padding-bottom: 0;
}
.msg-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  padding-bottom: 12px;
}
.loading-tip {
  text-align: center;
  padding: 24px;
}
.msg-row {
  margin-bottom: 12px;
  max-width: 80%;
}
.msg-left {
  margin-right: auto;
}
.msg-right {
  margin-left: auto;
}
.msg-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}
.msg-left .msg-bubble {
  background: #f0f0f0;
  color: #333;
  border-bottom-left-radius: 4px;
}
.msg-right .msg-bubble {
  background: linear-gradient(135deg, #ff4757, #ff6b81);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.msg-time {
  font-size: 11px;
  color: #999;
  margin-top: 3px;
  text-align: right;
}
.msg-left .msg-time {
  text-align: left;
  padding-left: 4px;
}
.msg-right .msg-time {
  text-align: right;
  padding-right: 4px;
}
.input-bar {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 8px 12px;
  border-top: 1px solid #f0f0f0;
}
.input-bar :deep(.van-field) {
  flex: 1;
}
</style>
