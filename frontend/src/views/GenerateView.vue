<template>
  <div class="container">
    <!-- 美化的标题区域 -->
    <div class="generate-header">
      <div class="magic-badge">
        <span v-if="isGenerating">🎨</span>
        <span v-else-if="hasFailedImages">💔</span>
        <span v-else-if="!hasStarted">🌟</span>
        <span v-else>✨</span>
      </div>
      <h1 class="generate-title">
        <span v-if="!hasStarted">准备就绪</span>
        <span v-else-if="isGenerating">魔法绘制中</span>
        <span v-else-if="hasFailedImages">需要修复</span>
        <span v-else>绘制完成</span>
      </h1>
      <p class="generate-subtitle">
        <span v-if="!hasStarted && pendingCount === store.progress.total">🎀 共 <span class="highlight-num">{{ store.progress.total }}</span> 页等待绘制，点击下方按钮开始~</span>
        <span v-else-if="isGenerating">✨ 正在施法生成第 {{ doneCount + 1 }} / {{ store.progress.total }} 页...</span>
        <span v-else-if="hasFailedImages">💔 哎呀，有 <span class="highlight-num">{{ failedCount }}</span> 张图片生成失败了</span>
        <span v-else-if="pendingCount > 0">🎀 还有 <span class="highlight-num">{{ pendingCount }}</span> 页待绘制</span>
        <span v-else>🎉 全部 <span class="highlight-num">{{ store.progress.total }}</span> 张图片生成完成啦！</span>
      </p>
      <div class="header-actions">
        <!-- 开始生图按钮 -->
        <button
          v-if="!hasStarted && !isGenerating"
          class="btn-gradient btn-start"
          @click="handleStartGeneration"
        >
          💖 开始生图
        </button>
        <!-- 停止生图按钮（仅非高并发模式显示） -->
        <button
          v-if="isGenerating && !isHighConcurrency"
          class="btn-stop"
          @click="handleStopGeneration"
        >
          ⏹️ 停止生图
        </button>
        <!-- 高并发模式提示 -->
        <span v-if="isGenerating && isHighConcurrency" class="concurrency-badge">
          ⚡ 高并发模式
        </span>
        <button
          v-if="hasFailedImages && !isGenerating"
          class="btn-gradient"
          @click="retryAllFailed"
          :disabled="isRetrying"
        >
          {{ isRetrying ? '🔧 正在修复...' : '🪄 一键补全失败图片' }}
        </button>
        <button class="btn-glass" @click="router.push('/outline')">
          ← 返回大纲
        </button>
      </div>
    </div>

    <div class="card glass-card">
      <div class="progress-info">
        <span class="progress-label">魔法进度</span>
        <span class="progress-percent">{{ Math.round(progressPercent) }}%</span>
      </div>
      <div class="progress-container">
        <div class="progress-bar" :style="{ width: progressPercent + '%' }" />
      </div>

      <div v-if="error" class="error-msg cancel-bounce">
        {{ error }}
      </div>

      <div class="grid-cols-4 image-grid">
        <div v-for="image in store.images" :key="image.index" class="image-card">
          <!-- 图片展示区域 -->
          <div v-if="image.url && image.status === 'done'" class="image-preview">
            <img 
              :src="image.url" 
              :alt="`第 ${image.index + 1} 页`" 
              @click="openImagePreview(image.index)"
              style="cursor: pointer;"
            />
            <!-- 重新生成按钮（悬停显示） -->
            <div class="image-overlay">
              <button
                class="overlay-btn"
                @click="regenerateImage(image.index)"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M23 4v6h-6"></path>
                  <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                </svg>
                重新施法
              </button>
            </div>
          </div>

          <!-- 生成中状态（已发送请求，无法停止） -->
          <div v-else-if="image.status === 'generating' || image.status === 'retrying'" class="image-placeholder loading-placeholder">
            <div class="spinner-heart"></div>
            <div class="status-text">{{ image.status === 'retrying' ? '修复中...' : '绘制中...' }}</div>
          </div>

          <!-- 失败状态 -->
          <div v-else-if="image.status === 'error'" class="image-placeholder error-placeholder">
            <div class="error-icon">💔</div>
            <div class="status-text">{{ getStatusText(image.status) }}</div>
            <!-- 悬停显示的重新开始按钮 -->
            <div class="image-overlay waiting-overlay">
              <button
                class="overlay-btn btn-start-single"
                @click="startSingleImage(image.index)"
              >
                🔄 点击重试
              </button>
            </div>
          </div>

          <!-- 已停止状态 -->
          <div v-else-if="image.status === 'stopped'" class="image-placeholder stopped-placeholder">
            <div class="stopped-icon">⏸️</div>
            <div class="status-text text-light">{{ getStatusText(image.status) }}</div>
            <!-- 悬停显示的重新开始按钮 -->
            <div class="image-overlay waiting-overlay">
              <button
                class="overlay-btn btn-start-single"
                @click="startSingleImage(image.index)"
              >
                ▶️ 继续生成
              </button>
            </div>
          </div>

          <!-- 等待中状态 -->
          <div v-else class="image-placeholder waiting-placeholder">
            <div class="waiting-icon">🎀</div>
            <div class="status-text text-light">{{ getStatusText(image.status) }}</div>
            <!-- 悬停显示的按钮 -->
            <div class="image-overlay waiting-overlay">
              <!-- 如果在队列中，显示取消按钮；否则显示开始按钮 -->
              <button
                v-if="pendingQueue.includes(image.index)"
                class="overlay-btn btn-stop-single"
                @click="stopSingleImage(image.index)"
              >
                ❌ 取消排队
              </button>
              <button
                v-else
                class="overlay-btn btn-start-single"
                @click="startSingleImage(image.index)"
              >
                ✨ 单独生成
              </button>
            </div>
          </div>

          <!-- 底部信息栏 -->
          <div class="image-footer">
            <span class="page-label">P{{ image.index + 1 }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 图片预览模态框 -->
  <ImagePreviewModal 
    :visible="previewVisible" 
    :images="generatedImages" 
    :initial-index="previewInitialIndex"
    @close="closeImagePreview"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useGeneratorStore } from '../stores/generator'
