import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/Home.vue') },
  { path: '/square', name: 'square', component: () => import('../views/Square.vue') },
  { path: '/bounty', name: 'bounty', component: () => import('../views/BountyHall.vue') },
  { path: '/login', name: 'login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'register', component: () => import('../views/Register.vue') },
  { path: '/demands', name: 'demands', component: () => import('../views/DemandList.vue') },
  { path: '/demands/create', name: 'create-demand', component: () => import('../views/DemandCreate.vue') },
  { path: '/demands/:id', name: 'demand-detail', component: () => import('../views/DemandDetail.vue') },
  { path: '/services', name: 'services', component: () => import('../views/ServiceList.vue') },
  { path: '/services/create', name: 'create-service', component: () => import('../views/ServiceCreate.vue') },
  { path: '/services/:id', name: 'service-detail', component: () => import('../views/ServiceDetail.vue') },
  { path: '/services/:id/pay', name: 'service-pay', component: () => import('../views/ServicePay.vue') },
  { path: '/services/:id/progress', name: 'service-progress', component: () => import('../views/ServiceProgress.vue') },
  { path: '/orders', name: 'orders', component: () => import('../views/OrderList.vue') },
  { path: '/orders/:id', name: 'order-detail', component: () => import('../views/OrderDetail.vue') },
  { path: '/profile', name: 'profile', component: () => import('../views/Profile.vue') },
  { path: '/certification', name: 'certification', component: () => import('../views/Certification.vue') },
  { path: '/users/:id', name: 'user-profile', component: () => import('../views/UserProfile.vue') },
  { path: '/messages', name: 'messages', component: () => import('../views/MessageList.vue') },
  { path: '/chat/:id', name: 'chat', component: () => import('../views/ChatView.vue') },
  { path: '/notifications', name: 'notifications', component: () => import('../views/NotificationView.vue') },
]

export default createRouter({ history: createWebHistory('/skillgate/c2c/'), routes })
