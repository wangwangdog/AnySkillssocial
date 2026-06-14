<template>
  <div class="page">
    <van-nav-bar title="需求详情" left-arrow @click-left="$router.back()" />

    <div v-if="loading" class="loading-wrap">
      <van-loading size="24px">加载中...</van-loading>
    </div>

    <template v-else-if="demand">
      <!-- Demand info -->
      <div class="detail-card">
        <div class="detail-title">{{ demand.title }}</div>
        <div class="detail-meta-row">
          <van-tag type="danger">¥{{ demand.budget || 0 }}</van-tag>
          <span class="meta-item">{{ demand.location || '未指定' }}</span>
        </div>
        <!-- Creator info -->
        <div class="creator-row" @click="$router.push(`/users/${demand.creator?.id}`)">
          <van-image round width="32" height="32" :src="demand.creator?.avatar || 'https://randomuser.me/api/portraits/women/44.jpg'" />
          <div class="creator-info">
            <div class="creator-nick">{{ demand.creator?.nickname || demand.creator?.phone || '匿名' }}</div>
            <div class="creator-label">发布者</div>
          </div>
          <van-icon name="arrow" class="creator-arw" />
        </div>
        <van-tag v-if="demand.skill_type" plain>{{ demand.skill_type }}</van-tag>
        <div v-if="demand.interview_bonus" class="bonus-tag">
          <van-icon name="gem-o" /> 面试有奖励
        </div>
        <div class="detail-desc">{{ demand.description }}</div>
      </div>

      <!-- Action buttons -->
      <div v-if="!isOwner" class="action-bar">
        <van-button
          round
          block
          type="primary"
          size="large"
          :disabled="applied"
          @click="handleApply"
        >
          {{ applied ? '已报名' : '报名' }}
        </van-button>
      </div>

      <!-- Applications (owner only) -->
      <div v-if="isOwner" class="section">
        <div class="section-title">报名列表</div>
        <div v-if="applications.length === 0" class="empty">暂无报名</div>
        <div v-for="app in applications" :key="app.id" class="app-card">
          <div class="app-header" style="cursor:pointer" @click="$router.push(`/users/${app.applicant?.id}`)">
            <van-image
              round
              width="36"
              height="36"
              :src="app.applicant?.avatar || 'https://randomuser.me/api/portraits/women/44.jpg'"
            />
            <div class="app-user">
              <div class="app-name">{{ app.applicant?.nickname || app.applicant?.phone || '匿名' }}</div>
              <div class="app-time">{{ formatTime(app.created_at) }}</div>
            </div>
            <van-tag :type="statusTagType(app.status)" plain>{{ app.status || '待处理' }}</van-tag>
          </div>
          <div v-if="app.message" class="app-message">{{ app.message }}</div>



          <!-- Accept / Reject buttons -->
          <div v-if="app.status === 'pending'" class="app-actions">
            <van-button size="small" type="primary" @click="acceptApp(app.id)">通过</van-button>
            <van-button size="small" plain @click="rejectApp(app.id)">拒绝</van-button>
          </div>
        </div>
      </div>

      <!-- Apply form (modal with video upload) -->
      <van-action-sheet v-model:show="showApplySheet" title="报名需求">
        <div class="apply-sheet">
          <van-field
            v-model="applyMessage"
            name="message"
            label="留言"
            type="textarea"
            placeholder="说说你的优势..."
            rows="3"
          />
          <van-uploader v-model="videoFileList" :max-count="1" :after-read="afterVideoRead" accept="video/*" preview-full-image>
            <van-cell title="上传视频介绍" is-link>
              <template #icon>
                <van-icon name="video-o" style="margin-right:6px" />
              </template>
            </van-cell>
          </van-uploader>
          <div v-if="applyVideo" class="video-preview">
            <video width="100%" controls :src="applyVideo"></video>
          </div>
          <div style="margin: 16px">
            <van-button round block type="primary" @click="submitApply" :loading="applying">
              提交报名
            </van-button>
          </div>
        </div>
      </van-action-sheet>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { getDemand, applyDemand, listApplications, acceptApplication, rejectApplication } from '@/utils/api'

const route = useRoute()
const demand = ref(null)
const loading = ref(true)
const applied = ref(false)
const isOwner = ref(false)

// Applications
const applications = ref([])

