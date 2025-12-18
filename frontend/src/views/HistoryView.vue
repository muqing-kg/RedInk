<template>
  <div class="container" style="max-width: 1200px;">

    <!-- Header Area -->
    <div class="page-header" style="justify-content: center; position: relative; margin-bottom: 20px; padding-bottom: 0;">
      <h1 class="page-title" style="text-align: center; margin: 0; font-size: 32px;">我的创作</h1>
    </div>

    <!-- 过期警告 Banner -->
    <div v-if="hasUrgentExpiry" class="expiry-banner fade-in">
      <div class="banner-content">
        <span class="banner-icon">⏰</span>
        <span>您有 {{ urgentCount }} 个作品即将过期（剩余不足3天），请及时下载保存，以免数据丢失！</span>
      </div>
    </div>



    <!-- Stats Overview -->
    <StatsOverview v-if="stats" :stats="stats" />

    <!-- Toolbar: Tabs & Search -->
    <div class="toolbar-wrapper">
      <div class="tabs-container" style="margin-bottom: 0; border-bottom: none;">
        <div
          class="tab-item"
          :class="{ active: currentTab === 'all' }"
          @click="switchTab('all')"
        >
          全部
        </div>
        <div
          class="tab-item"
          :class="{ active: currentTab === 'completed' }"
          @click="switchTab('completed')"
        >
          已完成
        </div>
        <div
          class="tab-item"
          :class="{ active: currentTab === 'draft' }"
          @click="switchTab('draft')"
        >
          草稿箱
        </div>
      </div>

      <div class="search-mini">
        <svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索标题..."
          @keyup.enter="handleSearch"
        />
      </div>
    </div>

    <!-- Content Area -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
    </div>

    <div v-else-if="records.length === 0" class="empty-state-large">
      <div class="empty-img">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
      </div>
      <h3>暂无相关记录</h3>
      <p class="empty-tips">去创建一个新的作品吧</p>
    </div>

    <div v-else class="gallery-grid">
      <GalleryCard
        v-for="record in records"
        :key="record.id"
        :record="record"
        @preview="viewImages"
        @edit="loadRecord"
        @delete="confirmDelete"

      />
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination-wrapper">
       <button class="page-btn" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Previous</button>
       <span class="page-indicator">{{ currentPage }} / {{ totalPages }}</span>
       <button class="page-btn" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">Next</button>
    </div>

    <!-- Image Viewer Modal -->
    <ImageGalleryModal
      v-if="viewingRecord"
      :visible="!!viewingRecord"
      :record="viewingRecord"
      :regeneratingImages="regeneratingImages"
      @close="closeGallery"
      @showOutline="showOutlineModal = true"
      @regenerate="regenerateHistoryImage"
      @downloadAll="downloadAllImages"
      @download="downloadImage"
    />

    <!-- 大纲查看模态框 -->
    <OutlineModal
      v-if="showOutlineModal && viewingRecord"
      :visible="showOutlineModal"
      :pages="viewingRecord.outline.pages"
      @close="showOutlineModal = false"
    />



  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  getHistoryList,
  getHistoryStats,
  searchHistory,
  deleteHistory,
  getHistory,
  type HistoryRecord,
  regenerateImage as apiRegenerateImage,
  updateHistory,
  getImageUrl,
  downloadFile,

} from '../api'
import { useGeneratorStore } from '../stores/generator'

// 引入组件
import StatsOverview from '../components/history/StatsOverview.vue'
import GalleryCard from '../components/history/GalleryCard.vue'
import ImageGalleryModal from '../components/history/ImageGalleryModal.vue'
import OutlineModal from '../components/history/OutlineModal.vue'
import { showSuccess, showError, showDangerConfirm } from '../utils/dialog'

const router = useRouter()
const route = useRoute()
const store = useGeneratorStore()

// 数据状态
const records = ref<HistoryRecord[]>([])
const loading = ref(false)
const stats = ref<any>(null)
const currentTab = ref('all')
const searchKeyword = ref('')
const currentPage = ref(1)
const totalPages = ref(1)

// 计算属性
const urgentCount = computed(() => {
  return records.value.filter(r => r.remaining_days !== undefined && r.remaining_days >= 0 && r.remaining_days <= 3).length
})

const hasUrgentExpiry = computed(() => urgentCount.value > 0)


// 查看器状态
const viewingRecord = ref<any>(null)
const regeneratingImages = ref<Set<number>>(new Set())
const showOutlineModal = ref(false)

