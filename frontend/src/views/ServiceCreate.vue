<template>
  <div class="page">
    <van-nav-bar title="发布服务" left-arrow @click-left="$router.back()" />

    <van-form @submit="handleSubmit">
      <van-field
        v-model="form.title"
        name="title"
        label="服务名称"
        placeholder="例：周末陪玩、个人瑜伽私教"
        :rules="[{ required: true, message: '请输入服务名称' }]"
      />

      <van-field
        v-model="form.description"
        name="description"
        label="服务描述"
        type="textarea"
        placeholder="请详细描述你的服务内容、优势..."
        rows="4"
        maxlength="500"
        show-word-limit
        :rules="[{ required: true, message: '请输入服务描述' }]"
      />

      <van-cell title="技能分类" is-link @click="showPicker = true">
        <template #value>
          <span :class="{ 'placeholder': !form.skill_type }">
            {{ form.skill_type || '请选择' }}
          </span>
        </template>
      </van-cell>

      <van-field
        v-model="form.price"
        name="price"
        label="价格 (¥)"
        type="number"
        placeholder="请输入价格"
        :rules="[
          { required: true, message: '请输入价格' },
          { validator: (v) => Number(v) > 0, message: '价格必须大于0' }
        ]"
      >
        <template #button>
          <span style="font-size:12px;color:#999">元/次</span>
        </template>
      </van-field>

      <van-field
        v-model="form.location"
        name="location"
        label="服务地区"
        placeholder="例：福田区、南山区"
      />

      <van-field
        v-model="form.duration"
        name="duration"
        label="服务时长"
        placeholder="例：2小时、全天"
      />

      <div style="margin: 24px 16px">
        <van-button round block type="primary" native-type="submit" :loading="submitting">
          发布服务
        </van-button>
      </div>
    </van-form>

    <!-- Skill type picker -->
    <van-action-sheet v-model:show="showPicker" title="选择技能分类">
      <van-picker
        :columns="skillTypes"
        @confirm="onSkillConfirm"
        @cancel="showPicker = false"
      />
    </van-action-sheet>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { createService } from '@/utils/api'

const router = useRouter()
const showPicker = ref(false)
const submitting = ref(false)

const form = reactive({
  title: '',
  description: '',
  skill_type: '',
  price: '',
  location: '',
  duration: '',
})

const skillTypes = [
  '按摩', '理疗', '跳舞', '唱歌', '健身',
  '摄影', '化妆', '烹饪', '陪玩', '其他'
]

function onSkillConfirm({ selectedValues }) {
  form.skill_type = selectedValues[0]
  showPicker.value = false
}

async function handleSubmit() {
  submitting.value = true
  showLoadingToast({ message: '发布中...', forbidClick: true })
  try {
    const payload = {
      title: form.title,
      description: form.description,
      skill_type: form.skill_type,
      price: Number(form.price),
      location: form.location,
      city: form.location,
      duration: form.duration,
    }
    await createService(payload)
    showToast('发布成功')
    router.push('/services')
  } catch (err) {
    const msg = err.response?.data?.message || err.message || '发布失败'
    showToast(msg)
  } finally {
    closeToast()
    submitting.value = false
  }
}
</script>

<style scoped>
.placeholder { color: #c8c9cc; }
</style>
