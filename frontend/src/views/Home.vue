<template>
  <div class="home-page">
    <!-- ===== 顶部 Header ===== -->
    <div class="home-header">
      <div class="header-left">
        <div class="app-name">Taba</div>
        <div class="app-slogan">连接技能，变现未来</div>
      </div>
      <div class="header-right" @click="$router.push('/notifications')">
        <div class="bell-wrap">
          <van-icon name="bell" size="22" color="#333" />
          <span class="bell-dot"></span>
        </div>
      </div>
    </div>

    <!-- ===== 搜索栏 ===== -->
    <div class="search-bar" @click="$router.push('/square')">
      <van-icon name="search" size="16" color="#999" />
      <span class="search-placeholder">搜索技能、达人、需求...</span>
    </div>

    <!-- ===== 每日签到卡片 ===== -->
    <div class="checkin-card" @click="handleCheckinClick">
      <div class="checkin-left">
        <div class="checkin-title">
          <span class="checkin-icon">📅</span>
          <span>每日签到</span>
        </div>
        <div class="checkin-streak">已连续签到 {{ checkinDays }} 天</div>
        <div class="checkin-progress-bar">
          <div class="checkin-progress-fill" :style="{ width: checkinProgress + '%' }"></div>
        </div>
      </div>
      <div class="checkin-right">
        <div class="checkin-btn" :class="{ done: checkedIn }">
          {{ checkedIn ? '已签到' : '去签到' }}
        </div>
        <div class="checkin-hint">再签到 {{ daysToReward }} 天额外获得 1 权益</div>
      </div>
    </div>

    <!-- ===== 浏览次数提示条 ===== -->
    <div class="browse-hint">
      <div class="hint-left">
        <span class="hint-icon">⚠️</span>
        <span class="hint-text">今日还可浏览 <em class="hint-highlight">{{ browseRemaining }}</em> 次达人信息</span>
      </div>
      <div class="hint-right" @click="refreshBrowse">
        <span class="refresh-btn">刷新</span>
      </div>
    </div>

    <!-- ===== Banner 轮播 ===== -->
    <div class="banner-wrap">
      <van-swipe :autoplay="3000" indicator-color="white" class="banner-swipe">
        <van-swipe-item v-for="(banner, idx) in banners" :key="idx" class="banner-item" @click="onBannerClick(banner)">
          <div class="banner-bg" :style="{ background: banner.bg }">
            <div class="banner-main-text">{{ banner.title }}</div>
            <div class="banner-sub-text">{{ banner.subtitle }}</div>
            <div class="banner-tag">{{ banner.tag }}</div>
          </div>
        </van-swipe-item>
      </van-swipe>
    </div>

    <!-- ===== 分类导航 ===== -->
    <div class="section-wrap">
      <div class="section-title">分类导航</div>
      <div class="category-grid">
        <div
          v-for="cat in categories"
          :key="cat.name"
          class="category-item"
          @click="onCategoryClick(cat)"
        >
          <div class="cat-icon-wrap" :style="{ background: cat.bg }">
            <span class="cat-icon">{{ cat.icon }}</span>
          </div>
          <div class="cat-name">{{ cat.name }}</div>
        </div>
      </div>
    </div>

    <!-- ===== 推荐服务者（精简卡片流） ===== -->
    <div class="section-wrap">
      <div class="section-title">推荐达人</div>
      <div v-if="recommendList.length === 0" class="empty-section">暂无推荐</div>
      <div v-else class="rec-horizontal">
        <div
          v-for="p in recommendList.slice(0, 6)"
          :key="p.id"
          class="rec-card"
          @click="$router.push(p.seller ? `/services/${p.id}` : `/users/${p.id}`)"
        >
          <div class="rec-avatar-wrap">
            <van-image round width="52" height="52" fit="cover" :src="p.seller?.avatar || p.avatar || defaultAvatar" />
            <span class="rec-online"></span>
          </div>
          <div class="rec-name van-ellipsis">{{ p.seller?.nickname || p.nickname || '匿名' }}</div>
          <div class="rec-skill van-ellipsis">{{ p.skill_type || (p.tags && p.tags[0]) || '' }}</div>
          <div class="rec-price">¥{{ p.price || 0 }}/次</div>
        </div>
      </div>
    </div>

    <!-- ===== 精选动态 Feed ===== -->
    <div class="feed-section">
      <div class="feed-header">
        <span class="feed-title">精选动态</span>
        <span class="feed-more" @click="$router.push('/messages')">
          更多动态 <van-icon name="arrow" size="12" />
        </span>
      </div>

      <div class="feed-list">
        <!-- 样式一：双图横排 -->
        <div
          v-for="(item, idx) in feedList"
          :key="'f'+idx"
          class="feed-card"
          :class="{ 'feed-card-single': item.layout === 'single' }"
          @click="onFeedClick(item)"
        >
          <!-- 用户信息区 -->
          <div class="feed-user">
            <div class="feed-user-left">
              <van-image round width="44" height="44" fit="cover" :src="item.avatar" />
              <div class="feed-user-info">
                <div class="feed-user-name-row">
                  <span class="feed-user-name">{{ item.nickname }}</span>
                  <span v-if="item.verified" class="feed-badge-verified">✓ 实名</span>
                  <span v-if="item.vip" class="feed-badge-vip">👑 黑金</span>
                </div>
                <div class="feed-time">{{ item.time }}</div>
              </div>
            </div>
            <div class="feed-user-right" v-if="!item.followed" @click.stop="onFollow(item)">
              <span class="feed-follow-btn">关注</span>
            </div>
          </div>

          <!-- 文字内容 -->
          <div class="feed-text">{{ item.text }}</div>

          <!-- 图片区：双图 -->
          <div v-if="item.layout === 'dual'" class="feed-imgs-dual">
            <div v-for="(img, iidx) in item.images" :key="iidx" class="feed-img-wrap-dual">
              <van-image width="100%" height="100%" fit="cover" :src="img" class="feed-img" />
              <span class="feed-img-tag">AI生成</span>
            </div>
          </div>

          <!-- 图片区：单图大图 -->
          <div v-if="item.layout === 'single'" class="feed-img-single">
            <van-image width="100%" height="200px" fit="cover" :src="item.images[0]" class="feed-img" />
            <span class="feed-img-tag">AI生成</span>
          </div>

          <!-- 互动操作栏 -->
          <div class="feed-actions">
            <div class="feed-action-item" @click.stop="toggleLike(item)">
              <van-icon :name="item.liked ? 'like' : 'like-o'" :color="item.liked ? '#FF4757' : '#999'" size="18" />
              <span :class="['feed-action-num', { liked: item.liked }]">{{ item.likes > 0 ? item.likes : '点赞' }}</span>
            </div>
            <div class="feed-action-item">
              <van-icon name="chat-o" color="#999" size="18" />
              <span class="feed-action-num">{{ item.comments > 0 ? item.comments : '评论' }}</span>
            </div>
            <div class="feed-action-item" @click.stop="onTip(item)">
              <van-icon name="gold-coin-o" color="#999" size="18" />
              <span class="feed-action-num">打赏</span>
            </div>
            <div class="feed-action-item" @click.stop="onShare(item)">
              <van-icon name="share-o" color="#999" size="18" />
              <span class="feed-action-num">分享</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { getMe, doCheckin, getCheckinStatus, getRecommendProviders } from '@/utils/api'