// Apply sheet
const showApplySheet = ref(false)
const applyMessage = ref('')
const applyVideo = ref('')
const videoFileList = ref([])
const applying = ref(false)

onMounted(async () => {
  await loadDemand()
  await checkOwner()
  if (isOwner.value) {
    await loadApplications()
  }
})

async function loadDemand() {
  try {
    const res = await getDemand(route.params.id)
    demand.value = res.data || res
    loading.value = false
  } catch {
    showToast('加载失败')
    loading.value = false
  }
}

function checkOwner() {
  const stored = localStorage.getItem('user')
  if (!stored || !demand.value) return
  const user = JSON.parse(stored)
  const creator = demand.value.creator
  isOwner.value = creator && (creator.id === user.id || creator.phone === user.phone)
  if (!isOwner.value) {
    // check if already applied
    applied.value = demand.value.applied === true
  }
}

async function loadApplications() {
  try {
    const res = await listApplications(route.params.id)
    applications.value = res.data || res || []
  } catch {
    // ignore
  }
}

function handleApply() {
  showApplySheet.value = true
}

function afterVideoRead(file) {
  applyVideo.value = file.objectUrl
  showToast('视频已选择（演示模式，上传功能待接入）')
}

async function submitApply() {
  applying.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })
  try {
    const payload = { message: applyMessage.value }
    if (applyVideo.value) payload.video_url = applyVideo.value
    await applyDemand(route.params.id, payload)
    showToast('报名成功')
    applied.value = true
    showApplySheet.value = false
  } catch (err) {
    const msg = err.response?.data?.detail || err.response?.data?.message || err.message || '报名失败'
    showToast(msg)
  } finally {
    closeToast()
    applying.value = false
  }
}

function statusTagType(status) {
  if (status === 'accepted') return 'success'
  if (status === 'rejected') return 'danger'
  return 'warning'
}

function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString()
}

async function acceptApp(appId) {
  showLoadingToast({ message: '处理中...', forbidClick: true })
  try {
    const res = await acceptApplication(route.params.id, appId)
    showToast('已通过，订单已创建')
    await loadApplications()
  } catch (err) {
    const msg = err.response?.data?.detail || err.message || '操作失败'
    showToast(msg)
  } finally {
    closeToast()
  }
}

async function rejectApp(appId) {
  showLoadingToast({ message: '处理中...', forbidClick: true })
  try {
    await rejectApplication(route.params.id, appId)
    showToast('已拒绝')
    await loadApplications()
  } catch (err) {
    const msg = err.response?.data?.detail || err.message || '操作失败'
    showToast(msg)
  } finally {
    closeToast()
  }
}
</script>

<style scoped>
.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}
.detail-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}
.detail-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 10px;
}
.detail-meta-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 13px;
  color: #666;
  flex-wrap: wrap;
}
.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}
.creator-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  padding: 8px 12px;
  background: #fff5f7;
  border-radius: 12px;
  cursor: pointer;
}
.creator-row:active {
  opacity: 0.7;
}
.creator-info {
  flex: 1;
}
.creator-nick {
  font-size: 14px;
  font-weight: 600;
  color: #ff4757;
}
.creator-label {
  font-size: 11px;
  color: #999;
}
.creator-arw {
  color: #ff6b81;
  font-size: 14px;
}
.bonus-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #fff7e6;
  color: #fa8c16;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  margin-top: 6px;
}
.detail-desc {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  margin-top: 12px;
  white-space: pre-wrap;
}
.action-bar {
  padding: 12px 0;
}
.section {
  margin-top: 16px;
}
.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}
.empty {
  text-align: center;
  padding: 24px;
  color: #999;
  font-size: 14px;
}
.app-card {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
}
.app-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
.app-user {
  flex: 1;
}
.app-name {
  font-size: 14px;
  font-weight: 500;
}
.app-time {
  font-size: 11px;
  color: #999;
}
.app-message {
  font-size: 13px;
  color: #666;
  margin-top: 8px;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 6px;
}
.app-video {
  margin-top: 8px;
}
.app-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}
.apply-sheet {
  padding: 16px;
}
.video-preview {
  padding: 12px 16px;
  text-align: center;
}
.video-preview video {
  max-height: 200px;
  border-radius: 8px;
  margin-bottom: 8px;
}
</style>