/**
 * 加载历史记录列表
 */
async function loadData() {
  loading.value = true
  try {
    let statusFilter = currentTab.value === 'all' ? undefined : currentTab.value
    const res = await getHistoryList(currentPage.value, 12, statusFilter)
    if (res.success) {
      records.value = res.records
      totalPages.value = res.total_pages
    }
  } catch(e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

/**
 * 续期
 */


/**
 * 加载统计数据
 */
async function loadStats() {
  try {
    const res = await getHistoryStats()
    if (res.success) stats.value = res
  } catch(e) {}
}

/**
 * 切换标签页
 */
function switchTab(tab: string) {
  currentTab.value = tab
  currentPage.value = 1
  loadData()
}

/**
 * 搜索历史记录
 */
async function handleSearch() {
  if (!searchKeyword.value.trim()) {
    loadData()
    return
  }
  loading.value = true
  try {
    const res = await searchHistory(searchKeyword.value)
    if (res.success) {
      records.value = res.records
      totalPages.value = 1
    }
  } catch(e) {} finally {
    loading.value = false
  }
}

/**
 * 加载记录并跳转到编辑页
 */
async function loadRecord(id: string) {
  const res = await getHistory(id)
  if (res.success && res.record) {
    store.setTopic(res.record.title)
    store.setOutline(res.record.outline.raw, res.record.outline.pages)
    store.recordId = res.record.id
    
    const pagesCount = res.record.outline.pages.length
    const generatedArr = res.record.images.generated || []
    
    if (res.record.images.task_id) {
      store.taskId = res.record.images.task_id
      
      // 根据 generated 数组的内容判断状态
      // 空字符串表示待生成，有文件名表示已完成
      store.images = res.record.outline.pages.map((_, idx) => {
        const filename = generatedArr[idx]
        // filename 存在且不为空字符串才是完成状态
        const isDone = filename && filename !== ''
        return {
          index: idx,
          url: isDone ? getImageUrl(res.record!.images.task_id!, filename, false) : '',
          status: isDone ? 'done' : 'pending',
          retryable: !isDone
        }
      })
      
      // 初始化进度状态
      const doneCount = store.images.filter(img => img.status === 'done').length
      store.progress = {
        current: doneCount,
        total: pagesCount,
        status: doneCount === pagesCount ? 'done' : (doneCount > 0 ? 'generating' : 'idle')
      }
    } else {
      // 没有 task_id，初始化空状态
      store.images = res.record.outline.pages.map((_, idx) => ({
        index: idx,
        url: '',
        status: 'pending',
        retryable: true
      }))
      store.progress = {
        current: 0,
        total: pagesCount,
        status: 'idle'
      }
    }
    
    router.push('/outline')
  }
}

/**
 * 查看图片
 */
async function viewImages(id: string) {
  const res = await getHistory(id)
  if (res.success) viewingRecord.value = res.record
}

/**
 * 关闭图片查看器
 */
function closeGallery() {
  viewingRecord.value = null
  showOutlineModal.value = false
}

/**
 * 确认删除
 */
async function confirmDelete(record: any) {
  if(await showDangerConfirm('确定删除吗？', '删除作品')) {
    await deleteHistory(record.id)
    loadData()
    loadStats()
    showSuccess('删除成功')
  }
}

/**
 * 切换页码
 */
function changePage(p: number) {
  currentPage.value = p
  loadData()
}

/**
 * 重新生成历史记录中的图片
 */
async function regenerateHistoryImage(index: number) {
  if (!viewingRecord.value || !viewingRecord.value.images.task_id) {
    showError('无法重新生成：缺少任务信息')
    return
  }

  const page = viewingRecord.value.outline.pages[index]
  if (!page) return

  regeneratingImages.value.add(index)

  try {
    const context = {
      fullOutline: viewingRecord.value.outline.raw || '',
      userTopic: viewingRecord.value.title || ''
    }

    const result = await apiRegenerateImage(
      viewingRecord.value.images.task_id,
      page,
      true,
      context
    )

    if (result.success && result.image_url) {
      const filename = result.image_url.split('/').pop() || ''
      viewingRecord.value.images.generated[index] = filename

      // 刷新图片
      const timestamp = Date.now()
      const imgElements = document.querySelectorAll(`img[src*="${viewingRecord.value.images.task_id}/${filename}"]`)
      imgElements.forEach(img => {
        const isThumbnail = (img as HTMLImageElement).src.includes('thumbnail=true')
        const newUrl = getImageUrl(viewingRecord.value!.images.task_id || '', filename, isThumbnail)
        ;(img as HTMLImageElement).src = `${newUrl}&t=${timestamp}`
      })

      await updateHistory(viewingRecord.value.id, {
        images: {
          task_id: viewingRecord.value.images.task_id,
          generated: viewingRecord.value.images.generated
        }
      })

      regeneratingImages.value.delete(index)
    } else {
      regeneratingImages.value.delete(index)
      showError('重新生成失败: ' + (result.error || '未知错误'))
    }
  } catch (e) {
    regeneratingImages.value.delete(index)
    showError('重新生成失败: ' + String(e))
  }
}



// ...

/**
 * 下载单张图片
 */
async function downloadImage(filename: string, index: number) {
  if (!viewingRecord.value) return
  try {
    const url = `/api/images/${viewingRecord.value.images.task_id}/${filename}?thumbnail=false`
    await downloadFile(url, `page_${index + 1}.png`)
  } catch (e: any) {
    console.error('下载失败:', e)
  }
}

/**
 * 打包下载所有图片
 */
async function downloadAllImages() {
  if (!viewingRecord.value) return
  try {
    const url = `/api/history/${viewingRecord.value.id}/download`
    const title = viewingRecord.value.title || 'images'
    await downloadFile(url, `${title}.zip`)
  } catch (e: any) {
    console.error('下载失败:', e)
  }
}

/**
 * 扫描所有任务并同步
 */


onMounted(async () => {
  await loadData()
  await loadStats()

  // 检查路由参数，如果有 ID 则自动打开图片查看器
  if (route.params.id) {
    await viewImages(route.params.id as string)
  }
})

// 监听路由变化，确保页面切换时重新加载数据
watch(() => route.path, async (newPath, oldPath) => {
  // 当路由变化时，重置状态并重新加载数据
  currentTab.value = 'all'
  currentPage.value = 1
  searchKeyword.value = ''
  await loadData()
  await loadStats()
})
</script>

<style scoped>


/* Toolbar */
.toolbar-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0;
  flex-wrap: wrap;
  gap: 12px;
}

.search-mini {
  position: relative;
  width: 240px;
  margin-bottom: 10px;
}

.search-mini input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  border-radius: 100px;
  border: 1px solid var(--border-color);
  font-size: 14px;
  background: white;
  transition: border-color 0.2s, box-shadow 0.2s;
}