import { regenerateImage as apiRegenerateImage, createHistory, updateHistory, getConfig } from '../api'
import ImagePreviewModal from '../components/ImagePreviewModal.vue'

const router = useRouter()
const store = useGeneratorStore()

const error = ref('')
const isRetrying = ref(false)
const hasStarted = ref(false)  // 是否已开始生成
const isHighConcurrency = ref(false)  // 是否是高并发模式
const isStopped = ref(false)  // 是否已停止

// 图片预览相关
const previewVisible = ref(false)
const previewInitialIndex = ref(0)

// 计算所有已生成图片的URL数组
const generatedImages = computed(() => {
  return store.images
    .filter(img => img.url && img.status === 'done')
    .map(img => img.url)
    .sort((a, b) => {
      // 确保图片按索引顺序排列
      const aIndex = store.images.findIndex(img => img.url === a)
      const bIndex = store.images.findIndex(img => img.url === b)
      return aIndex - bIndex
    })
})

// 打开图片预览
const openImagePreview = (index: number) => {
  const image = store.images[index]
  if (image && image.url && image.status === 'done') {
    // 找到该图片在已生成图片数组中的索引
    const previewIndex = generatedImages.value.indexOf(image.url)
    if (previewIndex !== -1) {
      previewInitialIndex.value = previewIndex
      previewVisible.value = true
    }
  }
}

// 关闭图片预览
const closeImagePreview = () => {
  previewVisible.value = false
}

// 队列管理
const pendingQueue = ref<number[]>([])
const activeTasks = ref<number[]>([])  // 使用数组而非 Set 以确保响应性
const abortControllers = new Map<number, AbortController>()

const isGenerating = computed(() => activeTasks.value.length > 0 || pendingQueue.value.length > 0)

const progressPercent = computed(() => {
  if (store.progress.total === 0) return 0
  const percent = (store.progress.current / store.progress.total) * 100
  return Math.min(percent, 100)  // 不超过 100%
})

const hasFailedImages = computed(() => store.images.some(img => img.status === 'error'))

const failedCount = computed(() => store.images.filter(img => img.status === 'error').length)

const doneCount = computed(() => store.images.filter(img => img.status === 'done').length)

