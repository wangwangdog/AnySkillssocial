<template>
  <el-container class="layout">
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h2>SkillGate</h2>
        <span>运营后台</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据总览</span>
        </el-menu-item>
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/orders">
          <el-icon><List /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="/content">
          <el-icon><Document /></el-icon>
          <span>内容管理</span>
        </el-menu-item>
        <el-menu-item index="/risk">
          <el-icon><Warning /></el-icon>
          <span>风控管理</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h3>{{ $route.meta.title || '后台管理' }}</h3>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>管理员</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { DataAnalysis, User, List, Document, Warning, Setting } from '@element-plus/icons-vue'

const logout = () => {
  localStorage.removeItem('admin_token')
  window.location.href = '/login'
}
</script>

<style scoped>
.layout {
  height: 100vh;
}
.sidebar {
  background-color: #304156;
}
.logo {
  height: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.logo h2 {
  margin: 0;
  font-size: 20px;
}
.logo span {
  font-size: 12px;
  color: #909399;
}
.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
.header-left h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}
.header-right {
  display: flex;
  align-items: center;
}
.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}
.main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
