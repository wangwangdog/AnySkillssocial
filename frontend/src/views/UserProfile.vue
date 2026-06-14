<template>
  <div class="page profile-page">
    <!-- 顶部返回 -->
    <div class="top-bar">
      <span class="top-back" @click="$router.back()">
        <van-icon name="arrow-left" />
      </span>
      <span class="top-title">个人主页</span>
      <span class="top-spacer"></span>
    </div>

    <div v-if="loading" class="loading-wrap">
      <van-loading size="24px">加载中...</van-loading>
    </div>

    <template v-else-if="profile">
      <!-- 头部大图区域 -->
      <div class="hero-area" :style="heroStyle">
        <div class="hero-avatar-row">
          <div class="hero-avatar" @click="previewAvatar">
            <van-image round width="72" height="72" :src="profile.avatar || defaultAvatar" />
          </div>
        </div>
        <div class="hero-info">
          <div class="hero-name">
            {{ profile.nickname }}
            <van-icon v-if="profile.is_skill_verified" name="medal" color="#ffd700" class="hero-verify" />
          </div>
          <div class="hero-sub">
            {{ [profile.age ? profile.age + '岁' : '', genderLabel, profile.residence_city, profile.education].filter(Boolean).join(' · ') }}
          </div>
        </div>
      </div>

      <!-- Bio -->
      <div v-if="profile.bio" class="bio-section">
        <div class="bio-text">{{ profile.bio }}</div>
      </div>

      <!-- 标签 -->
      <div v-if="profile.tags && profile.tags.length > 0" class="tags-row">
        <span v-for="(tag, idx) in profile.tags" :key="idx" class="tag-chip">#{{ tag }}</span>
      </div>

      <!-- 操作按钮 -->
      <div class="action-row">
        <template v-if="!isSelf">
          <van-button
            :class="['follow-btn', { followed: followed }]"
            round
            :icon="followed ? 'success' : 'plus'"
            @click="toggleFollow"
          >{{ followed ? '已关注' : '关注' }}</van-button>
          <van-button
            round
            class="msg-btn"
            icon="chat-o"
            @click="sendMsg"
          >发消息</van-button>
        </template>
        <template v-else>
          <van-button round class="publish-post-btn" icon="edit" @click="showPostDialog = true">发布动态</van-button>
          <van-button round class="msg-btn" icon="setting-o" @click="$router.push('/profile')">编辑资料</van-button>
        </template>
      </div>

      <!-- 统计行 -->
      <div class="stats-bar">
        <div class="stat-item">
          <div class="stat-val">{{ profile.follower_count || 0 }}</div>
          <div class="stat-label">粉丝</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <div class="stat-val">{{ profile.following_count || 0 }}</div>
          <div class="stat-label">关注</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <div class="stat-val">{{ profile.service_count || 0 }}</div>
          <div class="stat-label">服务</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <div class="stat-val">{{ profile.demand_count || 0 }}</div>
          <div class="stat-label">需求</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <div class="stat-val">{{ profile.rating_avg ? profile.rating_avg.toFixed(1) : '-' }}</div>
          <div class="stat-label">评分</div>
        </div>
      </div>

      <!-- 相册墙 -->
      <div v-if="albums.length > 0" class="album-section">
        <div class="section-label">📸 相册</div>
        <div class="album-grid">
          <div v-for="(a, idx) in albums" :key="a.id" class="album-item" @click="showAlbum(idx)">
            <van-image width="100%" height="100%" fit="cover" :src="a.url" />
          </div>
        </div>
      </div>
      <div v-else-if="profile.photos && profile.photos.length > 0" class="album-section">
        <div class="section-label">📸 相册</div>
        <div class="album-grid">
          <div v-for="(p, idx) in profile.photos" :key="idx" class="album-item" @click="showPhoto(idx)">
            <van-image width="100%" height="100%" fit="cover" :src="p" />
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <van-tabs v-model:active="activeTab" @change="loadTabData" class="profile-tabs" line-width="24px" color="#667eea" title-active-color="#667eea">
        <van-tab title="服务" name="services" />
        <van-tab title="需求" name="demands" />
        <van-tab title="动态" name="posts" />
      </van-tabs>

      <!-- 服务列表 -->
      <div v-if="activeTab === 'services'" class="tab-content">
        <div v-if="tabLoading" class="loading-tip"><van-loading /></div>
        <div v-else-if="services.length === 0" class="empty">暂无服务</div>
        <div v-for="item in services" :key="item.id" class="card-item" @click="$router.push('/services')">
          <div class="card-title">{{ item.title }}</div>
          <div class="card-meta">
            <van-tag v-if="item.skill_type" plain style="border-color:#667eea;color:#667eea">{{ item.skill_type }}</van-tag>
            <span class="card-price">¥{{ item.price }}</span>
          </div>
          <div class="card-desc">{{ item.description }}</div>
        </div>
      </div>

      <!-- 需求列表 -->
      <div v-if="activeTab === 'demands'" class="tab-content">
        <div v-if="tabLoading" class="loading-tip"><van-loading /></div>
        <div v-else-if="demands.length === 0" class="empty">暂无需求</div>
        <div v-for="item in demands" :key="item.id" class="card-item" @click="$router.push(`/demands/${item.id}`)">
          <div class="card-title">{{ item.title }}</div>
          <div class="card-meta">
            <van-tag v-if="item.skill_type" plain style="border-color:#667eea;color:#667eea">{{ item.skill_type }}</van-tag>
            <span class="card-budget">预算 ¥{{ item.budget || 0 }}</span>
          </div>
          <div v-if="item.location" class="card-location"><van-icon name="location-o" /> {{ item.location }}</div>
          <div class="card-desc">{{ item.description }}</div>
        </div>
      </div>

      <!-- 动态列表 -->
      <div v-if="activeTab === 'posts'" class="tab-content">
        <div v-if="tabLoading" class="loading-tip"><van-loading /></div>
        <div v-else-if="userPosts.length === 0" class="empty">暂无动态</div>
        <div v-for="item in userPosts" :key="item.id" class="post-card">
          <div class="post-content">{{ item.content }}</div>
          <div v-if="item.images && item.images.length > 0" class="post-imgs">
            <van-image v-for="(img, imgIdx) in item.images.slice(0, 3)" :key="imgIdx" width="100%" height="auto" fit="cover" :src="img" class="post-img" @click="showPostImg(item.images, imgIdx)" />
          </div>
          <div class="post-time">{{ formatTime(item.created_at) }}</div>
        </div>
      </div>

      <!-- 联系方式（付费解锁 · 页面最下方） -->
      <div v-if="profile.contact_price > 0 || isSelf" class="contact-section">
        <div v-if="isSelf" class="contact-unlocked">
          <div class="section-label">📞 我的联系方式</div>
          <div class="contact-item">📱 电话：{{ profile.contact_phone || '未设置' }}</div>
          <div class="contact-item">💬 QQ：{{ profile.contact_qq || '未设置' }}</div>
          <div class="contact-item">✉️ 微信：{{ profile.contact_wechat || '未设置' }}</div>
        </div>
        <div v-else-if="!profile.contact_unlocked" class="contact-locked">
          <div class="contact-lock-icon">🔒</div>
          <div class="contact-lock-text">查看联系方式</div>
          <van-button
            round
            class="unlock-btn"
            :loading="unlocking"
            @click="unlockContact"
          >付费 ¥{{ profile.contact_price }} 解锁</van-button>
          <div class="contact-hint">解锁后可查看电话、QQ、微信</div>
        </div>
        <div v-else class="contact-unlocked">
          <div class="section-label">📞 联系方式</div>
          <div class="contact-item">📱 电话：{{ profile.contact_phone }}</div>
          <div class="contact-item">💬 QQ：{{ profile.contact_qq }}</div>
          <div class="contact-item">✉️ 微信：{{ profile.contact_wechat }}</div>
        </div>
      </div>
    </template>

    <!-- 图片预览 -->
    <van-image-preview v-model:show="showPreview" :images="[profile?.avatar || defaultAvatar]" />
    <van-image-preview v-model:show="showPhotoPreview" :start-position="photoPreviewIndex" :images="photoList" />

    <!-- 发布动态弹窗 -->
    <van-action-sheet v-model:show="showPostDialog" title="发布动态" :close-on-click-action="false">
      <div class="post-editor">
        <van-field
          v-model="postContent"
          type="textarea"
          placeholder="分享你的技能或动态..."
          rows="4"
          maxlength="500"
          show-word-limit
          autosize
        />
        <div style="padding: 12px 16px">
          <van-button block round type="primary" color="#4CAF50" :loading="posting" @click="submitPost">发布</van-button>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast, showImagePreview } from 'vant'