const router = useRouter()
const defaultAvatar = 'https://randomuser.me/api/portraits/women/44.jpg'

// === 签到 ===
const checkedIn = ref(false)
const checkinDays = ref(0)
const daysToReward = ref(7)
const checkinProgress = ref(0)

// Watch checkinDays to update progress
import { watch } from 'vue'
watch(checkinDays, (val) => {
  const target = 7 // 7天一个周期
  checkinProgress.value = Math.min(Math.round((val % target) / target * 100), 100)
  daysToReward.value = Math.max(target - (val % target), 0)
})

// === 浏览次数 ===
const browseRemaining = ref(3)

// === Banner 数据 ===
const banners = [
  { title: 'GREEN TECK', subtitle: 'EVENT PKIA | K2-9', tag: 'AIGC', bg: 'linear-gradient(135deg, #1B5E20, #4CAF50)' },
  { title: '达人招募', subtitle: '加入我们，技能变现', tag: '招募', bg: 'linear-gradient(135deg, #1565C0, #42A5F5)' },
  { title: '限时活动', subtitle: '新用户首单立减', tag: '优惠', bg: 'linear-gradient(135deg, #E65100, #FF9800)' },
]

// === 分类导航 ===
const categories = [
  { icon: '🎬', name: '影视演员', bg: '#FFEBEE' },
  { icon: '📷', name: '摄影师', bg: '#E3F2FD' },
  { icon: '💄', name: '化妆师', bg: '#F3E5F5' },
  { icon: '🎤', name: '主持人', bg: '#E8F5E9' },
  { icon: '👜', name: '模特礼仪', bg: '#FFF8E1' },
  { icon: '🎵', name: '歌手乐手', bg: '#FCE4EC' },
]

