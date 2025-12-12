<template>
  <!-- 图片画廊模态框 -->
  <div v-if="visible && record" class="modal-fullscreen" @click="$emit('close')">
    <div class="modal-body" @click.stop>
      <!-- 头部区域 -->
      <div class="modal-header">
        <div style="flex: 1;">
          <!-- 标题区域 -->
          <div class="title-section">
            <h3
              class="modal-title"
              :class="{ 'collapsed': !titleExpanded && record.title.length > 80 }"
            >
              {{ record.title }}
            </h3>
            <button
              v-if="record.title.length > 80"
              class="title-expand-btn"
              @click="titleExpanded = !titleExpanded"
            >
              {{ titleExpanded ? '收起' : '展开' }}
            </button>
          </div>

          <div class="modal-meta">
            <span>{{ record.outline.pages.length }} 张图片 · {{ formattedDate }}</span>
            <button
              class="view-outline-btn"
              @click="$emit('showOutline')"
              title="查看完整大纲"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
              </svg>
              查看大纲
            </button>
          </div>
        </div>

        <div class="header-actions">
          <button class="btn download-btn" @click="$emit('downloadAll')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            打包下载
          </button>
          <button class="close-icon" @click="$emit('close')">×</button>
        </div>
      </div>

      <!-- 图片网格 -->
      <div class="modal-gallery-grid">
        <div
          v-for="(img, idx) in record.images.generated"
          :key="idx"
          class="modal-img-item"
        >
          <div
            class="modal-img-preview"
            v-if="img"
            :class="{ 'regenerating': regeneratingImages.has(idx) }"
          >
            <img
              :src="getImageUrl(record.images.task_id, img, false)"
              loading="lazy"
              decoding="async"
              @click="openImagePreview(idx)"
              style="cursor: pointer;"
            />
          </div>
          <div class="placeholder" v-else>Waiting...</div>

          <div class="img-footer">
            <span>Page {{ idx + 1 }}</span>
            <span
              v-if="img"
              class="download-link"
              @click="$emit('download', img, idx)"
            >
              下载
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 大图预览模态框 -->
  <ImagePreviewModal 
    :visible="previewVisible" 
    :images="generatedImages" 
    :initial-index="previewInitialIndex"
    @close="closeImagePreview"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { getImageUrl } from '../../api'
import ImagePreviewModal from '../ImagePreviewModal.vue'

/**
 * 图片画廊模态框组件
 *
 * 功能：
 * - 展示历史记录的所有生成图片（保持原样式）
 * - 支持重新生成单张图片
 * - 支持下载单张/全部图片
 * - 可展开查看完整大纲
 * - 支持点击图片放大预览（使用与生图页面相同的模态框组件）
 */

// 定义记录类型
interface ViewingRecord {
  id: string
  title: string
  updated_at: string
  outline: {
    raw: string
    pages: Array<{ type: string; content: string }>
  }
  images: {
    task_id: string
    generated: string[]
  }
}

// 定义 Props
const props = defineProps<{
  visible: boolean
  record: ViewingRecord | null
  regeneratingImages: Set<number>
}>()

// 定义 Emits
defineEmits<{
  (e: 'close'): void
  (e: 'showOutline'): void
  (e: 'downloadAll'): void
  (e: 'download', filename: string, index: number): void
  (e: 'regenerate', index: number): void
}>()

// 标题展开状态
const titleExpanded = ref(false)

// 图片预览相关
const previewVisible = ref(false)
const previewInitialIndex = ref(0)

// 计算所有已生成图片的URL数组
const generatedImages = computed(() => {
  if (!props.record) return []
  return props.record.images.generated
    .filter(img => img)
    .map(img => getImageUrl(props.record.images.task_id, img, false))
})

// 打开图片预览
const openImagePreview = (index: number) => {
  previewInitialIndex.value = index
  previewVisible.value = true
}

// 关闭图片预览
const closeImagePreview = () => {
  previewVisible.value = false
}

// 格式化日期
const formattedDate = computed(() => {
  if (!props.record) return ''
  const d = new Date(props.record.updated_at)
  return `${d.getMonth() + 1}/${d.getDate()}`
})
</script>