const pendingCount = computed(() => store.images.filter(img => img.status !== 'done' && img.status !== 'error').length)

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    generating: '绘制中',
    done: '✨完成',
    error: '失败',
    retrying: '修复中',
    pending: '等待',
    stopped: '已停止'
  }
  return texts[status] || '等待'
}

// 简单 UUID 生成器
function uuidv4() {
  return '10000000-1000-4000-8000-100000000000'.replace(/[018]/g, c =>
    (Number(c) ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> Number(c) / 4).toString(16)
  )
}

// 开始全局生成
function handleStartGeneration() {
  hasStarted.value = true
  isStopped.value = false
  
  // 将所有未完成的任务加入队列
  store.images.forEach(img => {
    if (img.status !== 'done') {
      addToQueue(img.index)
    }
  })
}

// 停止生图（只停止队列中等待的任务，已发送给模型的无法停止）
function handleStopGeneration() {
  isStopped.value = true
  // 清空等待队列
  while(pendingQueue.value.length > 0) {
    const index = pendingQueue.value.shift()!
    store.updateProgress(index, 'stopped')
  }
  // 注意：不再 abort 正在运行的请求，因为已发送给模型无法停止
}

// 单独开始生成一张图片
function startSingleImage(index: number) {
  hasStarted.value = true
  isStopped.value = false
  addToQueue(index)
}

// 单独取消排队（只能取消还在队列里的）
function stopSingleImage(index: number) {
  const qIndex = pendingQueue.value.indexOf(index)
  if (qIndex > -1) {
    pendingQueue.value.splice(qIndex, 1)
    store.updateProgress(index, 'stopped')
  }
}

function addToQueue(index: number) {
  // 避免重复添加
  if (pendingQueue.value.includes(index) || activeTasks.value.includes(index)) return
  
  // 检查是否已经在 done 状态
  const img = store.images.find(i => i.index === index)
  if (img && img.status === 'done') return

  pendingQueue.value.push(index)
  store.updateProgress(index, 'pending')
  processQueue()
}

async function processQueue() {
  const limit = isHighConcurrency.value ? 3 : 1
  
  while (activeTasks.value.length < limit && pendingQueue.value.length > 0) {
    const index = pendingQueue.value.shift()!
    startTask(index)
  }
}

async function startTask(index: number) {
  if (!activeTasks.value.includes(index)) activeTasks.value.push(index)
  const controller = new AbortController()
  abortControllers.set(index, controller)
  store.updateProgress(index, 'generating')

  // 确保有 Task ID
  if (!store.taskId) {
    store.taskId = uuidv4()
  }

  const page = store.outline.pages.find(p => p.index === index)
  if (!page) {
    const removeIdx = activeTasks.value.indexOf(index)
    if (removeIdx > -1) activeTasks.value.splice(removeIdx, 1)
    abortControllers.delete(index)
    return
  }
  
  try {
     const result = await apiRegenerateImage(
        store.taskId, 
        page, 
        true, 
        { fullOutline: store.outline.raw, userTopic: store.topic },
        controller.signal
     )
     
     if (result.success && result.image_url) {
        store.updateProgress(index, 'done', result.image_url)
        await syncHistory()
     } else {
        store.updateProgress(index, 'error', undefined, result.error)
     }
  } catch (e: any) {
     if (e.name === 'AbortError' || e.message === 'canceled' || axios.isCancel(e)) {
        store.updateProgress(index, 'stopped')
     } else {
        store.updateProgress(index, 'error', undefined, e.message || String(e))
     }
  } finally {
     const idx = activeTasks.value.indexOf(index)
     if (idx > -1) activeTasks.value.splice(idx, 1)
     abortControllers.delete(index)
     processQueue() // 触发下一个
  }
}