// === 推荐达人 ===
const recommendList = ref([])

// === 精选动态 Feed ===
const feedList = ref([
  {
    userId: 10,
    layout: 'dual',
    avatar: 'https://randomuser.me/api/portraits/women/10.jpg',
    nickname: '测试用户10_ion',
    verified: true,
    vip: false,
    time: '2小时前',
    followed: false,
    text: '第一次尝试AI摄影创作，效果惊艳！在西湖边拍摄了一组古风人像，光影质感完全不输专业摄影棚。大家觉得怎么样？',
    images: [
      'https://picsum.photos/seed/girl_photo1/400/400',
      'https://picsum.photos/seed/girl_photo2/400/400',
    ],
    likes: 128,
    comments: 36,
    liked: false,
  },
  {
    userId: 15,
    layout: 'single',
    avatar: 'https://randomuser.me/api/portraits/women/15.jpg',
    nickname: '测试用户15_t3h',
    verified: true,
    vip: true,
    time: '5小时前',
    followed: false,
    text: '新接了一个品牌代言，团队配合越来越默契了。商业拍摄的质感确实和日常不一样，期待成片上线！',
    images: [
      'https://picsum.photos/seed/girl_photo3/600/400',
    ],
    likes: 356,
    comments: 89,
    liked: true,
  },
])

function toggleLike(item) {
  item.liked = !item.liked
  item.likes += item.liked ? 1 : -1
}

function onFollow(item) {
  item.followed = true
  showToast('已关注')
  const token = localStorage.getItem('token')
  if (token && item.userId) {
    import('@/utils/api').then(m => m.followUser(item.userId)).catch(() => {})
  }
}

function onFeedClick(item) {
  router.push('/users/' + item.userId)
}

function onTip(item) {
  const token = localStorage.getItem('token')
  if (!token) return router.push('/login')
  showToast('打赏功能开发中')
}

function onShare(item) {
  showToast('已复制链接')
}

onMounted(async () => {
  await Promise.all([
    loadCheckinStatus(),
    loadRecommend(),
  ])
})

async function loadCheckinStatus() {
  try {
    const res = await getCheckinStatus()
    const d = res.data || res
    checkedIn.value = d.checked_in_today === true
    if (d.streak) checkinDays.value = d.streak
  } catch { /* ignore */ }
}

async function loadRecommend() {
  try {
    const res = await getRecommendProviders()
    const items = res.data || []
    if (items.length > 0) recommendList.value = items
  } catch { /* ignore */ }
}

