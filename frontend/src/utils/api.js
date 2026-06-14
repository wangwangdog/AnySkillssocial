import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 15000 })

// 拦截器 - 自动带 token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.hash = '#/login'
    }
    return Promise.reject(err)
  }
)

export default api

// ====== Auth ======
export function login(phone, password) { return api.post('/auth/login', { phone, password }) }
export function register(phone, nickname, password) { return api.post('/auth/register', { phone, nickname, password }) }
export function getMe() { return api.get('/auth/me') }
export function getCertification() { return api.get('/auth/certification') }
export function submitRealname(realName, idCard) { return api.post('/auth/cert/realname', { real_name: realName, id_card: idCard }) }
export function submitFace(photoUrl) { return api.post('/auth/cert/face', { photo_url: photoUrl }) }

// ====== Demands ======
export function listDemands(params) { return api.get('/demands', { params }) }
export function getDemand(id) { return api.get(`/demands/${id}`) }
export function createDemand(data) { return api.post('/demands', data) }
export function applyDemand(id, data) { return api.post(`/demands/${id}/apply`, data) }
export function listApplications(id) { return api.get(`/demands/${id}/applications`) }
export function acceptApplication(demandId, appId) { return api.post(`/demands/${demandId}/applications/${appId}/accept`) }
export function rejectApplication(demandId, appId) { return api.post(`/demands/${demandId}/applications/${appId}/reject`) }

// ====== Services ======
export function listServices(params) { return api.get('/services', { params }) }
export function getService(id) { return api.get(`/services/${id}`) }
export function createService(data) { return api.post('/services', data) }

// ====== Orders ======
export function listOrders() { return api.get('/orders') }
export function getOrder(id) { return api.get(`/orders/${id}`) }
export function createOrder(data) { return api.post('/orders', data) }
export function checkinOrder(id, data) { return api.post(`/orders/${id}/checkin`, data) }
export function checkoutOrder(id, data) { return api.post(`/orders/${id}/checkout`, data) }
export function rateOrder(id, score, comment) { return api.post(`/orders/${id}/rate?score=${score}&comment=${encodeURIComponent(comment)}`) }
export function getOrderRating(id) { return api.get(`/orders/${id}/rating`) }

// ====== Checkin ======
export function doCheckin() { return api.post('/checkin') }
export function getCheckinStatus() { return api.get('/checkin/status') }

// ====== Follow ======
export function getFollowedUsers() { return api.get('/users/me/following') }
export function getUserProfile(id) { return api.get(`/users/${id}`) }
export function getUserServices(id, params) { return api.get(`/users/${id}/services`, { params }) }
export function getUserDemands(id, params) { return api.get(`/users/${id}/demands`, { params }) }
export function getUserPosts(id, params) { return api.get(`/users/${id}/posts`, { params }) }
export function createPost(data) { return api.post('/users/posts', data) }

// ====== Follow ======
export function followUser(userId) { return api.post(`/users/${userId}/follow`) }
export function unfollowUser(userId) { return api.post(`/users/${userId}/unfollow`) }
export function checkFollow(userId) { return api.get(`/users/${userId}/follow/check`) }

// ====== Contact ======
export function getContactInfo(userId) { return api.get(`/users/${userId}/contact`) }
export function unlockContact(userId) { return api.post(`/users/${userId}/contact/unlock`) }

// ====== Favorites ======
export function toggleFavorite(itemType, itemId) { return api.post(`/favorites?item_type=${itemType}&item_id=${itemId}`) }
export function getFavorites(itemType) { return api.get('/favorites', { params: { item_type: itemType } }) }
export function checkFavorite(itemType, itemId) { return api.get('/favorites/check', { params: { item_type: itemType, item_id: itemId } }) }

// ====== Messages ======
export function sendMessage(recipientId, content) { return api.post('/messages/send', { recipient_id: recipientId, content }) }
export function getConversations() { return api.get('/messages/conversations') }
export function getMessages(convId) { return api.get(`/messages/${convId}`) }

// ====== Community ======
export function getFeed(params) { return api.get('/community/feed', { params }) }
export function getCommunityPosts(params) { return api.get('/community/posts', { params }) }

// ====== Recommend ======
export function getRecommendProviders() { return api.get('/recommend/providers') }

// ====== Payment ======
export function recharge(amount) { return api.post('/payment/recharge', { amount }) }

// ====== Notifications ======
export function getNotifications() { return api.get('/notifications') }
export function markNotificationRead(id) { return api.post(`/notifications/${id}/read`) }
export function markAllNotificationsRead() { return api.post('/notifications/read-all') }
export function getUnreadCount() { return api.get('/notifications/unread-count') }
