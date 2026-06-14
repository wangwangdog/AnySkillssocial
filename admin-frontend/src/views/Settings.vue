<template>
  <div class="settings-page">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="系统设置" name="system">
        <el-form :model="systemConfig" label-width="120px">
          <el-form-item label="平台名称">
            <el-input v-model="systemConfig.name" />
          </el-form-item>
          <el-form-item label="平台 Logo">
            <el-upload action="/api/admin/upload/logo">
              <el-button type="primary">上传</el-button>
            </el-upload>
          </el-form-item>
          <el-form-item label="维护模式">
            <el-switch v-model="systemConfig.maintenance" />
          </el-form-item>
          <el-button type="primary" @click="saveSystem">保存</el-button>
        </el-form>
      </el-tab-pane>
      
      <el-tab-pane label="支付配置" name="payment">
        <el-form :model="paymentConfig" label-width="120px">
          <el-form-item label="微信支付密钥">
            <el-input v-model="paymentConfig.wxpay_key" type="password" />
          </el-form-item>
          <el-form-item label="提现手续费率">
            <el-input-number v-model="paymentConfig.withdraw_fee_rate" :precision="2" />
          </el-form-item>
          <el-form-item label="最低提现金额">
            <el-input-number v-model="paymentConfig.min_withdraw" :min="0" />
          </el-form-item>
          <el-button type="primary" @click="savePayment">保存</el-button>
        </el-form>
      </el-tab-pane>
      
      <el-tab-pane label="存储配置" name="storage">
        <el-form :model="storageConfig" label-width="120px">
          <el-form-item label="存储模式">
            <el-select v-model="storageConfig.mode">
              <el-option label="本地" value="local" />
              <el-option label="阿里云 OSS" value="oss" />
            </el-select>
          </el-form-item>
          <el-form-item v-if="storageConfig.mode === 'oss'" label="OSS Endpoint">
            <el-input v-model="storageConfig.oss_endpoint" />
          </el-form-item>
          <el-form-item v-if="storageConfig.mode === 'oss'" label="Access Key ID">
            <el-input v-model="storageConfig.oss_access_key_id" />
          </el-form-item>
          <el-button type="primary" @click="saveStorage">保存</el-button>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const activeTab = ref('system')

const systemConfig = reactive({
  name: 'SkillGate',
  maintenance: false
})

const paymentConfig = reactive({
  wxpay_key: '',
  withdraw_fee_rate: 0.1,
  min_withdraw: 100
})

const storageConfig = reactive({
  mode: 'local',
  oss_endpoint: '',
  oss_access_key_id: ''
})

const saveSystem = () => console.log('保存系统设置', systemConfig)
const savePayment = () => console.log('保存支付配置', paymentConfig)
const saveStorage = () => console.log('保存存储配置', storageConfig)
</script>

<style scoped>
</style>
