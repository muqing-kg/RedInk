<template>
  <div id="app">
    <!-- 背景装饰球 (Background Blobs) -->
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
    <div class="blob blob-3"></div>

    <!-- 侧边栏 Sidebar (悬浮胶囊风) -->
    <aside class="layout-sidebar glass-panel" v-if="!isAuthPage">
      <div class="logo-area">
        <div class="logo-circle">
          <img src="/logo.png" alt="沐倾" class="logo-img" />
        </div>
        <div class="logo-text">
          <span class="brand-name">RedInk</span>
          <span class="brand-slogan">✨ 你的灵感魔法 ✨</span>
        </div>
      </div>
      
      <nav class="nav-menu">
        <RouterLink to="/" class="nav-item" active-class="active">
          <div class="nav-background"></div>
          <span class="nav-icon">🎨</span>
          <span class="nav-text">创作工坊</span>
        </RouterLink>
        <RouterLink to="/history" class="nav-item" active-class="active">
          <div class="nav-background"></div>
          <span class="nav-icon">🕰️</span>
          <span class="nav-text">时光机</span>
        </RouterLink>
        <RouterLink to="/settings" class="nav-item" active-class="active">
          <div class="nav-background"></div>
          <span class="nav-icon">⚙️</span>
          <span class="nav-text">魔法设置</span>
        </RouterLink>
      </nav>
      
      <div class="sidebar-quote-card">
        <div class="quote-header">DAILY INSPIRE</div>
        <div class="quote-content">
          {{ hitokoto }}
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="layout-main" :class="{ 'auth-main': isAuthPage }">
      <!-- 顶部导航栏 (透明悬浮) -->
      <header class="layout-header" v-if="!isAuthPage">
        <!-- 面包屑/标题区 -->
        <h2 class="page-title-float">
          <span class="title-emoji" v-if="route.meta.icon">{{ route.meta.icon }}</span>
          {{ route.meta.title || '' }}
        </h2>
        
        <!-- 用户胶囊 -->
        <div class="user-capsule" @click="toggleUserMenu" :class="{ 'active': showUserMenu }">
          <div class="user-avatar-ring">
            <img class="user-avatar-img" :src="`https://api.dicebear.com/7.x/adventurer/svg?seed=${currentUser?.username || 'RedInk'}`" alt="avatar">
          </div>
          <span class="user-name-text">{{ currentUser?.username || '魔法师' }}</span>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="dropdown-arrow">
            <path d="M6 9l6 6 6-6"/>
          </svg>

          <!-- 下拉菜单 -->
          <transition name="pop">
            <div class="dropdown-bubble" v-if="showUserMenu">
              <div class="dropdown-item" @click.stop="openChangePasswordModal">
                <span class="item-icon">🔐</span> 修改密码
              </div>
              <div class="dropdown-divider"></div>
              <div class="dropdown-item logout-item" @click.stop="logout">
                <span class="item-icon">👋</span> 退出登录
              </div>
            </div>
          </transition>
        </div>
      </header>
      
      <div class="content-glass-wrapper">
        <RouterView v-slot="{ Component, route }">
          <transition name="fade-scale" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </RouterView>

        <!-- 页脚 -->
        <footer class="cute-footer" v-if="!isAuthPage">
          <span class="footer-heart">Made with 💖 by MuQing</span>
          <span class="footer-dot">·</span>
          <span class="footer-link">RedInk 2025</span>
        </footer>
      </div>
      
      <!-- 模态框 (果冻弹窗) -->
      <transition name="bounce">
        <div class="modal-overlay" v-if="showChangePasswordModal" @click.self="closeChangePasswordModal">
          <div class="jelly-modal">
            <button class="modal-close-btn" @click="closeChangePasswordModal">✕</button>
            <div class="modal-header-img">🔐</div>
            <h3>修改密码</h3>
            <p class="modal-desc">为了账号安全，给自己换个新钥匙吧~</p>
            
            <form @submit.prevent="changePassword" class="cute-form">
              <div class="cute-input-group">
                <label>旧密码</label>
                <input type="password" v-model="changePasswordForm.currentPassword" placeholder="请输入现在的密码..." />
              </div>
              <div class="cute-input-group">
                <label>新密码</label>
                <input type="password" v-model="changePasswordForm.newPassword" placeholder="想要一个什么样的新密码？" />
              </div>
              <div class="cute-input-group">
                <label>确认新密码</label>
                <input type="password" v-model="changePasswordForm.confirmPassword" placeholder="再输入一次确认哦~" />
              </div>
              
              <div v-if="passwordError" class="error-bubble">{{ passwordError }}</div>
              
              <button type="submit" class="jelly-btn" :disabled="changingPassword">
                {{ changingPassword ? '✨ 施法中...' : '💖 确认修改' }}
              </button>
            </form>
          </div>
        </div>
      </transition>
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterView, RouterLink, useRoute, useRouter } from 'vue-router'
import { onMounted, computed, ref, onMounted as onMountedVue, onUnmounted, watch } from 'vue'
import { setupAutoSave } from './stores/generator'
import { getMe } from './api/auth'

