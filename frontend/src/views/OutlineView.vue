<template>
  <div class="container" style="max-width: 100%;">
    <!-- 美化的标题区域 -->
    <div class="outline-header">
      <div class="edit-badge">✏️</div>
      <h1 class="outline-title">编辑大纲</h1>
      <p class="outline-subtitle">调整页面顺序，修改文案，打造完美内容 ✨</p>
      <div class="header-actions">
        <button class="btn-glass" @click="goBack">
          ← 上一步
        </button>
        <button class="btn-gradient" @click="startGeneration">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"></path><line x1="16" y1="8" x2="2" y2="22"></line><line x1="17.5" y1="15" x2="9" y2="15"></line></svg>
          开始生成图片
        </button>
      </div>
    </div>

    <div class="outline-grid">
      <div 
        v-for="(page, idx) in store.outline.pages" 
        :key="page.index"
        class="card outline-card"
        :draggable="true"
        @dragstart="onDragStart($event, idx)"
        @dragover.prevent="onDragOver($event, idx)"
        @drop="onDrop($event, idx)"
        :class="{ 'dragging-over': dragOverIndex === idx }"
      >
        <!-- 拖拽手柄 (改为右上角或更加隐蔽) -->
        <div class="card-top-bar">
          <div class="page-info">
             <span class="page-number">P{{ idx + 1 }}</span>
             <span class="page-type" :class="page.type">{{ getPageTypeName(page.type) }}</span>
          </div>
          
          <div class="card-controls">
            <div class="drag-handle" title="拖拽排序">
               <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="12" r="1"></circle><circle cx="9" cy="5" r="1"></circle><circle cx="9" cy="19" r="1"></circle><circle cx="15" cy="12" r="1"></circle><circle cx="15" cy="5" r="1"></circle><circle cx="15" cy="19" r="1"></circle></svg>
            </div>
            <button class="icon-btn" @click="deletePage(idx)" title="删除此页">
               <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
          </div>
        </div>

        <textarea
          v-model="page.content"
          class="textarea-paper"
          placeholder="在此输入文案..."
          @input="store.updatePage(page.index, page.content)"
        />
        
        <div class="word-count">{{ page.content.length }} 字</div>
      </div>

      <!-- 添加按钮卡片 -->
      <div class="card add-card-dashed" @click="addPage('content')">
        <div class="add-content">
          <div class="add-icon">+</div>
          <span>添加页面</span>
        </div>
      </div>
    </div>
    
    <div style="height: 100px;"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useGeneratorStore } from '../stores/generator'

const router = useRouter()
const store = useGeneratorStore()

const dragOverIndex = ref<number | null>(null)
const draggedIndex = ref<number | null>(null)

const getPageTypeName = (type: string) => {
  const names = {
    cover: '封面',
    content: '内容',
    summary: '总结'
  }
  return names[type as keyof typeof names] || '内容'
}

// 拖拽逻辑
const onDragStart = (e: DragEvent, index: number) => {
  draggedIndex.value = index
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.dropEffect = 'move'
  }
}

const onDragOver = (e: DragEvent, index: number) => {
  if (draggedIndex.value === index) return
  dragOverIndex.value = index
}

const onDrop = (e: DragEvent, index: number) => {
  dragOverIndex.value = null
  if (draggedIndex.value !== null && draggedIndex.value !== index) {
    store.movePage(draggedIndex.value, index)
  }
  draggedIndex.value = null
}

import { showDangerConfirm } from '../utils/dialog'

const deletePage = async (index: number) => {
  if (await showDangerConfirm('确定要删除这一页吗？这是一次不可逆的操作哦~', '删除页面')) {
    store.deletePage(index)
  }
}

const addPage = (type: 'cover' | 'content' | 'summary') => {
  store.addPage(type, '')
  // 滚动到底部
  nextTick(() => {
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
  })
}

const goBack = () => {
  router.back()
}

const startGeneration = () => {
  router.push('/generate')
}
</script>

<style scoped>
/* Header Layout - 居中少女风格 */
.outline-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  width: 100%;
  margin: 0 0 30px 0;
  gap: 10px;
}