function handleCheckinClick() {
  const token = localStorage.getItem('token')
  if (!token) return router.push('/login')
  if (checkedIn.value) {
    showToast('今日已签到')
    return
  }
  doCheckin().then((res) => {
    checkedIn.value = true
    const d = res.data || res
    if (d.streak) checkinDays.value = d.streak
    const msg = d.bonus ? '签到成功 🎉\n' + d.bonus : '签到成功 🎉'
    showToast(msg)
  }).catch((err) => {
    const msg = err.response?.data?.detail || '签到失败'
    showToast(msg)
  })
}

function refreshBrowse() {
  browseRemaining.value = 3
  showToast('已刷新')
}

function onBannerClick(banner) {
  // TODO: navigate to banner detail page
}

function onCategoryClick(cat) {
  router.push(`/square?skill=${cat.name}`)
}
</script>

<style scoped>
.home-page {
  background: #F5F5F5;
  min-height: 100vh;
  padding-bottom: 70px;
}

/* ===== Header ===== */
.home-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 16px 0;
  background: #F5F5F5;
}
.header-left {}
.app-name {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  line-height: 1.2;
}
.app-slogan {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}
.header-right {
  padding-top: 6px;
}
.bell-wrap {
  position: relative;
  padding: 4px;
}
.bell-dot {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 8px;
  height: 8px;
  background: #FF5252;
  border-radius: 50%;
  border: 2px solid #F5F5F5;
}

/* ===== Search Bar ===== */
.search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 12px 16px;
  padding: 0 12px;
  height: 44px;
  background: #FFF;
  border-radius: 22px;
  border: 1px solid #E0E0E0;
  cursor: pointer;
}
.search-placeholder {
  font-size: 14px;
  color: #999;
}

/* ===== Check-in Card ===== */
.checkin-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0 16px 8px;
  padding: 16px;
  background: linear-gradient(135deg, #4CAF50, #2E7D32);
  border-radius: 14px;
  cursor: pointer;
}
.checkin-left { flex: 1; }
.checkin-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  font-weight: 700;
  color: #FFF;
  margin-bottom: 4px;
}
.checkin-icon { font-size: 18px; }
.checkin-streak {
  font-size: 12px;
  color: rgba(255,255,255,0.85);
  margin-bottom: 8px;
}
.checkin-progress-bar {
  width: 80%;
  height: 4px;
  background: rgba(255,255,255,0.3);
  border-radius: 2px;
  overflow: hidden;
}
.checkin-progress-fill {
  height: 100%;
  background: #FFF;
  border-radius: 2px;
  transition: width 0.3s;
}
.checkin-right {
  text-align: center;
  flex-shrink: 0;
  margin-left: 12px;
}
.checkin-btn {
  display: inline-block;
  padding: 6px 16px;
  background: #FFF;
  color: #4CAF50;
  font-size: 13px;
  font-weight: 600;
  border-radius: 20px;
  margin-bottom: 6px;
}
.checkin-btn.done {
  background: rgba(255,255,255,0.2);
  color: #FFF;
}
.checkin-hint {
  font-size: 10px;
  color: rgba(255,255,255,0.75);
}

/* ===== Browse Hint ===== */
.browse-hint {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0 16px 8px;
  padding: 10px 12px;
  background: #FFF8E1;
  border-radius: 10px;
}
.hint-left {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #666;
}
.hint-icon { font-size: 14px; }
.hint-highlight {
  font-style: normal;
  color: #FF9800;
  font-weight: 700;
}
.refresh-btn {
  display: inline-block;
  padding: 4px 14px;
  background: #FF9800;
  color: #FFF;
  font-size: 12px;
  border-radius: 14px;
  cursor: pointer;
}

