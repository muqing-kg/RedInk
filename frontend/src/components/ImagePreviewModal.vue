<template>
  <!-- 图片预览模态框 -->
  <div v-if="visible && images.length > 0" class="image-preview-modal" @click="handleCloseModal">
    <!-- 关闭按钮 -->
    <button class="preview-close-btn" @click="handleCloseModal">×</button>
    
    <!-- 导航按钮 -->
    <button 
      class="nav-btn prev-btn" 
      @click.stop="navigate(-1)" 
      :disabled="currentIndex <= 0"
    >
      ‹
    </button>
    
    <!-- 图片容器 -->
    <div class="preview-container" @click.stop>
      <!-- 主图片 -->
      <img 
        ref="previewImage" 
        :src="currentImage" 
        :alt="`Preview ${currentIndex + 1}/${images.length}`" 
        class="preview-image"
        @load="handleImageLoad"
      />
      
      <!-- 图片信息 -->
      <div class="preview-info">
        <span class="preview-counter">{{ currentIndex + 1 }} / {{ images.length }}</span>
      </div>
      
      <!-- 移动端滑动提示 -->
      <div class="swipe-hint">左右滑动切换图片</div>
    </div>
    
    <!-- 导航按钮 -->
    <button 
      class="nav-btn next-btn" 
      @click.stop="navigate(1)" 
      :disabled="currentIndex >= images.length - 1"
    >
      ›
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'

/**
 * 图片预览模态框组件
 * 功能：
 * - 点击图片放大预览
 * - 支持键盘左右键导航
 * - 支持鼠标滚轮导航
 * - 支持移动端左右滑动导航
 * - 点击空白处关闭
 * - 关闭按钮
 */

// Props定义
const props = defineProps<{
  visible: boolean
  images: string[] // 图片URL数组
  initialIndex?: number // 初始显示索引
}>()

// Emits定义
const emit = defineEmits<{
  (e: 'close'): void
}>()

// 响应式状态
const currentIndex = ref(0)
const previewImage = ref<HTMLImageElement | null>(null)
const startX = ref(0)
const startY = ref(0)
const isDragging = ref(false)

// 计算当前显示的图片URL
const currentImage = ref('')

// 监听图片数组和初始索引变化
watch(() => [props.images, props.initialIndex, props.visible], ([newImages, newInitialIndex, newVisible]) => {
  if (newVisible && newImages.length > 0) {
    // 重置当前索引
    currentIndex.value = newInitialIndex || 0
    updateCurrentImage()
  }
}, { deep: true })

// 更新当前显示的图片
const updateCurrentImage = () => {
  if (props.images.length > 0) {
    currentIndex.value = Math.max(0, Math.min(currentIndex.value, props.images.length - 1))
    currentImage.value = props.images[currentIndex.value]
  }
}

// 导航到上一张/下一张
const navigate = (direction: number) => {
  currentIndex.value += direction
  updateCurrentImage()
}

// 关闭模态框
const handleCloseModal = () => {
  emit('close')
}

// 处理键盘事件
const handleKeydown = (e: KeyboardEvent) => {
  if (!props.visible) return
  
  switch (e.key) {
    case 'ArrowLeft':
      navigate(-1)
      break
    case 'ArrowRight':
      navigate(1)
      break
    case 'Escape':
      handleCloseModal()
      break
  }
}

// 处理鼠标滚轮事件
const handleWheel = (e: WheelEvent) => {
  if (!props.visible) return
  
  e.preventDefault()
  if (e.deltaY > 0) {
    // 向下滚动，查看下一张
    navigate(1)
  } else {
    // 向上滚动，查看上一张
    navigate(-1)
  }
}

// 处理图片加载完成
const handleImageLoad = () => {
  // TODO: 主人~ 这里可以添加图片加载完成的动画效果
}

// 处理触摸开始
const handleTouchStart = (e: TouchEvent) => {
  startX.value = e.touches[0].clientX
  startY.value = e.touches[0].clientY
  isDragging.value = true
}

// 处理触摸移动
const handleTouchMove = (e: TouchEvent) => {
  if (!isDragging.value) return
  
  const currentX = e.touches[0].clientX
  const currentY = e.touches[0].clientY
  const diffX = currentX - startX.value
  const diffY = currentY - startY.value
  
  // 判断是水平滑动还是垂直滑动
  if (Math.abs(diffX) > Math.abs(diffY)) {
    e.preventDefault()
  }
}

// 处理触摸结束
const handleTouchEnd = (e: TouchEvent) => {
  if (!isDragging.value) return
  
  const endX = e.changedTouches[0].clientX
  const diffX = endX - startX.value
  
  // 滑动距离超过阈值才切换图片
  const SWIPE_THRESHOLD = 50
  if (Math.abs(diffX) > SWIPE_THRESHOLD) {
    if (diffX > 0) {
      // 向右滑动，查看上一张
      navigate(-1)
    } else {
      // 向左滑动，查看下一张
      navigate(1)
    }
  }
  
  isDragging.value = false
}

// 生命周期钩子
onMounted(() => {
  // 添加事件监听器
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('wheel', handleWheel, { passive: false })
  window.addEventListener('touchstart', handleTouchStart, { passive: true })
  window.addEventListener('touchmove', handleTouchMove, { passive: false })
  window.addEventListener('touchend', handleTouchEnd)
})

onUnmounted(() => {
  // 移除事件监听器
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('wheel', handleWheel)
  window.removeEventListener('touchstart', handleTouchStart)
  window.removeEventListener('touchmove', handleTouchMove)
  window.removeEventListener('touchend', handleTouchEnd)
})
</script>

<style scoped>
/* 图片预览模态框 */
.image-preview-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeIn 0.2s ease;
}

/* 淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 关闭按钮 */
.preview-close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  font-size: 32px;
  color: white;
  cursor: pointer;
  padding: 10px;
  z-index: 1001;
  transition: opacity 0.2s;
}

.preview-close-btn:hover {
  opacity: 0.8;
}

/* 导航按钮 */
.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0, 0, 0, 0.5);
  border: none;
  color: white;
  font-size: 48px;
  width: 60px;
  height: 60px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  z-index: 1001;
  transition: all 0.2s;
  user-select: none;
}

.nav-btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.8);
  transform: translateY(-50%) scale(1.1);
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.prev-btn {
  left: 20px;
}

.next-btn {
  right: 20px;
}

/* 图片容器 */
.preview-container {
  position: relative;
  max-width: 100%;
  max-height: 90vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  touch-action: pan-y;
}

/* 预览图片 */
.preview-image {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
  cursor: zoom-out;
  transition: transform 0.3s ease;
}

/* 图片信息 */
.preview-info {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  user-select: none;
}

/* 移动端滑动提示 */
.swipe-hint {
  position: absolute;
  bottom: 60px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12px;
  opacity: 0.7;
  user-select: none;
  animation: fadeInOut 2s ease-in-out infinite;
}

/* 淡入淡出动画 */
@keyframes fadeInOut {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.7;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .image-preview-modal {
    padding: 10px;
  }
  
  .preview-close-btn {
    top: 10px;
    right: 10px;
    font-size: 24px;
  }
  
  .nav-btn {
    font-size: 32px;
    width: 40px;
    height: 40px;
  }
  
  .prev-btn {
    left: 10px;
  }
  
  .next-btn {
    right: 10px;
  }
  
  .swipe-hint {
    display: block;
  }
}

@media (min-width: 769px) {
  .swipe-hint {
    display: none;
  }
}
</style>