<template>
  <div class="page">
    <van-nav-bar title="登录" />
    <div class="form-wrapper">
      <van-form @submit="handleLogin">
        <van-field
          v-model="phone"
          name="phone"
          label="手机号"
          placeholder="请输入手机号"
          maxlength="11"
          :rules="[
            { required: true, message: '请输入手机号' },
            { pattern: /^1\d{10}$/, message: '手机号格式不正确' }
          ]"
        />
        <van-field
          v-model="password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请输入密码' }]"
        />
        <div style="margin: 16px">
          <van-button round block type="primary" native-type="submit" :loading="loading">
            登录
          </van-button>
        </div>
      </van-form>
      <div class="link-row">
        <span @click="$router.push('/register')">还没有账号？去注册</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { login } from '@/utils/api'

const router = useRouter()
const phone = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  showLoadingToast({ message: '登录中...', forbidClick: true })
  try {
    const res = await login(phone.value, password.value)
    const { token, user } = res.data || res
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    showToast('登录成功')
    router.push('/')
  } catch (err) {
    const msg = err.response?.data?.message || err.message || '登录失败'
    showToast(msg)
  } finally {
    closeToast()
    loading.value = false
  }
}
</script>

<style scoped>
.form-wrapper {
  margin-top: 40px;
}
.link-row {
  text-align: center;
  font-size: 14px;
  color: var(--primary);
}
.link-row span {
  cursor: pointer;
}
</style>