/* ===== Banner ===== */
.banner-wrap {
  margin: 0 16px 12px;
  border-radius: 14px;
  overflow: hidden;
}
.banner-swipe {
  border-radius: 14px;
}
.banner-item {
  height: 170px;
}
.banner-bg {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 24px;
  position: relative;
}
.banner-main-text {
  font-size: 26px;
  font-weight: 800;
  color: #FFF;
  letter-spacing: 2px;
}
.banner-sub-text {
  font-size: 13px;
  color: rgba(255,255,255,0.85);
  margin-top: 6px;
}
.banner-tag {
  position: absolute;
  bottom: 14px;
  right: 14px;
  padding: 3px 10px;
  background: rgba(0,0,0,0.45);
  color: #FFF;
  font-size: 11px;
  border-radius: 10px;
}

/* ===== Section ===== */
.section-wrap {
  margin: 0 16px 16px;
}
.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
}

/* ===== Category Grid ===== */
.category-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}
.cat-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.cat-name {
  font-size: 13px;
  color: #666;
  text-align: center;
}

/* ===== 推荐达人横向卡片 ===== */
.rec-horizontal {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: none;
}
.rec-horizontal::-webkit-scrollbar { display: none; }
.rec-card {
  flex-shrink: 0;
  width: 108px;
  background: #FFF;
  border-radius: 12px;
  padding: 12px;
  text-align: center;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.rec-avatar-wrap {
  position: relative;
  display: inline-block;
  margin-bottom: 6px;
}
.rec-online {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 10px;
  height: 10px;
  background: #4CAF50;
  border-radius: 50%;
  border: 2px solid #FFF;
}
.rec-name {
  font-size: 13px;
  font-weight: 600;
  color: #333;
}
.rec-skill {
  font-size: 11px;
  color: #999;
  margin-top: 2px;
}
.rec-price {
  font-size: 12px;
  color: #4CAF50;
  font-weight: 600;
  margin-top: 4px;
}
.empty-section {
  text-align: center;
  color: #999;
  padding: 24px 0;
  font-size: 14px;
}

/* ===== Feed 精选动态 ===== */
.feed-section {
  padding: 0 16px;
  margin-bottom: 16px;
}
.feed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}
.feed-title {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}
.feed-more {
  font-size: 13px;
  color: #00BCD4;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 2px;
}
.feed-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.feed-card {
  background: #FFF;
  border-radius: 12px;
  padding: 14px;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
/* 用户信息行 */
.feed-user {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.feed-user-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.feed-user-name-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.feed-user-name {
  font-size: 16px;
  font-weight: 700;
  color: #333;
}
.feed-badge-verified {
  display: inline-block;
  padding: 1px 6px;
  font-size: 10px;
  color: #00BCD4;
  background: #E0F7FA;
  border-radius: 8px;
  line-height: 1.4;
}
.feed-badge-vip {
  display: inline-block;
  padding: 1px 8px;
  font-size: 10px;
  color: #FFF;
  background: linear-gradient(135deg, #D4A017, #8B6914);
  border-radius: 8px;
  line-height: 1.4;
  font-weight: 600;
}
.feed-time {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}
.feed-follow-btn {
  display: inline-block;
  padding: 4px 14px;
  font-size: 12px;
  color: #00BCD4;
  border: 1px solid #00BCD4;
  border-radius: 14px;
  cursor: pointer;
  font-weight: 500;
}
/* 文本内容 */
.feed-text {
  font-size: 14px;
  color: #555;
  line-height: 1.6;
  margin-bottom: 10px;
}
/* 图片区 - 双图 */
.feed-imgs-dual {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 10px;
}
.feed-img-wrap-dual {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 1;
}
/* 图片区 - 单图 */
.feed-img-single {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 10px;
}
.feed-img {
  display: block;
  border-radius: 8px;
}
.feed-img-tag {
  position: absolute;
  bottom: 6px;
  right: 6px;
  padding: 2px 8px;
  font-size: 10px;
  color: #FFF;
  background: rgba(0,0,0,0.5);
  border-radius: 8px;
}
/* 互动操作栏 */
.feed-actions {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid #F0F0F0;
}
.feed-action-item {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 4px 8px;
}
.feed-action-num {
  font-size: 12px;
  color: #999;
}
.feed-action-num.liked {
  color: #FF4757;
}
</style>