// 启用自动保存到 localStorage
const route = useRoute()
const router = useRouter()
const isAuthPage = computed(() => route.path === '/login' || route.path === '/register')

// 用户信息相关状态
const currentUser = ref<{ username: string; role: string } | null>(null)
const showUserMenu = ref(false)
const hitokoto = ref('今天也要加油鸭！')

// 获取一言
async function fetchHitokoto() {
  try {
    const res = await fetch('https://v1.hitokoto.cn/?c=i&encode=text')
    if (res.ok) {
      hitokoto.value = await res.text()
    }
  } catch (e) {
    console.error('获取一言失败', e)
  }
}

// 修改密码相关状态
const showChangePasswordModal = ref(false)
const changingPassword = ref(false)
const passwordError = ref('')
const changePasswordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 获取当前用户信息
async function fetchCurrentUser() {
  // 检查 token 是否存在
  const token = localStorage.getItem('access_token')
  if (!token) {
    // 没有 token，重定向到登录页
    currentUser.value = null
    if (!isAuthPage.value) {
      router.replace('/login')
    }
    return
  }

  try {
    const result = await getMe()
    if (result.success && result.user) {
      currentUser.value = {
        username: result.user.username,
        role: result.user.role
      }
    } else {
      // API 返回失败，token 可能无效
      throw new Error('Token 验证失败')
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    // 清除无效 token，重定向到登录页
    localStorage.removeItem('access_token')
    currentUser.value = null
    if (!isAuthPage.value) {
      router.replace('/login')
    }
  }
}

// 切换用户菜单
function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
}

// 关闭用户菜单
function closeUserMenu() {
  showUserMenu.value = false
}

// 打开修改密码模态框
function openChangePasswordModal() {
  showChangePasswordModal.value = true
  closeUserMenu()
  changePasswordForm.value = { currentPassword: '', newPassword: '', confirmPassword: '' }
  passwordError.value = ''
}

// 关闭修改密码模态框
function closeChangePasswordModal() {
  showChangePasswordModal.value = false
}

// 修改密码（保持原有逻辑不变）
async function changePassword() {
  if (!changePasswordForm.value.currentPassword) { passwordError.value = '请输入当前密码'; return }
  if (!changePasswordForm.value.newPassword) { passwordError.value = '请输入新密码'; return }
  if (changePasswordForm.value.newPassword.length < 6) { passwordError.value = '新密码长度不能少于6个字符'; return }
  if (changePasswordForm.value.newPassword !== changePasswordForm.value.confirmPassword) { passwordError.value = '两次输入的新密码不一致'; return }
  
  passwordError.value = ''
  changingPassword.value = true
  
  try {
    const response = await fetch('/api/auth/change-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(changePasswordForm.value)
    })
    
    const data = await response.json()
    if (data.success) {
      closeChangePasswordModal()
      alert('密码修改成功啦！请重新登录哦~')
      logout()
    } else {
      passwordError.value = data.error || '密码修改失败'
    }
  } catch (error) {
    passwordError.value = '网络错误，密码修改失败'
    console.error('修改密码失败:', error)
  } finally {
    changingPassword.value = false
  }
}

// 退出登录
function logout() {
  localStorage.removeItem('access_token')
  currentUser.value = null
  closeUserMenu()
  router.replace('/login')
}

// 点击外部关闭菜单
function handleClickOutside(event: MouseEvent) {
  const userMenu = document.querySelector('.user-menu')
  if (userMenu && !userMenu.contains(event.target as Node)) {
    closeUserMenu()
  }
}

onMountedVue(async () => {
  setupAutoSave()
  fetchHitokoto()
  if (!isAuthPage.value) await fetchCurrentUser()
  document.addEventListener('click', handleClickOutside)
})

