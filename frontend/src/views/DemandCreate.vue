<template>
  <div class="page">
    <van-nav-bar title="发布需求" left-arrow @click-left="$router.back()" />

    <van-form @submit="handleSubmit">
      <van-field
        v-model="form.title"
        name="title"
        label="标题"
        placeholder="简述你的需求"
        :rules="[{ required: true, message: '请输入需求标题' }]"
      />

      <van-field
        v-model="form.description"
        name="description"
        label="详细描述"
        type="textarea"
        placeholder="请详细描述你的需求..."
        rows="4"
        maxlength="500"
        show-word-limit
        :rules="[{ required: true, message: '请输入需求描述' }]"
      />

      <van-cell title="技能分类" is-link @click="showPicker = true">
        <template #value>
          <span :class="{ 'placeholder': !form.skill_type }">
            {{ form.skill_type || '请选择' }}
          </span>
        </template>
      </van-cell>

      <van-field
        v-model="form.budget"
        name="budget"
        label="预算 (¥)"
        type="number"
        placeholder="请输入预算金额"
        :rules="[
          { required: true, message: '请输入预算' },
          { validator: (v) => Number(v) > 0, message: '预算必须大于0' }
        ]"
      >
        <template #extra>
          <span style="font-size:12px;color:#999">元</span>
        </template>
      </van-field>

      <van-cell title="面试奖励" center>
        <template #right-icon>
          <van-switch v-model="form.interview_bonus" size="24" />
        </template>
        <template #label>
          <span style="font-size:12px;color:#999">开启后报名者可获得面试奖励积分</span>
        </template>
      </van-cell>

      <div style="margin: 24px 16px">
        <van-button round block type="primary" native-type="submit" :loading="submitting">
          发布需求
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
import { createDemand } from '@/utils/api'

const router = useRouter()
const showPicker = ref(false)
const submitting = ref(false)

const form = reactive({
  title: '',
  description: '',
  skill_type: '',
  budget: '',
  interview_bonus: false
})

const skillTypes = [
  '按摩',
  '理疗',
  '跳舞',
  '唱歌',
  '健身',
  '摄影',
  '化妆',
  '烹饪',
  '陪玩',
  '其他'
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
      budget: Number(form.budget),
      interview_bonus: form.interview_bonus
    }
    await createDemand(payload)
    showToast('发布成功')
    router.push('/demands')
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
.placeholder {
  color: #c8c9cc;
}
</style>
