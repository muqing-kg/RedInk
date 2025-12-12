<template>
  <!-- 统计概览卡片 -->
  <div class="stats-overview" v-if="stats">
    <div class="stat-box">
      <div class="stat-icon-circle blue">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
          <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
      </div>
      <div class="stat-content">
        <h4>总作品数</h4>
        <div class="number">{{ stats.total || 0 }}</div>
      </div>
    </div>

    <div class="stat-box">
      <div class="stat-icon-circle green">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
      </div>
      <div class="stat-content">
        <h4>已完成</h4>
        <div class="number">{{ stats.by_status?.completed || 0 }}</div>
      </div>
    </div>

    <div class="stat-box">
      <div class="stat-icon-circle orange">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 20h9"></path>
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
        </svg>
      </div>
      <div class="stat-content">
        <h4>草稿箱</h4>
        <div class="number">{{ stats.by_status?.draft || 0 }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 历史记录统计概览组件
 *
 * 显示三个统计卡片：
 * - 总作品数
 * - 已完成数量
 * - 草稿箱数量
 */

// 定义 Props
interface Stats {
  total?: number
  by_status?: {
    completed?: number
    draft?: number
    generating?: number
  }
}

defineProps<{
  stats: Stats | null
}>()
</script>

<style scoped>
/* 统计概览容器 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

/* 单个统计卡片 */
.stat-box {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: white;
  border-radius: 24px;
  border: 4px solid #FFF0F5;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(159, 134, 192, 0.05);
}

.stat-box:hover {
  box-shadow: 0 15px 35px rgba(255, 133, 161, 0.15);
  transform: translateY(-5px);
  border-color: #FFD6E0;
}

/* 图标圆圈 */
.stat-icon-circle {
  width: 56px;
  height: 56px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s;
  position: relative;
  z-index: 1;
}

/* 装饰性背景球 */
.stat-box::before {
  content: '';
  position: absolute;
  top: -20px;
  right: -20px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  opacity: 0.2;
  transition: all 0.5s;
}
.stat-box:hover::before {
  transform: scale(1.5);
  opacity: 0.3;
}

/* 蓝色 - 总作品数 -> 改为梦幻紫 */
.stat-icon-circle.blue {
  background: #F3E8FF;
  color: #9F86C0;
}
.stat-box:has(.blue)::before { background: #E7C6FF; }

/* 绿色 - 已完成 -> 改为薄荷绿 */
.stat-icon-circle.green {
  background: #E0F2F1;
  color: #4DB6AC;
}
.stat-box:has(.green)::before { background: #B2DFDB; }

/* 橙色 - 草稿箱 -> 改为蜜桃粉 */
.stat-icon-circle.orange {
  background: #FFE4E6;
  color: #FB7185;
}
.stat-box:has(.orange)::before { background: #FECDD3; }

/* 统计内容 */
.stat-content h4 {
  font-size: 14px;
  font-weight: 700;
  color: #8D84A3;
  margin: 0 0 6px 0;
  letter-spacing: 0.5px;
}

.stat-content .number {
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(45deg, #4A4063, #9F86C0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1;
  font-family: 'Quicksand', sans-serif;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .stat-box {
    padding: 16px 20px;
  }

  .stat-content .number {
    font-size: 24px;
  }
}
</style>