// 同步历史记录
async function syncHistory() {
  if (!store.recordId || !store.taskId) return
  
  try {
    // 按索引位置保存文件名，未完成的位置用空字符串占位
    // 这样加载时可以通过索引正确还原每张图片的状态
    const generatedImages = store.images.map(img => {
      if (img.status === 'done' && img.url) {
        // 从 URL 提取文件名
        // /api/images/{taskId}/{filename}
        const parts = img.url!.split('/')
        return parts[parts.length - 1].split('?')[0]
      }
      return '' // 未完成的图片用空字符串占位
    })

    // 计算状态
    const totalImages = store.images.length
    const doneImagesCount = store.images.filter(img => img.status === 'done').length
    const failedImagesCount = store.images.filter(img => img.status === 'error').length
    
    let status = 'draft'
    if (doneImagesCount === totalImages && failedImagesCount === 0) {
      // 全部完成且无失败
      status = 'completed'
    } else if (doneImagesCount > 0) {
      // 部分完成
      status = 'partial'
    }

    // 找到第一个已完成的图片作为缩略图
    const firstDoneImage = generatedImages.find(f => f !== '')
    const thumbnail = firstDoneImage || undefined
    
    await updateHistory(store.recordId, { 
      images: { task_id: store.taskId, generated: generatedImages }, 
      status: status, 
      thumbnail: thumbnail 
    })

    // 如果全部完成且不在生成中，跳转到结果页
    if (status === 'completed' && !isGenerating.value) {
      store.finishGeneration(store.taskId)
      setTimeout(() => {
        router.push('/result')
      }, 500)
    }
  } catch (e) {
    console.error('同步历史记录失败:', e)
  }
}

// 重新生成图片（即使已完成也强制重新生成）
function regenerateImage(index: number) {
  hasStarted.value = true
  isStopped.value = false
  // 强制加入队列，不检查 done 状态
  if (pendingQueue.value.includes(index) || activeTasks.value.includes(index)) return
  pendingQueue.value.push(index)
  store.updateProgress(index, 'pending')
  processQueue()
}

// 批量重试所有失败的图片
async function retryAllFailed() {
  hasStarted.value = true
  isStopped.value = false
  const failedPages = store.getFailedPages()
  if (failedPages.length === 0) return
  isRetrying.value = true // UI显示用
  
  failedPages.forEach(p => addToQueue(p.index))
  isRetrying.value = false // 立即重置，因为我们转交给队列处理了
}



// 监听 images 变化，自动更新 progress
// 其实 store.updateProgress 已经处理了 progress.current/total
// 我们只需要确保初始化正确

onMounted(async () => {
  if (store.outline.pages.length === 0) {
    // 延迟检查，避免过渡期间状态未就绪导致误判
    setTimeout(() => {
      if (store.outline.pages.length === 0) {
        router.push('/')
      }
    }, 100)
    return
  }
  
  // 初始化images数组和进度信息 - 解决新生成大纲后没有卡片的问题
  if (store.images.length === 0 && store.outline.pages.length > 0) {
    // 如果images数组为空，但outline.pages有内容，初始化images数组
    store.images = store.outline.pages.map(page => ({
      index: page.index,
      url: '',
      status: 'pending'
    }))
    // 更新进度信息
    store.progress.total = store.outline.pages.length
    store.progress.current = 0
  }
  
  // 创建历史记录
  if (!store.recordId) {
    try {
      const result = await createHistory(store.topic, { raw: store.outline.raw, pages: store.outline.pages })
      if (result.success && result.record_id) {
        store.recordId = result.record_id
      }
    } catch (e) {
      console.error('创建历史记录失败:', e)
    }
  }
  // 获取高并发配置
  try {
    const configResult = await getConfig()
    if (configResult.success && configResult.config) {
      const activeProvider = configResult.config.image_generation.active_provider
      const providerConfig = configResult.config.image_generation.providers[activeProvider]
      if (providerConfig) {
        isHighConcurrency.value = providerConfig.high_concurrency === true
      }
    }
  } catch (e) {
    console.error('获取配置失败:', e)
  }

  // 初始化进度：计算已完成的图片数量
  const doneCount = store.images.filter(img => img.status === 'done').length
  if (doneCount > 0) {
    // 如果有已完成的图片，说明之前已经开始过
    hasStarted.value = true
    store.progress.current = doneCount
  }
  
  // 检查是否有未完成的图片需要继续
  const pendingCount = store.images.filter(img => img.status !== 'done' && img.status !== 'error').length
  if (pendingCount === 0 && doneCount > 0 && !hasFailedImages.value) {
    // 全部完成，没有失败的
    // 可以显示完成状态
  }
})
</script>