watch(() => route.path, async () => {
  if (!isAuthPage.value) await fetchCurrentUser()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* ==================== 背景装饰 (Blobs) ==================== */
.blob {
  position: fixed;
  border-radius: 50%;
  filter: blur(80px);
  z-index: -1;
  opacity: 0.6;
  animation: float 20s infinite ease-in-out;
}
.blob-1 {
  width: 400px;
  height: 400px;
  background: #FFD6E0;
  top: -100px;
  left: -50px;
}
.blob-2 {
  width: 300px;
  height: 300px;
  background: #C4FAF8;
  bottom: 0px;
  right: -50px;
  animation-delay: -5s;
}
.blob-3 {
  width: 250px;
  height: 250px;
  background: #E7C6FF;
  top: 40%;
  left: 30%;
  opacity: 0.4;
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(30px, -50px) rotate(10deg); }
  66% { transform: translate(-20px, 20px) rotate(-5deg); }
}

/* ==================== 侧边栏 ==================== */
.layout-sidebar {
  width: 260px;
  position: fixed;
  left: 20px; /* 悬浮留白 */
  top: 20px;
  height: calc(100vh - 40px);
  z-index: 100;
  display: flex;
  flex-direction: column;
  padding: 30px 20px;
  /* 玻璃效果在base.css .glass-panel 或类似类中定义，这里如果没引base.css可以直接写 */
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 2px solid rgba(255, 255, 255, 0.8);
  border-radius: 30px;
  box-shadow: 0 10px 30px rgba(159, 134, 192, 0.1);
  transition: all 0.3s ease;
}

.layout-sidebar:hover {
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 15px 35px rgba(255, 133, 161, 0.15);
}

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin-bottom: 40px;
}

.logo-circle {
  width: 80px;
  height: 80px;
  background: white;
  border-radius: 50%;
  padding: 5px;
  box-shadow: 0 8px 20px rgba(255, 133, 161, 0.2);
  transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.logo-circle:hover { transform: rotate(10deg) scale(1.05); }

.logo-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }

.logo-text { text-align: center; }
.brand-name {
  display: block;
  font-family: 'Quicksand', sans-serif;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(45deg, #FF85A1, #9F86C0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.brand-slogan { font-size: 12px; color: #8D84A3; margin-top: 4px; display: block; }

/* 导航药丸 */
.nav-menu { display: flex; flex-direction: column; gap: 12px; flex: 1; }

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 14px 20px;
  color: #6C6377;
  text-decoration: none;
  font-weight: 600;
  border-radius: 20px;
  transition: all 0.3s;
  overflow: hidden;
}

.nav-background {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(90deg, #FF9A9E 0%, #FECFEF 100%);
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 0;
  border-radius: 20px;
}

.nav-icon, .nav-text { z-index: 1; position: relative; transition: transform 0.3s; }
.nav-icon { font-size: 20px; }

.nav-item:hover { color: #FF85A1; background: rgba(255, 255, 255, 0.6); }
.nav-item:hover .nav-icon { transform: scale(1.2); }

.nav-item.active { color: white; box-shadow: 0 8px 20px rgba(255, 154, 158, 0.4); }
.nav-item.active .nav-background { opacity: 1; }
.nav-item.active .nav-icon { transform: scale(1.2) rotate(-10deg); }

/* 侧边栏每日一句卡片 */
.sidebar-quote-card {
  margin-top: 20px;
  background: transparent;
  padding: 20px 16px;
  position: relative;
  overflow: hidden;
  text-align: center;
}

.sidebar-quote-card::before {
  content: '✨';
  position: absolute;
  top: 8px;
  left: 12px;
  font-size: 16px;
  opacity: 0.6;
  animation: sparkle 2s ease-in-out infinite;
}

.sidebar-quote-card::after {
  content: '💫';
  position: absolute;
  bottom: 8px;
  right: 12px;
  font-size: 14px;
  opacity: 0.5;
  animation: sparkle 2s ease-in-out infinite 1s;
}

@keyframes sparkle {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

.quote-header {
  font-size: 11px;
  letter-spacing: 3px;
  background: linear-gradient(90deg, #FF69B4, #BA55D3, #9370DB);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
  margin-bottom: 12px;
  text-transform: uppercase;
}

.quote-content {
  font-size: 13px;
  line-height: 1.8;
  background: linear-gradient(135deg, #FF6B9D 0%, #C44569 50%, #8B5CF6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-weight: 600;
  padding: 0 8px;
}

/* ==================== 布局 & 头部 ==================== */
.layout-main {
  margin-left: 300px; /* 侧边栏宽260 + 左边距20 + 间隙20 */
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.layout-main.auth-main { margin-left: 0; padding: 0; }

.layout-header {
  height: 70px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}

.title-emoji { font-size: 24px; margin-right: 8px; }
.page-title-float {
  font-size: 20px;
  font-weight: 700;
  color: #4A4063;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.4);
  padding: 8px 16px;
  border-radius: 20px;
  backdrop-filter: blur(5px);
}

/* 用户胶囊 */
.user-capsule {
  position: relative;
  display: flex;
  align-items: center;
  background: white;
  padding: 6px 16px 6px 6px;
  border-radius: 30px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(159, 134, 192, 0.1);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  border: 2px solid white;
}
.user-capsule:hover, .user-capsule.active {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 133, 161, 0.25);
}

.user-avatar-ring {
  width: 36px; height: 36px;
  border-radius: 50%;
  border: 2px solid #FFD6E0;
  padding: 2px;
  margin-right: 8px;
}
.user-avatar-img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
.user-name-text { font-size: 14px; font-weight: 700; color: #4A4063; margin-right: 8px; }
.dropdown-arrow { color: #FF85A1; transition: transform 0.3s; }
.user-capsule.active .dropdown-arrow { transform: rotate(180deg); }

/* 下拉气泡 */
.dropdown-bubble {
  position: absolute;
  top: 120%; right: 0;
  width: 180px;
  background: white;
  border-radius: 20px;
  padding: 10px;
  box-shadow: 0 10px 40px rgba(159, 134, 192, 0.15);
  border: 2px solid #FFF0F5;
  z-index: 100;
}
.dropdown-bubble::before {
  content: '';
  position: absolute;
  top: -8px; right: 20px;
  width: 16px; height: 16px;
  background: white;
  transform: rotate(45deg);
  border-top: 2px solid #FFF0F5;
  border-left: 2px solid #FFF0F5;
}

.dropdown-item {
  padding: 12px;
  border-radius: 12px;
  color: #6C6377;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
.dropdown-item:hover { background: #FFF0F5; color: #FF85A1; }
.logout-item:hover { background: #FFE5E5; color: #FF5C5C; }
.dropdown-divider { height: 1px; background: #eee; margin: 4px 10px; }

/* 内容容器 */
.content-glass-wrapper { flex: 1; display: flex; flex-direction: column; }

/* 页脚 */
.cute-footer {
  margin-top: auto;
  padding-top: 40px;
  text-align: center;
  font-size: 12px;
  color: #8D84A3;
  opacity: 0.8;
}
.footer-heart { font-weight: 600; }
.footer-dot { margin: 0 8px; color: #FF85A1; }

/* ==================== 模态框 (果冻弹窗) ==================== */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(74, 64, 99, 0.4);
  backdrop-filter: blur(8px);
  z-index: 2000;
  display: flex; align-items: center; justify-content: center;
}

.jelly-modal {
  background: white;
  width: 380px;
  padding: 40px 30px;
  border-radius: 40px;
  text-align: center;
  position: relative;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  border: 4px solid #FFF0F5;
}

.modal-close-btn {
  position: absolute; top: 20px; right: 20px;
  background: #F0F0F0; border: none;
  width: 32px; height: 32px; border-radius: 50%;
  color: #8D84A3; font-weight: bold;
}
.modal-close-btn:hover { background: #FF85A1; color: white; transform: rotate(90deg); }

.modal-header-img { font-size: 50px; margin-bottom: 20px; animation: bounce 2s infinite; }
.jelly-modal h3 { font-size: 24px; color: #4A4063; margin-bottom: 8px; }
.modal-desc { color: #8D84A3; font-size: 14px; margin-bottom: 30px; }

.cute-form { display: flex; flex-direction: column; gap: 15px; }

.cute-input-group { text-align: left; }
.cute-input-group label { display: block; font-size: 12px; font-weight: 700; color: #FF85A1; margin-bottom: 5px; margin-left: 10px; }
.cute-input-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #F0F0F0;
  border-radius: 16px;
  font-family: inherit;
  color: #4A4063;
  transition: all 0.3s;
  background: #FAFAFA;
}
.cute-input-group input:focus {
  border-color: #FF85A1;
  background: white;
  box-shadow: 0 0 0 4px rgba(255, 133, 161, 0.1);
  outline: none;
}

.error-bubble {
  background: #FFE5E5; color: #FF5C5C;
  padding: 8px 12px; border-radius: 12px; font-size: 12px;
  margin-top: 5px;
}

.jelly-btn {
  background: linear-gradient(45deg, #FF85A1, #FF5C8D);
  color: white; border: none;
  padding: 14px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 16px;
  margin-top: 10px;
  box-shadow: 0 8px 20px rgba(255, 92, 141, 0.3);
}
.jelly-btn:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 12px 25px rgba(255, 92, 141, 0.4); }
.jelly-btn:active { transform: scale(0.95); }

/* ==================== 动画 ==================== */
@keyframes bounce { 
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 路由切换 fade-scale */
.fade-scale-enter-active, .fade-scale-leave-active { transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); }
.fade-scale-enter-from { opacity: 0; transform: scale(0.95) translateY(20px); }
.fade-scale-leave-to { opacity: 0; transform: scale(1.05); }

/* 下拉菜单 pop */
.pop-enter-active, .pop-leave-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.pop-enter-from, .pop-leave-to { opacity: 0; transform: scale(0.8) translateY(-10px); }

/* 模态框 bounce */
.bounce-enter-active { animation: elastic-in 0.5s; }
.bounce-leave-active { transition: opacity 0.3s; opacity: 0; }

@keyframes elastic-in {
  0% { transform: scale(0.8); opacity: 0; }
  50% { transform: scale(1.05); opacity: 1; }
  70% { transform: scale(0.95); }
  100% { transform: scale(1); }
}
</style>
