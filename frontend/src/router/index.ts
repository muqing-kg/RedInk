import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import OutlineView from '../views/OutlineView.vue'
import GenerateView from '../views/GenerateView.vue'
import ResultView from '../views/ResultView.vue'
import HistoryView from '../views/HistoryView.vue'
import SettingsView from '../views/SettingsView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/outline',
      name: 'outline',
      component: OutlineView
    },
    {
      path: '/generate',
      name: 'generate',
      component: GenerateView
    },
    {
      path: '/result',
      name: 'result',
      component: ResultView
    },
    {
      path: '/history',
      name: 'history',
      component: HistoryView
    },
    {
      path: '/history/:id',
      name: 'history-detail',
      component: HistoryView
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView
    }
    ,{
      path: '/login',
      name: 'login',
      component: LoginView
    }
    ,{
      path: '/register',
      name: 'register',
      component: RegisterView
    }
  ]
})

// 路由守卫：未登录用户自动跳转到登录页
const publicPaths = new Set(['/login', '/register'])
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (!token && !publicPaths.has(to.path)) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

// 路由守卫：页面切换时重置状态
import { useGeneratorStore } from '../stores/generator'
router.afterEach((to, from) => {
  // 当从生成相关页面切换到其他页面时，重置store状态
  if ((from.path === '/generate' || from.path === '/result' || from.path === '/outline') && 
      (to.path === '/' || to.path === '/history' || to.path === '/settings')) {
    const store = useGeneratorStore()
    // 重置所有与生成相关的状态，确保页面切换后状态干净
    store.stage = 'input' // 重置为初始状态
    store.progress = {
      current: 0,
      total: 0,
      status: 'idle'
    }
    store.images = []
    store.taskId = null
    // 保留用户编辑的核心内容
    // store.topic 和 store.outline 保持不变，以便用户可以继续编辑
    // store.recordId 保持不变，以便用户可以继续编辑历史记录
  }
  
  // 当从非生成页面进入生成相关页面时，确保状态正确
  if ((to.path === '/generate' || to.path === '/result' || to.path === '/outline') && 
      (from.path === '/' || from.path === '/history' || from.path === '/settings')) {
    const store = useGeneratorStore()
    // 如果outline为空，确保有默认值
    if (!store.outline.pages || store.outline.pages.length === 0) {
      store.outline = {
        raw: '',
        pages: []
      }
    }
  }
})

export default router