<style scoped>
/* Header Layout - 居中少女风格 */
.generate-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  width: 100%;
  margin: 0 0 20px 0;
  gap: 8px;
}

/* 魔法徽章 */
.magic-badge {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFE0EC 0%, #F0E6FF 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  box-shadow: 0 10px 30px rgba(255, 133, 161, 0.25);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

/* 渐变标题 */
.generate-title {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #FF6B9D 0%, #C44569 50%, #8B5CF6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 8px 0;
}

.generate-subtitle {
  font-size: 1rem;
  color: #6C6377;
  margin-bottom: 20px;
}

.highlight-num {
  font-weight: 700;
  font-size: 1.2rem;
  background: linear-gradient(90deg, #FF69B4, #BA55D3);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

/* 渐变按钮 */
.btn-gradient {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  background: linear-gradient(135deg, #FF85A1 0%, #FF6B9D 50%, #C44569 100%);
  border: none;
  border-radius: 50px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 8px 25px rgba(255, 133, 161, 0.4);
}

.btn-gradient:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(255, 133, 161, 0.5);
}

.btn-gradient:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 玻璃按钮 */
.btn-glass {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(255, 133, 161, 0.3);
  border-radius: 50px;
  font-weight: 600;
  color: #6C6377;
  cursor: pointer;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
}

.btn-glass:hover {
  border-color: #FF85A1;
  color: #FF85A1;
  transform: translateY(-2px);
}

/* 玻璃卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.08);
  border: 1px solid rgba(255,255,255,0.8);
}

/* 进度条 */
.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 700;
  color: #4A4063;
}
.progress-percent { color: #FF85A1; }

.progress-container {
  height: 12px;
  background: #F0E6EF;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 40px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #FF9A9E 0%, #FECFEF 100%);
  border-radius: 10px;
  transition: width 0.5s ease-out;
  box-shadow: 0 0 10px rgba(255, 154, 158, 0.4);
}

/* 图片网格 */
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 24px;
}

/* 响应式设计 - 图片网格 */
@media (max-width: 1024px) {
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px;
  }
  
  /* 调整玻璃卡片内边距 */
  .glass-card {
    padding: 24px;
  }
  
  /* 调整标题大小 */
  .generate-title {
    font-size: 1.5rem;
  }
  
  /* 调整副标题大小 */
  .generate-subtitle {
    font-size: 0.9rem;
  }
  
  /* 调整按钮大小 */
  .btn-gradient,
  .btn-glass {
    padding: 10px 20px;
    font-size: 0.9rem;
  }
  
  /* 调整按钮间距 */
  .header-actions {
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 12px;
  }
  
  /* 进一步调整玻璃卡片内边距 */
  .glass-card {
    padding: 16px;
  }
  
  /* 进一步调整标题大小 */
  .generate-title {
    font-size: 1.2rem;
  }
  
  /* 调整进度条容器 */
  .progress-container {
    margin-bottom: 24px;
  }
  
  /* 调整状态信息大小 */
  .status-info {
    font-size: 0.9rem;
  }
}

.image-card {
  display: flex;
  flex-direction: column;
  border-radius: 16px;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
  min-height: 280px;
}
.image-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(159, 134, 192, 0.15); }

.image-preview {
  aspect-ratio: 3/4;
  position: relative;
  flex: 1;
}
.image-preview img { width: 100%; height: 100%; object-fit: cover; }

.image-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity 0.2s;
}
.image-preview:hover .image-overlay { opacity: 1; }

/* 修复：确保占位符状态下悬停也能显示操作按钮 */
.image-placeholder:hover .image-overlay,
.image-placeholder:hover .waiting-overlay {
  opacity: 1;
}