import { getUserProfile, getUserServices, getUserDemands, getUserPosts, sendMessage, followUser, unfollowUser, checkFollow, unlockContact as unlockContactApi, createPost } from '@/utils/api'

const route = useRoute()
const router = useRouter()
const profile = ref(null)
const loading = ref(true)
const activeTab = ref('services')
const tabLoading = ref(false)
const services = ref([])
const demands = ref([])
const userPosts = ref([])
const showPreview = ref(false)
const photoPreviewIndex = ref(0)
const showPhotoPreview = ref(false)
const followed = ref(false)
const isSelf = ref(false)
const unlocking = ref(false)
const showPostDialog = ref(false)
const postContent = ref('')
const posting = ref(false)
const defaultAvatar = 'https://randomuser.me/api/portraits/women/44.jpg'

const genderLabel = computed(() => {
  const map = { male: '男', female: '女', other: '其他' }
  return profile.value?.gender ? map[profile.value.gender] || profile.value.gender : ''
})

const albums = computed(() => profile.value?.albums || [])

const photoList = computed(() => {
  if (albums.value.length > 0) return albums.value.map(a => a.url)
  return profile.value?.photos || []
})

const heroStyle = computed(() => {
  if (profile.value?.photos && profile.value.photos.length > 0) {
    return { backgroundImage: `url(${profile.value.photos[0]})` }
  }
  return {}
})

