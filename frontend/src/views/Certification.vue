<template>
  <div class="page cert-page">
    <van-nav-bar title="诚信认证" left-arrow @click-left="$router.back()" />

    <div v-if="loading" class="loading-wrap"><van-loading size="24px">加载中...</van-loading></div>

    <template v-else>
      <!-- 星级展示 -->
      <div class="stars-card">
        <div class="stars-title">诚信星级</div>
        <div class="stars-row">
          <van-icon v-for="s in 3" :key="s" :name="s <= cert.stars ? 'star' : 'star-o'"
            :color="s <= cert.stars ? '#ffd700' : '#ddd'" size="36" />
        </div>
        <div class="stars-desc">
          {{ cert.stars > 0 ? `已完成 ${cert.stars}/3 项认证` : '尚未完成任何认证' }}
        </div>
      </div>

      <!-- 认证项目 -->
      <div class="cert-list">
        <div v-for="(item, idx) in cert.items" :key="item.key" class="cert-item">
          <div class="cert-icon-wrap">
            <van-icon :name="icons[idx]" size="24" :color="item.done ? '#07c160' : '#999'" />
          </div>
          <div class="cert-info">
            <div class="cert-label">{{ item.label }}</div>
            <div class="cert-desc">{{ item.desc }}</div>
          </div>
          <div class="cert-status">
            <van-icon v-if="item.done" name="success" color="#07c160" size="20" />
            <van-button v-else size="mini" round class="cert-go-btn" @click="handleCert(item.key)">去认证</van-button>
          </div>
        </div>
      </div>

      <!-- 实名认证表单 -->
      <van-action-sheet v-model:show="showRealname" title="实名认证" close-on-popstate>
        <div class="sheet-body">
          <van-form @submit="submitRealname">
            <van-field v-model="realName" label="真实姓名" placeholder="请输入真实姓名" :rules="[{ required: true, message: '请填写姓名' }]" />
            <van-field v-model="idCard" label="身份证号" placeholder="请输入18位身份证号" maxlength="18" :rules="[{ required: true, message: '请填写身份证号' }, { validator: v => v.length === 18, message: '身份证号需18位' }]" />
            <div style="padding: 20px 16px;">
              <van-button round block class="submit-btn" native-type="submit" :loading="submitting">提交认证</van-button>
            </div>
          </van-form>
        </div>
      </van-action-sheet>

      <!-- 人脸认证 -->
      <van-action-sheet v-model:show="showFace" title="人脸认证" close-on-popstate>
        <div class="sheet-body">
          <div class="face-hint">请上传清晰的正面人脸照片</div>
          <van-uploader :after-read="handleFaceUpload" accept="image/*" :max-count="1">
            <div class="face-upload-area">
              <van-icon name="photograph" size="40" color="#667eea" />
              <div class="face-upload-text">点击上传照片</div>
            </div>
          </van-uploader>
          <div v-if="facePreview" style="margin-top:12px;">
            <van-image width="100%" height="200" fit="cover" :src="facePreview" />
          </div>
          <div v-if="facePreview" style="padding: 16px;">
            <van-button round block class="submit-btn" :loading="submitting" @click="submitFace">确认提交</van-button>
          </div>
        </div>
      </van-action-sheet>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { getCertification, submitRealname as submitRealnameApi, submitFace as submitFaceApi } from '@/utils/api'

const loading = ref(true)
const cert = reactive({ stars: 0, items: [] })
const showRealname = ref(false)
const showFace = ref(false)
const realName = ref('')
const idCard = ref('')
const facePreview = ref('')
const faceFile = ref(null)
const submitting = ref(false)

const icons = ['phone-o', 'records-o', 'photograph']

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) { showToast('请先登录'); return }
  await loadCert()
})

async function loadCert() {
  try {
    const res = await getCertification()
    const d = res.data || res
    cert.stars = d.stars
    cert.items = d.items || []
  } catch { showToast('加载失败') }
  finally { loading.value = false }
}

function handleCert(key) {
  if (key === 'realname') showRealname.value = true
  else if (key === 'face') showFace.value = true
  else showToast('手机已认证')
}

async function submitRealname() {
  submitting.value = true
  try {
    await submitRealnameApi(realName.value, idCard.value)
    showToast('实名认证成功')
    showRealname.value = false
    await loadCert()
    // 更新本地用户信息
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    user.is_verified = true
    localStorage.setItem('user', JSON.stringify(user))
  } catch (err) {
    showToast(err.response?.data?.detail || '认证失败')
  } finally { submitting.value = false }
}

function handleFaceUpload(file) {
  facePreview.value = file.content?.url || URL.createObjectURL(file.file)
  faceFile.value = file
}

async function submitFace() {
  if (!facePreview.value) return
  submitting.value = true
  try {
    await submitFaceApi(facePreview.value)
    showToast('人脸认证成功')
    showFace.value = false
    facePreview.value = ''
    await loadCert()
  } catch (err) {
    showToast(err.response?.data?.detail || '认证失败')
  } finally { submitting.value = false }
}
</script>

<style scoped>
.cert-page { padding-bottom: 20px; }
.loading-wrap { display: flex; justify-content: center; padding: 60px 0; }

.stars-card {
  background: linear-gradient(135deg, #667eea, #764ba2);
  padding: 30px 20px;
  text-align: center;
  color: #fff;
}
.stars-title { font-size: 18px; font-weight: 700; margin-bottom: 14px; }
.stars-row { display: flex; justify-content: center; gap: 8px; }
.stars-desc { font-size: 13px; opacity: 0.85; margin-top: 10px; }

.cert-list {
  background: #fff;
  margin-top: 10px;
}
.cert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid #f5f5f5;
}
.cert-item:last-child { border-bottom: none; }
.cert-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.cert-info { flex: 1; }
.cert-label { font-size: 15px; font-weight: 600; }
.cert-desc { font-size: 12px; color: #999; margin-top: 2px; }
.cert-status { flex-shrink: 0; }
.cert-go-btn {
  background: linear-gradient(135deg, #667eea, #764ba2) !important;
  color: #fff !important;
  border: none !important;
  font-size: 12px !important;
}

/* Sheets */
.sheet-body { padding: 16px; }
.submit-btn {
  background: linear-gradient(135deg, #667eea, #764ba2) !important;
  color: #fff !important;
  border: none !important;
  height: 44px !important;
}

.face-hint { font-size: 14px; color: #666; text-align: center; margin-bottom: 16px; }
.face-upload-area {
  border: 2px dashed #667eea;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
}
.face-upload-text { font-size: 14px; color: #667eea; margin-top: 8px; }
</style>