<style scoped>
/* 全屏模态框遮罩 */
.modal-fullscreen {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

/* 模态框主体 */
.modal-body {
  background: white;
  width: 100%;
  max-width: 1000px;
  height: 90vh;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 头部区域 */
.modal-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-shrink: 0;
  gap: 20px;
}

/* 标题区域 */
.title-section {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 4px;
}

.modal-title {
  flex: 1;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.4;
  color: #1a1a1a;
  word-break: break-word;
  transition: max-height 0.3s ease;
}

.modal-title.collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.title-expand-btn {
  flex-shrink: 0;
  padding: 2px 8px;
  background: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  color: #666;
  transition: all 0.2s;
  margin-top: 2px;
}

.title-expand-btn:hover {
  background: var(--primary, #ff2442);
  color: white;
}

/* 元信息 */
.modal-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

/* 查看大纲按钮 */
.view-outline-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #495057;
  transition: all 0.2s;
}

.view-outline-btn:hover {
  background: var(--primary, #ff2442);
  color: white;
  border-color: var(--primary, #ff2442);
}

/* 头部操作区 */
.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.download-btn {
  padding: 8px 16px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.close-icon {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  line-height: 1;
}

.close-icon:hover {
  color: #333;
}

/* 图片网格 - 保持原样式 */
.modal-gallery-grid {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

/* 单个图片项 - 保持原样式 */
.modal-img-item {
  display: flex;
  flex-direction: column;
}

/* 图片预览容器 - 保持原样式 */
.modal-img-preview {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  overflow: hidden;
  border-radius: 8px;
  contain: layout style paint;
}

/* 图片 - 保持原样式，仅添加cursor指针 */
.modal-img-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 悬浮遮罩 - 保持原样式 */
.modal-img-overlay {
  display: none !important;
}

.modal-img-preview:hover .modal-img-overlay { display: none !important; }

/* 重绘中状态 - 保持原样式 */
.modal-img-preview.regenerating .modal-img-overlay { display: none !important; }

.modal-img-preview.regenerating .regenerate-icon { animation: none; }

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 遮罩层按钮 - 保持原样式 */
.modal-overlay-btn { display: none !important; }

.modal-overlay-btn:hover { display: none !important; }

.modal-overlay-btn:disabled { display: none !important; }

/* 占位符 - 保持原样式 */
.placeholder {
  width: 100%;
  aspect-ratio: 3/4;
  background: #f5f5f5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
}

/* 图片底部信息 - 保持原样式 */
.img-footer {
  margin-top: 8px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}

.download-link {
  cursor: pointer;
  color: var(--primary, #ff2442);
  transition: opacity 0.2s;
}

.download-link:hover {
  opacity: 0.7;
}

/* 响应式 - 优化手机端显示 */
@media (max-width: 768px) {
  /* 全屏模态框 */
  .modal-fullscreen {
    padding: 10px;
    align-items: flex-start;
  }
  
  /* 模态框主体 */
  .modal-body {
    height: 95vh;
  }

  /* 模态框头部 */
  .modal-header {
    padding: 12px;
    gap: 12px;
    flex-direction: column;
    align-items: stretch;
  }
  
  /* 标题区域 */
  .title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  /* 模态框标题 */
  .modal-title {
    font-size: 16px;
    line-height: 1.3;
  }
  
  /* 元信息 */
  .modal-meta {
    font-size: 11px;
    gap: 8px;
    margin-top: 4px;
  }
  
  /* 头部操作区 */
  .header-actions {
    justify-content: flex-end;
  }
  
  /* 下载按钮 */
  .download-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
  
  /* 图片网格 */
  .modal-gallery-grid {
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 12px;
  }
  
  /* 图片项 */
  .modal-img-item {
    max-width: 320px;
    margin: 0 auto;
    gap: 6px;
  }
  
  /* 图片预览容器 */
  .modal-img-preview {
    border-radius: 6px;
  }
  
  /* 遮罩层按钮 */
  .modal-overlay-btn {
    padding: 6px 12px;
    font-size: 11px;
    gap: 4px;
  }
  
  /* 图片底部信息 */
  .img-footer {
    font-size: 11px;
    padding: 8px 10px;
  }
  
  /* 关闭按钮 */
  .close-icon {
    font-size: 24px;
    padding: 6px;
    top: 12px;
    right: 12px;
  }
}
</style>