onMounted(async () => {
  await loadUser()
  await loadTabData()
  await loadFollowStatus()
})

async function loadUser() {
  try {
    const res = await getUserProfile(route.params.id)
    profile.value = res.data || res
    const token = localStorage.getItem('token')
    const currentUser = token ? JSON.parse(localStorage.getItem('user') || '{}') : null
    isSelf.value = currentUser && (currentUser.id === profile.value.id || currentUser.id === route.params.id)
  } catch {
    showToast('用户不存在')
  } finally { loading.value = false }
}

async function loadFollowStatus() {
  if (isSelf.value) return
  const token = localStorage.getItem('token')
  if (!token) return
  try {
    const res = await checkFollow(route.params.id)
    followed.value = res.followed === true
  } catch { /* ignore */ }
}

async function loadTabData() {
  tabLoading.value = true
  try {
    if (activeTab.value === 'services') {
      const res = await getUserServices(route.params.id)
      services.value = res.data || res || []
    } else if (activeTab.value === 'demands') {
      const res = await getUserDemands(route.params.id)
      demands.value = res.data || res || []
    } else {
      const res = await getUserPosts(route.params.id)
      userPosts.value = res.data || res || []
    }
  } catch { /* ignore */ }
  finally { tabLoading.value = false }
}

async function toggleFollow() {
  const token = localStorage.getItem('token')
  if (!token) { showToast('请先登录'); return router.push('/login') }
  try {
    if (followed.value) {
      const res = await unfollowUser(route.params.id)
      followed.value = false
      if (profile.value) profile.value.follower_count = res.follower_count
      showToast('已取消关注')
    } else {
      const res = await followUser(route.params.id)
      followed.value = true
      if (profile.value) profile.value.follower_count = res.follower_count
      showToast('关注成功')
    }
  } catch (err) {
    showToast('操作失败')
  }
}

