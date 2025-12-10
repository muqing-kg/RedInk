<template>
  <Teleport to="body">
    <Transition name="dialog-fade">
      <div v-if="visible" class="dialog-overlay" @click.self="handleOverlayClick">
        <Transition name="dialog-zoom">
          <div v-if="visible" class="dialog-container" :class="typeClass">
            <!-- 图标 -->
            <div class="dialog-icon" :class="typeClass">
              <!-- 成功图标 -->
              <svg v-if="type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M9 12l2 2 4-4"></path>
              </svg>
              <!-- 错误图标 -->
              <svg v-else-if="type === 'error'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
              </svg>
              <!-- 警告图标 -->
              <svg v-else-if="type === 'warning'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              <!-- 确认图标 -->
              <svg v-else-if="type === 'confirm'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              <!-- 输入图标 -->
              <svg v-else-if="type === 'prompt'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              <!-- 信息图标 -->
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
            </div>

            <!-- 标题 -->
            <h3 class="dialog-title">{{ title }}</h3>

            <!-- 内容 -->
            <p class="dialog-message">{{ message }}</p>

            <!-- 输入框 -->
            <div v-if="showInput" class="dialog-input-wrapper">
              <input 
                ref="inputRef"
                v-model="inputText" 
                class="dialog-input" 
                :placeholder="inputPlaceholder"
                @keyup.enter="handleConfirm"
              />
            </div>

            <!-- 按钮组 -->
            <div class="dialog-buttons">
              <button 
                v-if="showCancel" 
                class="dialog-btn dialog-btn-cancel"
                @click="handleCancel"
              >
                {{ cancelText }}
              </button>
              <button 
                class="dialog-btn dialog-btn-confirm"
                :class="confirmBtnClass"
                @click="handleConfirm"
              >
                {{ confirmText }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, nextTick, watch } from 'vue'

interface Props {
  visible: boolean
  type?: 'success' | 'error' | 'warning' | 'confirm' | 'info' | 'prompt'
  title?: string
  message: string
  showCancel?: boolean
  confirmText?: string
  cancelText?: string
  showInput?: boolean
  inputPlaceholder?: string
  inputValue?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'info',
  title: '提示',
  showCancel: false,
  confirmText: '确定',
  cancelText: '取消',
  showInput: false,
  inputPlaceholder: '',
  inputValue: ''
})

const emit = defineEmits<{
  (e: 'confirm', value?: string): void
  (e: 'cancel'): void
  (e: 'close'): void
}>()

const inputText = ref(props.inputValue)
const inputRef = ref<HTMLInputElement | null>(null)

// 监听 visible 变化，当显示且为输入模式时，自动聚焦
watch(() => props.visible, (val) => {
  if (val && props.showInput) {
    inputText.value = props.inputValue // 重置值
    nextTick(() => {
      inputRef.value?.focus()
    })
  }
})

const typeClass = computed(() => `type-${props.type}`)

const confirmBtnClass = computed(() => {
  if (props.type === 'error' || props.type === 'warning') {
    return 'danger'
  }
  return ''
})

function handleConfirm() {
  emit('confirm', props.showInput ? inputText.value : undefined)
  emit('close')
}

function handleCancel() {
  emit('cancel')
  emit('close')
}

function handleOverlayClick() {
  if (!props.showCancel) {
    handleConfirm()
  }
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.dialog-container {
  background: white;
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 400px;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.dialog-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.dialog-icon svg {
  width: 36px;
  height: 36px;
}

.dialog-icon.type-success {
  background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
  color: white;
}

.dialog-icon.type-error {
  background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
  color: white;
}

.dialog-icon.type-warning {
  background: linear-gradient(135deg, #faad14 0%, #ffc53d 100%);
  color: white;
}

.dialog-icon.type-confirm {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: white;
}

.dialog-icon.type-info {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: white;
}

.dialog-icon.type-prompt {
  background: linear-gradient(135deg, #FF85A1 0%, #FFccd5 100%);
  color: white;
}

.dialog-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 12px;
}

.dialog-message {
  font-size: 15px;
  color: #666;
  margin: 0 0 28px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-line;
}

.dialog-input-wrapper {
  margin-bottom: 24px;
}

.dialog-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #EEE;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  color: #333;
}

.dialog-input:focus {
  border-color: #FF85A1;
  background: #FFF0F5;
}

.dialog-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.dialog-btn {
  padding: 10px 28px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  outline: none;
  min-width: 100px;
}

.dialog-btn-cancel {
  background: #f5f5f5;
  color: #666;
}

.dialog-btn-cancel:hover {
  background: #e8e8e8;
  color: #333;
}

.dialog-btn-confirm {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: white;
}

.dialog-btn-confirm:hover {
  background: linear-gradient(135deg, #096dd9 0%, #1890ff 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.35);
}

.dialog-btn-confirm.danger {
  background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
}

.dialog-btn-confirm.danger:hover {
  background: linear-gradient(135deg, #f5222d 0%, #ff4d4f 100%);
  box-shadow: 0 4px 12px rgba(255, 77, 79, 0.35);
}

/* 动画 */
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.25s ease;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog-zoom-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.dialog-zoom-leave-active {
  transition: all 0.2s ease;
}

.dialog-zoom-enter-from {
  opacity: 0;
  transform: scale(0.85);
}

.dialog-zoom-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
