<template>
  <div id="app-root">
    <router-view />
    <van-tabbar v-if="showTabbar" route active-color="#4CAF50" inactive-color="#666" placeholder>
      <van-tabbar-item to="/" icon="home-o">首页</van-tabbar-item>
      <van-tabbar-item to="/bounty" icon="bullhorn-o">悬赏大厅</van-tabbar-item>
      <!-- 中间发布按钮 -->
      <van-tabbar-item :to="null" @click="showPublishSheet = true">
        <template #icon>
          <div class="publish-btn">+</div>
        </template>
        <span style="color:#4CAF50;font-weight:600;font-size:10px">发布</span>
      </van-tabbar-item>
      <van-tabbar-item to="/square" icon="cluster-o">服务广场</van-tabbar-item>
      <van-tabbar-item to="/profile" icon="contact-o">我的</van-tabbar-item>
    </van-tabbar>

    <!-- ===== 发布弹窗 (Bottom Sheet) ===== -->
    <div
      v-if="showPublishSheet"
      class="publish-overlay"
      :class="{ 'publish-overlay-show': showPublishSheet }"
      @click.self="closeSheet"
    >
      <div class="publish-sheet" :class="{ 'publish-sheet-show': showPublishSheet }">
        <!-- 弹窗头部 -->
        <div class="ps-header">
          <span class="ps-title">发布内容</span>
          <span class="ps-close" @click="closeSheet">×</span>
        </div>

        <!-- 拖拽指示条 -->
        <div class="ps-drag-bar"></div>

        <!-- 发布选项 -->
        <div class="ps-options">
          <div class="ps-option" @click="onPublish('bounty')">
            <div class="ps-icon-wrap" style="background:#E3F2FD">
              <span class="ps-icon">📢</span>
            </div>
            <span class="ps-label">发布悬赏</span>
          </div>
          <div class="ps-option" @click="onPublish('post')">
            <div class="ps-icon-wrap" style="background:#FFEBEE">
              <span class="ps-icon">🖼️</span>
            </div>
            <span class="ps-label">发布动态</span>
          </div>
          <div class="ps-option" @click="onPublish('companion')">
            <div class="ps-icon-wrap" style="background:#F3E5F5">
              <span class="ps-icon">🔍</span>
            </div>
            <span class="ps-label">找人陪玩</span>
          </div>
        </div>

        <!-- 取消按钮 -->
        <div class="ps-cancel" @click="closeSheet">取消</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'

const route = useRoute()
const router = useRouter()
const hidePages = ['login', 'register']
const showTabbar = computed(() => !hidePages.includes(route.name))

const showPublishSheet = ref(false)

// 拖拽起始 Y
let touchStartY = 0

function closeSheet() {
  showPublishSheet.value = false
}

function onPublish(type) {
  showPublishSheet.value = false
  const token = localStorage.getItem('token')
  if (!token) return router.push('/login')

  if (type === 'bounty') {
    // 发布悬赏 → 对外发布个人的服务提供
    router.push('/services/create')
  } else if (type === 'post') {
    // 发布动态 → 个人主页动态页
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    if (user.id) router.push('/users/' + user.id)
    else router.push('/profile')
  } else if (type === 'companion') {
    // 找人陪玩 → 发布需求
    router.push('/demands/create')
  }
}

// Touch drag to close
function onTouchStart(e) {
  touchStartY = e.touches[0].clientY
}
function onTouchMove(e) {
  const diff = e.touches[0].clientY - touchStartY
  if (diff > 100) closeSheet()
}
</script>

<style scoped>
/* ===== 发布按钮 ===== */
.publish-btn {
  width: 44px;
  height: 44px;
  background: #F44336;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 300;
  color: #FFF;
  line-height: 1;
  margin-top: -16px;
  box-shadow: 0 2px 8px rgba(244, 67, 54, 0.4);
}

/* ===== 遮罩 ===== */
.publish-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 2000;
  display: flex;
  align-items: flex-end;
  opacity: 0;
  transition: opacity 300ms ease-out;
}
.publish-overlay-show {
  opacity: 1;
}

/* ===== 弹窗容器 ===== */
.publish-sheet {
  width: 100%;
  background: #FFF;
  border-radius: 22px 22px 0 0;
  padding: 0 16px;
  padding-bottom: calc(16px + env(safe-area-inset-bottom, 0px));
  transform: translateY(100%);
  transition: transform 300ms ease-out;
}
.publish-sheet-show {
  transform: translateY(0);
}

/* ===== 拖拽指示条 ===== */
.ps-drag-bar {
  width: 36px;
  height: 4px;
  background: #E0E0E0;
  border-radius: 2px;
  margin: 8px auto;
}

/* ===== 头部 ===== */
.ps-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}
.ps-title {
  font-size: 20px;
  font-weight: 700;
  color: #333;
}
.ps-close {
  font-size: 24px;
  color: #666;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
}

/* ===== 选项区 ===== */
.ps-options {
  display: flex;
  justify-content: space-around;
  padding: 20px 0 28px;
}
.ps-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: transform 0.15s;
}
.ps-option:active {
  transform: scale(0.95);
  opacity: 0.8;
}
.ps-icon-wrap {
  width: 76px;
  height: 76px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
}
.ps-icon {
  line-height: 1;
}
.ps-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* ===== 取消按钮 ===== */
.ps-cancel {
  text-align: center;
  padding: 14px 0;
  font-size: 16px;
  color: #009688;
  cursor: pointer;
  border-top: 1px solid #E0E0E0;
}
.ps-cancel:active {
  opacity: 0.7;
}
</style>