function showPostImg(images, idx) { showImagePreview(images, idx) }

async function unlockContact() {
  const token = localStorage.getItem('token')
  if (!token) { showToast('请先登录'); return router.push('/login') }
  unlocking.value = true
  try {
    const res = await unlockContactApi(route.params.id)
    showToast('解锁成功！')
    if (profile.value) {
      profile.value.contact_unlocked = true
      profile.value.contact_phone = res.contact_phone || ''
      profile.value.contact_qq = res.contact_qq || ''
      profile.value.contact_wechat = res.contact_wechat || ''
    }
  } catch (err) {
    const msg = err.response?.data?.detail || '解锁失败'
    showToast(msg)
  } finally {
    unlocking.value = false
  }
}

function showAlbum(idx) { photoPreviewIndex.value = idx; showPhotoPreview.value = true }
function showPhoto(idx) { photoPreviewIndex.value = idx; showPhotoPreview.value = true }

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
  if (diff < 7 * day) return `${Math.floor(diff / day)}天前`
  return `${pad(d.getMonth() + 1)}/${pad(d.getDate())}`
}

async function sendMsg() {
  const token = localStorage.getItem('token')
  if (!token) { showToast('请先登录'); return router.push('/login') }
  showLoadingToast({ message: '正在连接...', forbidClick: true })
  try {
    const res = await sendMessage(profile.value.id, '你好')
    closeToast()
    router.push(`/chat/${res.conversation_id || (res.data && res.data.conversation_id)}`)
  } catch {
    closeToast(); showToast('发送失败')
  }
}

async function submitPost() {
  const content = postContent.value.trim()
  if (!content) { showToast('请输入内容'); return }
  posting.value = true
  try {
    await createPost({ content })
    showToast('发布成功')
    showPostDialog.value = false
    postContent.value = ''
    // 如果当前在动态 tab，刷新列表
    if (activeTab.value === 'posts') await loadTabData()
  } catch (err) {
    showToast('发布失败')
  } finally {
    posting.value = false
  }
}

function previewAvatar() { if (profile.value?.avatar) showPreview.value = true }
</script>