/* 编辑徽章 */
.edit-badge {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFE0EC 0%, #F0E6FF 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  box-shadow: 0 10px 30px rgba(255, 133, 161, 0.2);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

/* 渐变标题 */
.outline-title {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #FF6B9D 0%, #C44569 50%, #8B5CF6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 8px 0 !important;
}

.outline-subtitle {
  font-size: 1rem;
  color: #6C6377;
  margin-bottom: 20px;
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
  gap: 6px;
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

/* 网格布局 */
.outline-grid {
  display: grid;
  /* 响应式列：最小宽度 300px (增大) */
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 32px; /* 增大间距 */
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px; /* 侧边留白 */
}

.outline-card {
  display: flex;
  flex-direction: column;
  padding: 24px; /* 增大内边距 */
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  border: none;
  border-radius: 20px; /* 更大的圆角 */
  background: white;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  min-height: 400px; /* 稍微增高 */
  position: relative;
  overflow: hidden; /* 防止内容溢出 */
}

.outline-card:hover {
  transform: translateY(-8px) scale(1.01);
  box-shadow: 0 15px 40px rgba(159, 134, 192, 0.15); /* 少女风阴影 */
  z-index: 10;
}

.outline-card.dragging-over {
  border: 2px dashed #FF85A1;
  background: #FFF0F5;
  opacity: 0.9;
}

/* 顶部栏 */
.card-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #eee;
}

.page-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-number {
  font-size: 16px;
  font-weight: 800;
  color: #DDD;
  font-family: 'Inter', sans-serif;
}

.page-type {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 8px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.page-type.cover { color: #FF4D4F; background: #FFF1F0; }
.page-type.content { color: #8c8c8c; background: #fafafa; border: 1px solid #eee; }
.page-type.summary { color: #52C41A; background: #F6FFED; }

.card-controls {
  display: flex;
  gap: 10px;
  opacity: 0.2; /* 默认更淡 */
  transition: opacity 0.3s;
}
.outline-card:hover .card-controls { opacity: 1; }

.drag-handle {
  cursor: grab;
  padding: 4px;
  border-radius: 6px;
  color: #ccc;
  transition: all 0.2s;
}
.drag-handle:hover {
  background: #f5f5f5;
  color: #666;
}
.drag-handle:active { cursor: grabbing; }

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #ccc;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s;
}
.icon-btn:hover { 
  color: #FF4D4F; 
  background: #FFF1F0;
}

/* 文本区域 */
.textarea-paper {
  flex: 1;
  width: 100%;
  border: none;
  background: transparent;
  padding: 0;
  font-size: 17px;
  line-height: 1.8;
  color: #4A4063;
  resize: none;
  font-family: inherit;
  margin-bottom: 15px;
}

.textarea-paper::placeholder {
  color: #ccc;
}
.textarea-paper:focus {
  outline: none;
}

.word-count {
  text-align: right;
  font-size: 12px;
  color: #E0E0E0;
  margin-top: auto;
  font-weight: 600;
}

/* 添加卡片 */
.add-card-dashed {
  border: 3px dashed #E0E0E0;
  background: rgba(255,255,255,0.3);
  box-shadow: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  min-height: 400px;
  color: #ccc;
  border-radius: 20px;
  transition: all 0.3s;
}

.add-card-dashed:hover {
  border-color: #FF85A1;
  color: #FF85A1;
  background: rgba(255, 133, 161, 0.05);
  transform: translateY(-4px);
}

.add-content {
  text-align: center;
}

.add-icon {
  font-size: 40px;
  font-weight: 300;
  margin-bottom: 12px;
  line-height: 1;
}

/* 手机端优化 */
@media (max-width: 768px) {
  /* 容器调整 */
  .container {
    padding: 16px !important;
  }
  
  /* 页面标题 */
  h1 {
    font-size: 1.8rem !important;
  }
  
  /* 副标题 */
  h2 {
    font-size: 1.4rem !important;
  }
  
  /* 大纲网格布局 */
  .outline-grid {
    grid-template-columns: 1fr !important;
    gap: 12px !important;
    padding: 0 !important;
  }
  
  /* 大纲卡片 */
  .outline-card {
    padding: 16px !important;
    margin-bottom: 0 !important;
    min-height: 300px !important;
  }
  
  /* 文本区域 */
  .textarea-paper {
    font-size: 14px !important;
    line-height: 1.6 !important;
    margin-bottom: 12px !important;
  }
  
  /* 卡片控制按钮 */
  .card-controls {
    opacity: 1 !important;
  }
  
  /* 页面类型标签 */
  .page-type {
    padding: 3px 8px !important;
    font-size: 10px !important;
  }
  
  /* 添加卡片 */
  .add-card-dashed {
    min-height: 300px !important;
  }
  
  /* 添加图标 */
  .add-icon {
    font-size: 40px !important;
  }
  
  /* 字数统计 */
  .word-count {
    font-size: 11px !important;
  }
  
  /* 大纲头部 */
  .outline-header {
    margin: 0 0 20px 0 !important;
    gap: 8px !important;
  }
  
  /* 头部操作区 */
  .header-actions {
    gap: 12px !important;
    flex-direction: column !important;
    align-items: stretch !important;
  }
  
  .btn-glass,
  .btn-gradient {
    justify-content: center !important;
    padding: 10px 20px !important;
  }
}

/* 超小屏幕优化 */
@media (max-width: 480px) {
  /* 容器调整 */
  .container {
    padding: 12px !important;
  }
  
  /* 大纲卡片 */
  .outline-card {
    min-height: 250px !important;
  }
  
  /* 添加卡片 */
  .add-card-dashed {
    min-height: 250px !important;
  }
}
</style>
