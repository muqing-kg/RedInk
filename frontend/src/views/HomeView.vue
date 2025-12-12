<template>
  <div class="container home-container">
    <!-- 图片网格轮播背景 -->
    <ShowcaseBackground />

    <!-- Hero Area -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="brand-pill">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
          AI 驱动的小红书创作助手
        </div>
        <div class="platform-slogan">
          让传播不再需要门槛，让创作从未如此简单
        </div>
        <h1 class="page-title">灵感一触即发</h1>
        <p class="page-subtitle">输入你的创意主题，让 AI 帮你生成爆款标题、正文和封面图</p>
      </div>

      <!-- 主题输入组合框 -->
      <ComposerInput
        ref="composerRef"
        v-model="topic"
        :loading="loading"
        @generate="handleGenerate"
        @imagesChange="handleImagesChange"
      />
    </div>



    <!-- 错误提示 -->
    <div v-if="error" class="error-toast">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
      {{ error }}
    </div>

    <!-- 魔法生成加载遮罩 -->
    <transition name="fade">
      <div v-if="loading" class="magic-loading-overlay">
        <div class="magic-content">
          <div class="magic-icon-wrapper">
            <span class="magic-icon">✨</span>
            <div class="magic-ring"></div>
            <div class="magic-ring-2"></div>
          </div>
          <h3 class="magic-title">正在施展灵感魔法...</h3>
          <p class="magic-subtitle">AI 正在分析全网爆款趋势，为你定制专属大纲</p>
          
          <div class="loading-steps">
            <div class="step-item active">
              <span class="step-dot"></span>
              <span>解析创意主题</span>
            </div>
            <div class="step-item active" style="animation-delay: 0.5s">
              <span class="step-dot"></span>
              <span>构思爆款标题</span>
            </div>
            <div class="step-item active" style="animation-delay: 1s">
              <span class="step-dot"></span>
              <span>规划内容结构</span>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGeneratorStore } from '../stores/generator'
import { generateOutline } from '../api'

// 引入组件
import ShowcaseBackground from '../components/home/ShowcaseBackground.vue'
import ComposerInput from '../components/home/ComposerInput.vue'

const router = useRouter()
const store = useGeneratorStore()

// 状态
const topic = ref('')
const loading = ref(false)
const error = ref('')
const composerRef = ref<InstanceType<typeof ComposerInput> | null>(null)

// 组件加载时重置状态，确保页面显示正常
onMounted(() => {
  // 重置生成相关的状态，保留核心编辑内容
  if (store.stage !== 'input') {
    store.stage = 'input'
    store.progress = {
      current: 0,
      total: 0,
      status: 'idle'
    }
    store.images = []
    store.taskId = null
    // 保留用户编辑的topic和outline，以便用户可以继续编辑
    // 注意：topic是本地ref，不会受store影响
  }
})

// 上传的图片文件
const uploadedImageFiles = ref<File[]>([])

/**
 * 处理图片变化
 */
function handleImagesChange(images: File[]) {
  uploadedImageFiles.value = images
}

/**
 * 生成大纲
 */
async function handleGenerate() {
  if (!topic.value.trim()) return

  loading.value = true
  error.value = ''

  try {
    const imageFiles = uploadedImageFiles.value

    const result = await generateOutline(
      topic.value.trim(),
      imageFiles.length > 0 ? imageFiles : undefined
    )

    if (result.success && result.pages) {
      store.reset()
      store.setTopic(topic.value.trim())
      store.setOutline(result.outline || '', result.pages)
      store.recordId = null

      // 保存用户上传的图片到 store
      if (imageFiles.length > 0) {
        store.userImages = imageFiles
      } else {
        store.userImages = []
      }

      // 清理 ComposerInput 的预览
      composerRef.value?.clearPreviews()
      uploadedImageFiles.value = []

      router.push('/outline')
    } else {
      error.value = result.error || '生成大纲失败'
    }
  } catch (err: any) {
    error.value = err.message || '网络错误，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.home-container {
  max-width: 1100px;
  padding-top: 10px;
  position: relative;
  z-index: 1;
}

/* Hero Section - 少女风格 */
.hero-section {
  text-align: center;
  margin-bottom: 20px;
  padding: 30px 40px;
  animation: fadeIn 0.6s ease-out;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 240, 245, 0.95) 100%);
  border-radius: 32px;
  box-shadow: 0 20px 60px rgba(255, 133, 161, 0.15);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.hero-content {
  margin-bottom: 36px;
}