.overlay-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 16px; background: white; border: none; border-radius: 20px;
  cursor: pointer; font-size: 13px; color: #FF85A1; font-weight: 600;
  transition: all 0.2s;
}
.overlay-btn:hover { background: #FF85A1; color: white; }

.image-placeholder {
  aspect-ratio: 3/4;
  background: #FAFAFA;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 12px; flex: 1; min-height: 240px;
}
.loading-placeholder { background: #FFF0F5; }
.error-placeholder { background: #FFF1F0; }

.spinner-heart {
  width: 32px; height: 32px;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23FF85A1'%3E%3Cpath d='M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z'/%3E%3C/svg%3E") no-repeat center center;
  animation: heartbeat 1.2s infinite ease-in-out;
}
@keyframes heartbeat { 0%,100% { transform: scale(0.8); } 50% { transform: scale(1.1); } }

.status-text { font-size: 13px; color: #8D84A3; }
.text-light { color: #CCC; }

.error-icon { font-size: 24px; }
.stopped-icon { font-size: 24px; }
.stopped-placeholder { background: #FAFAFA; }
.retry-btn {
  margin-top: 8px; padding: 6px 16px;
  background: #FF85A1; color: white; border: none;
  border-radius: 20px; cursor: pointer; font-size: 12px;
}

.image-footer {
  padding: 12px 16px;
  border-top: 1px solid #F8F8F8;
  display: flex; justify-content: space-between; align-items: center;
  font-size: 12px;
}
.page-label { color: #BBB; font-weight: 600; }

.status-badge { padding: 2px 8px; border-radius: 10px; font-weight: 600; font-size: 11px; }
.status-badge.done { background: #E6F7ED; color: #52C41A; }
.status-badge.generating, .status-badge.retrying { background: #E6F4FF; color: #1890FF; }
.status-badge.error { background: #FFF1F0; color: #FF4D4F; }
.status-badge.pending { background: #F5F0FF; color: #B8A6D9; }
.status-badge.stopped { background: #F5F5F5; color: #999; }

.btn-stop-single {
  background: rgba(255, 255, 255, 0.95) !important;
  color: #FF6B6B !important;
  padding: 10px 24px !important;
  height: 40px !important;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.2);
  box-sizing: border-box;
  border-radius: 50px;
  border: 2px solid #FFD6D6 !important; /* 淡红色边框 */
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-stop-single:hover {
  background: linear-gradient(135deg, #FF8F8F 0%, #FF6B6B 100%) !important;
  color: white !important;
  border-color: transparent !important;
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
}

.btn-jelly {
  box-shadow: 0 4px 12px rgba(255, 133, 161, 0.3);
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.btn-jelly:hover { transform: scale(1.05); }

.btn-outline {
  background: white; border: 2px solid #EEE; color: #999;
  padding: 8px 20px; border-radius: 99px; cursor: pointer; font-weight: 600;
  transition: all 0.2s;
}
.btn-outline:hover { border-color: #FF85A1; color: #FF85A1; }

/* 开始生图按钮 - 特大少女风格 */
.btn-start {
  padding: 14px 32px;
  font-size: 16px;
  animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 4px 20px rgba(255, 133, 161, 0.4); }
  50% { box-shadow: 0 4px 30px rgba(255, 133, 161, 0.6); }
}

/* 等待中状态美化 */
.waiting-placeholder {
  background: linear-gradient(135deg, #FFF8FA 0%, #F8F0FF 100%);
  position: relative;
}

.waiting-icon {
  font-size: 28px;
  animation: swing 2s ease-in-out infinite;
}

@keyframes swing {
  0%, 100% { transform: rotate(-5deg); }
  50% { transform: rotate(5deg); }
}

/* 统一卡片内容区域高度 */
.image-preview,
.image-placeholder {
  width: 100%;
  height: 300px; /* 统一内容区域高度 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

/* 已完成卡片的图片高度统一 */
.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 统一覆盖层按钮垂直位置 */
.image-overlay,
.waiting-overlay {
  opacity: 0;
  background: transparent; /* 透明背景，只显示按钮 */
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  /* 使用flex布局，将按钮放置在状态文字下方 */
  flex-direction: column;
  justify-content: center; /* 居中对齐，确保在图标和文字区域 */
  align-items: center;
  transition: opacity 0.2s ease;
  z-index: 10;
  pointer-events: none; /* 避免覆盖层阻止卡片其他区域的点击 */
}

/* 覆盖层按钮基础样式 (正常状态：白底粉字，清新可爱) */
.image-overlay .overlay-btn,
.waiting-overlay .overlay-btn {
  pointer-events: auto;
  background: rgba(255, 255, 255, 0.95) !important;
  color: #FF85A1 !important;
  padding: 10px 24px !important;
  height: 40px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(255, 133, 161, 0.2);
  border-radius: 50px;
  border: 2px solid #FFE0EC !important; /* 淡粉色边框 */
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  margin-top: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-sizing: border-box;
}

/* 覆盖层按钮悬停样式 (Hover状态：渐变粉底白字，活力满满) */
.image-overlay .overlay-btn:hover,
.waiting-overlay .overlay-btn:hover {
  background: linear-gradient(135deg, #FF85A1 0%, #FF6B9D 100%) !important;
  color: white !important;
  border-color: transparent !important;
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 25px rgba(255, 107, 157, 0.5);
}

.image-overlay .overlay-btn:active,
.waiting-overlay .overlay-btn:active {
  transform: scale(0.95);
  box-shadow: 0 2px 8px rgba(255, 107, 157, 0.3);
}

/* 单栏生成按钮样式 (正常状态) */
.btn-start-single {
  background: rgba(255, 255, 255, 0.95) !important;
  color: #FF85A1 !important;
  padding: 10px 24px !important;
  height: 40px !important;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(255, 133, 161, 0.2);
  box-sizing: border-box;
  border-radius: 50px;
  border: 2px solid #FFE0EC !important;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* 单栏生成按钮样式 (Hover状态) */
.btn-start-single:hover {
  background: linear-gradient(135deg, #FF85A1 0%, #FF6B9D 100%) !important;
  color: white !important;
  border-color: transparent !important;
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 25px rgba(255, 107, 157, 0.5);
}

/* 停止按钮样式 */
.btn-stop {
  padding: 12px 24px;
  background: linear-gradient(135deg, #FF6B6B 0%, #EE5A5A 100%);
  color: white;
  border: none;
  border-radius: 99px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.btn-stop:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

/* 高并发模式提示 */
.concurrency-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
  color: #E65100;
  border-radius: 99px;
  font-size: 13px;
  font-weight: 600;
  animation: pulse-badge 1.5s infinite;
}

@keyframes pulse-badge {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
/* 手机端优化 */
@media (max-width: 768px) {
  /* 容器调整 */
  .container {
    padding: 16px !important;
  }
  
  /* 生成标题区域 */
  .generate-header {
    margin: 0 0 16px 0 !important;
    gap: 6px !important;
  }
  
  /* 魔法徽章 */
  .magic-badge {
    width: 56px !important;
    height: 56px !important;
    font-size: 24px !important;
  }
  
  /* 生成标题 */
  .generate-title {
    font-size: 1.5rem !important;
    margin: 4px 0 !important;
  }
  
  /* 生成副标题 */
  .generate-subtitle {
    font-size: 0.9rem !important;
    margin-bottom: 16px !important;
  }
  
  /* 头部操作区 */
  .header-actions {
    gap: 12px !important;
    flex-direction: column;
    align-items: stretch;
  }
  
  /* 按钮样式 */
  .btn-gradient,
  .btn-glass,
  .btn-stop {
    padding: 10px 20px !important;
    justify-content: center;
    font-size: 14px !important;
  }
  
  /* 卡片样式 */
  .glass-card {
    padding: 20px !important;
    border-radius: 16px !important;
  }
  
  /* 进度信息 */
  .progress-info {
    font-size: 14px !important;
  }
  
  /* 图片网格 */
  .grid-cols-4.image-grid {
    grid-template-columns: 1fr !important;
    gap: 12px !important;
  }
  
  /* 图片卡片 */
  .image-card {
    border-radius: 12px !important;
    max-width: 320px !important;
    margin: 0 auto !important;
  }
  
  /* 图片预览 */
  .image-preview {
    aspect-ratio: 3/4;
  }
  
  /* 图片占位符 */
  .image-placeholder {
    aspect-ratio: 3/4;
  }
  
  /* 状态文本 */
  .status-text {
    font-size: 13px !important;
  }
  
  /* 底部信息栏 */
  .image-footer {
    padding: 8px 12px !important;
  }
  
  /* 页面标签 */
  .page-label {
    font-size: 11px !important;
    padding: 3px 8px !important;
  }
}
</style>