/* 手机端优化 */
@media (max-width: 768px) {
  /* 调整工具栏布局为垂直排列 */
  .toolbar-wrapper {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
    margin-bottom: 16px;
  }
  
  /* 标签页容器调整 */
  .tabs-container {
    display: flex;
    justify-content: center;
    width: 100%;
  }
  
  /* 标签页样式调整 */
  .tab-item {
    padding: 8px 16px !important;
    font-size: 13px !important;
  }
  
  /* 搜索框宽度自适应 */
  .search-mini {
    width: 100%;
    margin-bottom: 0;
  }
  
  /* 搜索框输入调整 */
  .search-mini input {
    padding: 10px 16px 10px 40px;
    font-size: 13px;
  }
  
  /* 画廊网格调整 */
  .gallery-grid {
    grid-template-columns: 1fr !important;
    gap: 12px !important;
    margin-bottom: 24px !important;
  }
  
  /* 历史卡片大小调整 */
  .gallery-card {
    max-width: 320px !important;
    margin: 0 auto !important;
  }
  
  /* 过期横幅调整 */
  .expiry-banner {
    padding: 10px 16px !important;
    font-size: 13px !important;
  }
  
  /* 页面标题调整 */
  .page-title {
    font-size: 1.8rem !important;
  }
  

}

.search-mini input:focus {
  border-color: var(--primary);
  outline: none;
  box-shadow: 0 0 0 3px var(--primary-light);
}

.search-mini .icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #ccc;
}

/* Gallery Grid */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 40px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  background: white;
  border-radius: 6px;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Empty State */
.empty-state-large {
  text-align: center;
  padding: 80px 0;
  color: var(--text-sub);
}

.empty-img {
  font-size: 64px;
  opacity: 0.5;
}

.empty-state-large .empty-tips {
  margin-top: 10px;
  color: var(--text-placeholder);
}

/* Expiry Banner */
.expiry-banner {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
  padding: 12px 24px;
  border-radius: 8px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  animation: slideDown 0.3s ease;
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
}

.banner-icon {
  font-size: 18px;
}

@keyframes slideDown {
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.fade-in {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
