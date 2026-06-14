<template>
  <div class="page">
    <van-nav-bar title="注册" left-arrow @click-left="$router.back()" />
    <div class="form-wrapper">
      <van-form @submit="handleRegister">
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
          v-model="nickname"
          name="nickname"
          label="昵称"
          placeholder="请输入昵称"
          :rules="[
            { required: true, message: '请输入昵称' },
            { max: 20, message: '昵称最长20个字符' }
          ]"
        />
        <van-field
          v-model="password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码（至少6位）"
          :rules="[
            { required: true, message: '请输入密码' },
            { pattern: /^.{6,}$/, message: '密码至少6位' }
          ]"
        />
        <van-field
          v-model="confirmPassword"
          type="password"
          name="confirmPassword"
          label="确认密码"
          placeholder="请再次输入密码"
          :rules="[
            { required: true, message: '请确认密码' },
            { validator: (val) => val === password.value, message: '两次密码不一致' }
          ]"
        />
        <div style="margin: 16px">
          <van-button round block type="primary" native-type="submit" :loading="loading">
            注册
          </van-button>
        </div>
      </van-form>
      <div class="link-row">
        <span @click="$router.push('/login')">已有账号？去登录</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { register } from '@/utils/api'

const router = useRouter()
const phone = ref('')
const nickname = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)

async function handleRegister() {
  loading.value = true
  showLoadingToast({ message: '注册中...', forbidClick: true })
  try {
    const res = await register(phone.value, nickname.value, password.value)
    const { token, user } = res.data || res
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    showToast('注册成功')
    router.push('/')
  } catch (err) {
    const msg = err.response?.data?.message || err.response?.data?.detail || err.message || '注册失败'
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
