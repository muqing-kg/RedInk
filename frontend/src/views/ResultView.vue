<template>
  <div class="container">
    <!-- 美化的标题区域 -->
    <div class="result-header">
      <div class="success-badge">
        <span class="badge-icon">🎉</span>
      </div>
      <h1 class="result-title">创作完成</h1>
      <p class="result-subtitle">
        <span class="sparkle">✨</span>
        恭喜！你的小红书图文已生成完毕，共 
        <span class="highlight-count">{{ store.images.length }}</span> 
        张精美图片
        <span class="sparkle">✨</span>
      </p>
      <div class="action-buttons">
        <button class="btn-glass" @click="startOver">
          <span class="btn-icon">🔄</span>
          再来一篇
        </button>
        <button class="btn-gradient" @click="downloadAll">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
          一键下载全部
        </button>
      </div>
    </div>

    <!-- 图片网格卡片 -->
    <div class="result-card">
      <div class="grid-cols-4">
        <div v-for="image in store.images" :key="image.index" class="image-card group">
          <!-- Image Area -->
          <div 
            v-if="image.url" 
            class="image-preview"
            @click="viewImage(image.url)"
          >
            <img
              :src="image.url"
              :alt="`第 ${image.index + 1} 页`"
            />
            <!-- Regenerating Overlay -->
            <div v-if="regeneratingIndex === image.index" class="regenerating-overlay">
               <div class="mini-spinner"></div>
               <span>重绘中...</span>
            </div>
            
            <!-- Hover Overlay -->
            <div v-else class="hover-overlay">
              <span class="preview-icon">🔍</span>
              <span>预览大图</span>
            </div>
          </div>
          
          <!-- Action Bar -->
          <div class="image-actions">
            <span class="page-label">P{{ image.index + 1 }}</span>
            <div class="action-group">
              <button 
                class="icon-btn"
                title="重新生成此图"
                @click="handleRegenerate(image)"
                :disabled="regeneratingIndex === image.index"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 4v6h-6"></path><path d="M1 20v-6h6"></path><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
              </button>
              <button 
                class="download-btn"
                @click="downloadOne(image)"
              >
                下载
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 标题区域居中美化 */
.result-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-bottom: 40px;
  padding: 20px 0;
}

.success-badge {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFE0EC 0%, #FFF0F5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  box-shadow: 0 10px 30px rgba(255, 133, 161, 0.2);
  animation: float 3s ease-in-out infinite;
}

.badge-icon {
  font-size: 40px;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.result-title {
  font-size: 2.2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #FF6B9D 0%, #C44569 50%, #8B5CF6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 12px;
}

.result-subtitle {
  font-size: 1.1rem;
  color: #6C6377;
  margin-bottom: 28px;
}

.sparkle {
  animation: sparkle 2s ease-in-out infinite;
}

@keyframes sparkle {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.2); }
}

.highlight-count {
  font-weight: 700;
  font-size: 1.4rem;
  background: linear-gradient(90deg, #FF69B4, #BA55D3);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 4px;
}

/* 按钮组 */
.action-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: center;
}

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
  box-shadow: 0 8px 20px rgba(255, 133, 161, 0.15);
}

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

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(255, 133, 161, 0.5);
}

.btn-icon {
  font-size: 16px;
}

/* 结果卡片 */
.result-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

/* 图片卡片 */
.image-card {
  border-radius: 16px;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.image-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px rgba(255, 133, 161, 0.15);
}

.image-preview {
  position: relative;
  aspect-ratio: 3/4;
  overflow: hidden;
  cursor: pointer;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s;
}

.image-card:hover .image-preview img {
  transform: scale(1.08);
}

/* 重绘中遮罩 */
.regenerating-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.regenerating-overlay span {
  font-size: 12px;
  color: #FF85A1;
  margin-top: 8px;
  font-weight: 600;
}

.mini-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #FFE0EC;
  border-top-color: #FF85A1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 悬停遮罩 */
.hover-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 107, 157, 0.6) 0%, rgba(139, 92, 246, 0.6) 100%);
  opacity: 0;
  transition: opacity 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  gap: 8px;
}

.image-card:hover .hover-overlay {
  opacity: 1;
}

.preview-icon {
  font-size: 28px;
}

/* 操作栏 */
.image-actions {
  padding: 12px 16px;
  border-top: 1px solid #f5f0f3;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-label {
  font-size: 12px;
  font-weight: 700;
  color: #C44569;
  background: linear-gradient(135deg, #FFE0EC 0%, #FFF0F5 100%);
  padding: 4px 10px;
  border-radius: 20px;
}

.action-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.icon-btn {
  border: none;
  background: none;
  color: #9CA3AF;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}

.icon-btn:hover {
  color: #FF85A1;
}

.icon-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.download-btn {
  border: none;
  background: linear-gradient(90deg, #FF85A1, #C44569);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.download-btn:hover {
  opacity: 0.8;
}
</style>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useGeneratorStore } from '../stores/generator'
import { regenerateImage, getToken, downloadFile } from '../api'
import { showError } from '../utils/dialog'

const router = useRouter()
const store = useGeneratorStore()
const regeneratingIndex = ref<number | null>(null)

const viewImage = (url: string) => {
  const baseUrl = url.split('?')[0]
  const token = getToken()
  const tokenParam = token ? `&token=${token}` : ''
  window.open(baseUrl + '?thumbnail=false' + tokenParam, '_blank')
}

const startOver = () => {
  store.reset()
  router.push('/')
}

const downloadOne = async (image: any) => {
  if (image.url) {
    try {
      const baseUrl = image.url.split('?')[0]
      await downloadFile(baseUrl + '?thumbnail=false', `rednote_page_${image.index + 1}.png`)
    } catch (e: any) {
      showError('下载失败: ' + e.message)
    }
  }
}

const downloadAll = async () => {
  if (store.recordId) {
    try {
      await downloadFile(`/api/history/${store.recordId}/download`, `rednote_images.zip`)
    } catch (e: any) {
      showError('下载失败: ' + e.message)
    }
  } else {
    // 逐个下载
    for (let i = 0; i < store.images.length; i++) {
      const image = store.images[i]
      if (image.url) {
        try {
          const baseUrl = image.url.split('?')[0]
          await downloadFile(baseUrl + '?thumbnail=false', `rednote_page_${image.index + 1}.png`)
        } catch (e: any) {
          console.error('下载失败:', e)
        }
        // 间隔 300ms
        if (i < store.images.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 300))
        }
      }
    }
  }
}

const handleRegenerate = async (image: any) => {
  if (!store.taskId || regeneratingIndex.value !== null) return

  regeneratingIndex.value = image.index
  try {
    // Find the page content from outline
    const pageContent = store.outline.pages.find(p => p.index === image.index)
    if (!pageContent) {
       showError('无法找到对应页面的内容')
       return
    }

    // 构建上下文信息
    const context = {
      fullOutline: store.outline.raw || '',
      userTopic: store.topic || ''
    }

    const result = await regenerateImage(store.taskId, pageContent, true, context)
    if (result.success && result.image_url) {
       const newUrl = result.image_url
       store.updateImage(image.index, newUrl)
    } else {
       showError('重绘失败: ' + (result.error || '未知错误'))
    }
  } catch (e: any) {
    showError('重绘失败: ' + e.message)
  } finally {
    regeneratingIndex.value = null
  }
}
</script>