<style scoped>
.profile-page { padding-bottom: 70px; background: #f5f5f5; min-height: 100vh; }

/* ===== 顶部返回 ===== */
.top-bar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: linear-gradient(135deg, #f9536c 0%, #ff6f91 100%);
  color: #fff;
}
.top-back { font-size: 20px; cursor: pointer; padding: 4px; }
.top-title { font-size: 17px; font-weight: 700; }
.top-spacer { width: 28px; }

.loading-wrap { display: flex; justify-content: center; padding: 60px 0; }

/* ===== 头部大图 ===== */
.hero-area {
  background: linear-gradient(135deg, #f9536c 0%, #ff6f91 100%);
  background-size: cover;
  background-position: center;
  padding: 20px 16px 10px;
  position: relative;
  text-align: center;
  min-height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.hero-area::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.15);
}
.hero-avatar-row, .hero-info { position: relative; z-index: 1; }
.hero-avatar { cursor: pointer; margin-bottom: 10px; }
.hero-avatar :deep(.van-image__img) { border: 3px solid rgba(255,255,255,0.7); }
.hero-name {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.hero-verify { font-size: 18px; }
.hero-sub {
  font-size: 13px;
  color: rgba(255,255,255,0.85);
  margin-top: 4px;
}

/* ===== Bio ===== */
.bio-section {
  background: #fff;
  padding: 14px 16px;
  margin: 0;
}
.bio-text { font-size: 14px; color: #333; line-height: 1.8; white-space: pre-wrap; }

/* ===== 标签 ===== */
.tags-row {
  background: #fff;
  padding: 0 16px 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.tag-chip {
  font-size: 12px;
  color: #667eea;
  background: #f0f0ff;
  padding: 3px 10px;
  border-radius: 12px;
}

/* ===== 操作按钮 ===== */
.action-row {
  background: #fff;
  padding: 6px 16px 14px;
  display: flex;
  gap: 10px;
}
.follow-btn {
  flex: 1;
  border: 1px solid #667eea !important;
  color: #667eea !important;
  font-size: 14px;
}
.follow-btn.followed {
  background: #667eea !important;
  color: #fff !important;
  border: none !important;
}
.msg-btn {
  flex: 1;
  background: linear-gradient(135deg, #f9536c, #ff6f91) !important;
  color: #fff !important;
  border: none !important;
  font-size: 14px;
}
.publish-post-btn {
  flex: 1;
  background: #4CAF50 !important;
  color: #fff !important;
  border: none !important;
  font-size: 14px;
}

/* ===== 统计行 ===== */
.stats-bar {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 16px 0;
  margin-top: 8px;
}
.stat-item { flex: 1; text-align: center; }
.stat-val { font-size: 18px; font-weight: 700; color: #333; }
.stat-label { font-size: 11px; color: #999; margin-top: 3px; }
.stat-divider { width: 1px; height: 24px; background: #eee; }

/* ===== 相册 ===== */
.album-section {
  background: #fff;
  padding: 16px;
  margin-top: 8px;
}
.section-label { font-size: 14px; font-weight: 600; margin-bottom: 10px; color: #333; }

/* ===== 联系方式付费解锁 ===== */
.contact-section {
  background: #fff;
  padding: 20px 16px;
  margin-top: 8px;
}
.contact-locked {
  text-align: center;
  padding: 10px 0;
}
.contact-lock-icon { font-size: 32px; margin-bottom: 8px; }
.contact-lock-text { font-size: 16px; font-weight: 600; color: #333; margin-bottom: 12px; }
.contact-hint { font-size: 12px; color: #999; margin-top: 10px; }
.unlock-btn {
  background: linear-gradient(135deg, #f06d51, #ee0a24) !important;
  color: #fff !important;
  border: none !important;
  padding: 0 24px;
  font-size: 15px;
}
.post-editor {
  min-height: 200px;
  padding: 8px 0 20px;
}
.contact-unlocked { padding: 4px 0; }
.contact-item {
  font-size: 14px;
  color: #333;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}
.contact-item:last-child { border-bottom: none; }

.album-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 4px;
}
.album-item {
  aspect-ratio: 1;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  background: #f5f5f5;
}
.album-item:active { opacity: 0.8; }

/* ===== Tabs ===== */
.profile-tabs { margin-top: 8px; }
.profile-tabs :deep(.van-tabs__wrap) { background: #fff; }

/* ===== Tab content ===== */
.tab-content { padding: 0 12px; margin-top: 8px; }
.loading-tip { text-align: center; padding: 24px; }
.empty { text-align: center; padding: 40px 0; color: #999; font-size: 14px; }
.card-item {
  background: #fff;
  border-radius: 10px;
  padding: 14px;
  margin-bottom: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.card-title { font-size: 15px; font-weight: 600; margin-bottom: 8px; }
.card-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.card-price { color: #ee0a24; font-weight: 600; font-size: 14px; }
.card-budget { color: #667eea; font-weight: 500; font-size: 13px; }
.card-location { font-size: 12px; color: #999; margin-bottom: 4px; }
.card-desc { font-size: 13px; color: #666; line-height: 1.5; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }

/* ===== Post ===== */
.post-card {
  background: #fff;
  border-radius: 10px;
  padding: 14px;
  margin-bottom: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.post-content { font-size: 14px; color: #333; line-height: 1.8; white-space: pre-wrap; }
.post-imgs { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 8px; }
.post-img { border-radius: 6px; overflow: hidden; min-height: 100px; background: #f5f5f5; cursor: pointer; }
.post-time { font-size: 11px; color: #999; margin-top: 8px; }
</style>