/* 品牌标签 - 渐变粉紫色 */
.brand-pill {
  display: inline-flex;
  align-items: center;
  padding: 8px 20px;
  background: linear-gradient(135deg, #FFE0EC 0%, #F0E6FF 100%);
  color: #C44569;
  border-radius: 100px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 20px;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 15px rgba(255, 133, 161, 0.2);
}

/* 平台标语 */
.platform-slogan {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #6C6377 0%, #8B7B9B 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 24px;
  line-height: 1.6;
  letter-spacing: 0.5px;
}

/* 页面标题 - 渐变色 */
.page-title {
  font-size: 2.8rem;
  font-weight: 800;
  background: linear-gradient(135deg, #FF6B9D 0%, #C44569 40%, #8B5CF6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 16px;
  color: #8B7B9B;
  margin-top: 12px;
}

/* Page Footer */
.page-footer {
  text-align: center;
  padding: 24px 0 16px;
  margin-top: 20px;
}

.footer-copyright {
  font-size: 15px;
  color: #6C6377;
  font-weight: 500;
  margin-bottom: 6px;
}

.footer-copyright a {
  color: #FF6B9D;
  text-decoration: none;
  font-weight: 600;
}

.footer-copyright a:hover {
  text-decoration: underline;
}

.footer-license {
  font-size: 13px;
  color: #A99BB5;
}

.footer-license a {
  color: #8B7B9B;
  text-decoration: none;
}

.footer-license a:hover {
  color: #FF6B9D;
}

/* Error Toast - 柔和的粉红色 */
.error-toast {
  position: fixed;
  bottom: 32px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #FF6B9D 0%, #C44569 100%);
  color: white;
  padding: 14px 28px;
  border-radius: 50px;
  box-shadow: 0 10px 30px rgba(255, 107, 157, 0.4);
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 1000;
  animation: slideUp 0.3s ease-out;
  font-weight: 500;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
  from { opacity: 0; transform: translate(-50%, 20px); }
}

/* ==================== 魔法加载遮罩 ==================== */
.magic-loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(15px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.magic-content {
  text-align: center;
  animation: float 3s ease-in-out infinite;
}

.magic-icon-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.magic-icon {
  font-size: 40px;
  z-index: 2;
  animation: scalePulse 1.5s infinite;
}

.magic-ring, .magic-ring-2 {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 2px solid #FF85A1;
  opacity: 0;
}

.magic-ring {
  width: 100%; height: 100%;
  animation: ripple 2s infinite;
}

.magic-ring-2 {
  width: 100%; height: 100%;
  animation: ripple 2s infinite 0.6s;
}

.magic-title {
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(135deg, #FF6B9D 0%, #8B5CF6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 12px;
}

.magic-subtitle {
  font-size: 14px;
  color: #8B7B9B;
  margin-bottom: 32px;
}

.loading-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
  width: fit-content;
  margin: 0 auto;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #6C6377;
  opacity: 0;
  animation: slideRightFade 0.5s forwards;
}

.step-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #FFD6E0;
}

.step-item.active .step-dot {
  background: #FF85A1;
  box-shadow: 0 0 10px rgba(255, 133, 161, 0.5);
}

/* 动画定义 */
@keyframes scalePulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

@keyframes ripple {
  0% { width: 60%; height: 60%; opacity: 0.6; border-width: 4px; }
  100% { width: 150%; height: 150%; opacity: 0; border-width: 0px; }
}

@keyframes slideRightFade {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ==================== 响应式设计 (手机端适配) ==================== */
@media (max-width: 1024px) {
  /* 调整容器宽度 */
  .home-container {
    max-width: 100%;
    padding: 10px;
  }
  
  /* 调整Hero区域内边距 */
  .hero-section {
    padding: 40px 40px;
  }
  
  /* 调整页面标题大小 */
  .page-title {
    font-size: 2.2rem;
  }
}

@media (max-width: 768px) {
  /* 调整Hero区域内边距 */
  .hero-section {
    padding: 30px 20px;
    margin-bottom: 24px;
  }
  
  /* 调整平台标语大小 */
  .platform-slogan {
    font-size: 16px;
  }
  
  /* 调整页面标题大小 */
  .page-title {
    font-size: 1.8rem;
  }
  
  /* 调整副标题大小 */
  .page-subtitle {
    font-size: 14px;
  }
  
  /* 调整品牌标签 */
  .brand-pill {
    padding: 6px 16px;
    font-size: 12px;
    margin-bottom: 16px;
  }
  
  /* 调整Hero内容间距 */
  .hero-content {
    margin-bottom: 24px;
  }
  
  /* 调整错误提示 */
  .error-toast {
    padding: 12px 24px;
    font-size: 14px;
    bottom: 24px;
  }
}

@media (max-width: 480px) {
  /* 调整Hero区域内边距 */
  .hero-section {
    padding: 24px 16px;
    border-radius: 24px;
  }
  
  /* 进一步调整页面标题大小 */
  .page-title {
    font-size: 1.5rem;
  }
  
  /* 调整平台标语 */
  .platform-slogan {
    font-size: 14px;
    line-height: 1.5;
  }
  
  /* 调整错误提示 */
  .error-toast {
    padding: 10px 20px;
    font-size: 13px;
    bottom: 16px;
    left: 16px;
    right: 16px;
    transform: none;
    text-align: center;
    justify-content: center;
  }
  
  /* 调整首页容器 */
  .home-container {
    padding: 5px;
  }
}
</style>
