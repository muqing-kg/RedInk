<template>
  <div class="container">
    <div class="page-header" style="flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 40px;">
      <h1 class="page-title" style="margin-bottom: 10px;">系统设置</h1>
      <p class="page-subtitle">配置文本生成和图片生成的 API 服务</p>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>加载配置中...</p>
    </div>

    <div v-else class="settings-container">
      <!-- 标签页导航 -->
      <div class="settings-tabs">
        <div 
          v-for="tab in tabs" 
          :key="tab.key"
          class="tab-item"
          :class="{ 'active': activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </div>
      </div>
      
      <!-- 全局配置标签页 -->
      <div v-if="activeTab === 'global'" class="tab-content">
        <!-- 文本生成配置（全局） -->
        <div class="card card-global">
          <div class="section-header">
            <div>
              <h2 class="section-title">文本生成配置</h2>
              <p class="section-desc">用于生成小红书图文大纲</p>
            </div>
            <div v-if="isAdmin">
              <button class="btn btn-small" @click="openAddTextModal">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                添加
              </button>
            </div>
          </div>

          <!-- 服务商列表表格 -->
          <ProviderTable
            :providers="textConfig.providers"
            :activeProvider="textConfig.active_provider"
            :is-admin="isAdmin"
            :disable-activation="personalConfig.isTextPersonalEnabled.value"
            @activate="activateTextProvider"
            @edit="openEditTextModal"
            @delete="deleteTextProvider"
            @test="testTextProviderInList"
          />
        </div>

        <!-- 图片生成配置（全局） -->
        <div class="card card-global">
          <div class="section-header">
            <div>
              <h2 class="section-title">图片生成配置</h2>
              <p class="section-desc">用于生成小红书配图</p>
            </div>
            <div v-if="isAdmin">
              <button class="btn btn-small" @click="openAddImageModal">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                添加
              </button>
            </div>
          </div>

          <!-- 服务商列表表格 -->
          <ProviderTable
            :providers="imageConfig.providers"
            :activeProvider="imageConfig.active_provider"
            :is-admin="isAdmin"
            :disable-activation="personalConfig.isImagePersonalEnabled.value"
            @activate="activateImageProvider"
            @edit="openEditImageModal"
            @delete="deleteImageProvider"
            @test="testImageProviderInList"
          />
        </div>
      </div>
      
      <!-- 用户管理标签页 -->
      <div v-if="activeTab === 'users'" class="tab-content">
        <div class="card">
          <div class="section-header">
            <div>
              <h2 class="section-title">用户管理</h2>
              <p class="section-desc">管理员查看并修改用户信息</p>
            </div>
            <div>
              <button class="btn btn-small" @click="loadUsers" :disabled="userLoading">
                {{ userLoading ? '加载中...' : '刷新' }}
              </button>
            </div>
          </div>
          <table style="width:100%; border-collapse:collapse;">
            <thead>
              <tr>
                <th style="text-align:left; padding:8px;">用户名</th>
                <th style="text-align:left; padding:8px;">邮箱</th>
                <th style="text-align:left; padding:8px;">角色</th>
                <th style="text-align:left; padding:8px;">注册时间</th>
                <th style="text-align:left; padding:8px;">操作</th>
              </tr>
            </thead>
            <tbody>
            <tr v-for="u in users" :key="u.id" style="border-top:1px solid #eee;">
              <td style="padding:8px;">{{ u.username }}</td>
              <td style="padding:8px;">{{ u.email || '-' }}</td>
              <td style="padding:8px;">{{ u.role }}</td>
              <td style="padding:8px;">{{ formatDateTime(u.created_at) }}</td>
              <td style="padding:8px;">
                <button class="btn btn-small" @click="editUser(u)" style="margin-right:8px; cursor: pointer;">
                  编辑
                </button>
                <button class="btn btn-small btn-danger" @click="deleteUser(u)" style="cursor: pointer;">
                  删除
                </button>
              </td>
            </tr>
            <tr v-if="users.length === 0">
              <td colspan="5" style="padding:12px; color:#666;">暂无用户数据</td>
            </tr>
          </tbody>
          </table>
        </div>
      </div>
      
      <!-- 个人配置标签页 -->
      <div v-if="activeTab === 'personal'" class="tab-content">
        <div class="personal-notice">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          <span>个人配置保存在您的浏览器中，不会上传到服务器。启用后将覆盖全局配置。</span>
        </div>

        <!-- 个人文本生成配置 -->
        <div class="card card-personal">
          <div class="section-header">
            <div>
              <h2 class="section-title">
                文本生成配置
                <label class="toggle-switch">
                  <input type="checkbox" v-model="personalConfig.config.value.text.enabled" @change="personalConfig.save()">
                  <span class="slider"></span>
                </label>
                <span class="toggle-label">{{ personalConfig.isTextPersonalEnabled.value ? '已启用' : '已禁用' }}</span>
              </h2>
              <p class="section-desc">启用后将使用个人 API Key，全局配置失效</p>
            </div>
            <div v-if="personalConfig.isTextPersonalEnabled.value">
              <button class="btn btn-small" @click="openPersonalTextModal()">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                添加
              </button>
            </div>
          </div>

          <!-- 服务商列表表格 -->
          <div v-if="personalConfig.isTextPersonalEnabled.value">
            <ProviderTable
              :providers="personalConfig.getTextProvidersAsRecord()"
              :activeProvider="personalConfig.config.value.text.active_provider"
              :is-admin="false"
              :show-delete="true"
              :show-edit="true"
              @activate="personalConfig.activateTextProvider"
              @edit="openEditPersonalTextModal"
              @delete="personalConfig.deleteTextProvider"
              @test="testPersonalTextProvider"
            />
            <div v-if="personalConfig.config.value.text.providers.length === 0" class="empty-hint">
              暂无个人配置，请点击"添加"按钮添加服务商
            </div>
          </div>
          <div v-else class="disabled-hint">
            个人配置已禁用，当前使用全局配置
          </div>
        </div>

        <!-- 个人图片生成配置 -->
        <div class="card card-personal">
          <div class="section-header">
            <div>
              <h2 class="section-title">
                图片生成配置
                <label class="toggle-switch">
                  <input type="checkbox" v-model="personalConfig.config.value.image.enabled" @change="personalConfig.save()">
                  <span class="slider"></span>
                </label>
                <span class="toggle-label">{{ personalConfig.isImagePersonalEnabled.value ? '已启用' : '已禁用' }}</span>
              </h2>
              <p class="section-desc">启用后将使用个人 API Key，全局配置失效</p>
            </div>
            <div v-if="personalConfig.isImagePersonalEnabled.value">
              <button class="btn btn-small" @click="openPersonalImageModal()">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                添加
              </button>
            </div>
          </div>

          <!-- 服务商列表表格 -->
          <div v-if="personalConfig.isImagePersonalEnabled.value">
            <ProviderTable
              :providers="personalConfig.getImageProvidersAsRecord()"
              :activeProvider="personalConfig.config.value.image.active_provider"
              :is-admin="false"
              :show-delete="true"
              :show-edit="true"
              @activate="personalConfig.activateImageProvider"
              @edit="openEditPersonalImageModal"
              @delete="personalConfig.deleteImageProvider"
              @test="testPersonalImageProvider"
            />
            <div v-if="personalConfig.config.value.image.providers.length === 0" class="empty-hint">
              暂无个人配置，请点击"添加"按钮添加服务商
            </div>
          </div>
          <div v-else class="disabled-hint">
            个人配置已禁用，当前使用全局配置
          </div>
        </div>
      </div>
    </div>

    <!-- 个人文本服务商弹窗 -->
    <ProviderModal
      :visible="showPersonalTextModal"
      :isEditing="!!editingPersonalTextProvider"
      :formData="personalTextForm"
      :testing="false"
      :typeOptions="textTypeOptions"
      providerCategory="text"
      @close="closePersonalTextModal"
      @save="savePersonalTextProvider"
      @test="testPersonalTextConnection"
      @update:formData="(data: any) => personalTextForm = data"
    />

    <!-- 个人图片服务商弹窗 -->
    <ImageProviderModal
      :visible="showPersonalImageModal"
      :isEditing="!!editingPersonalImageProvider"
      :formData="personalImageForm"
      :testing="false"
      :typeOptions="imageTypeOptions"
      @close="closePersonalImageModal"
      @save="savePersonalImageProvider"
      @test="testPersonalImageConnection"
      @update:formData="(data: any) => personalImageForm = data"
    />

    <!-- 文本服务商弹窗 -->
    <ProviderModal
      :visible="showTextModal"
      :isEditing="!!editingTextProvider"
      :formData="textForm"
      :testing="testingText"
      :typeOptions="textTypeOptions"
      providerCategory="text"
      @close="closeTextModal"
      @save="saveTextProvider"
      @test="testTextConnection"
      @update:formData="updateTextForm"
    />

    <!-- 图片服务商弹窗 -->
    <ImageProviderModal
      :visible="showImageModal"
      :isEditing="!!editingImageProvider"
      :formData="imageForm"
      :testing="testingImage"
      :typeOptions="imageTypeOptions"
      @close="closeImageModal"
      @save="saveImageProvider"
      @test="testImageConnection"
      @update:formData="updateImageForm"
    />
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import ProviderTable from '../components/settings/ProviderTable.vue'
import ProviderModal from '../components/settings/ProviderModal.vue'
import ImageProviderModal from '../components/settings/ImageProviderModal.vue'
import {
  useProviderForm,
  textTypeOptions,
  imageTypeOptions,
  type TextProviderForm,
  type ImageProviderForm
} from '../composables/useProviderForm'
import { usePersonalConfig, type PersonalProvider } from '../composables/usePersonalConfig'
import { getAdminUsers, updateAdminUser, deleteAdminUser } from '../api/adminUsers'
import { getUserProviders, setUserProvider } from '../api/provider'
import { getMe } from '../api/auth'
import { testConnection } from '../api'
import { showSuccess, showError, showWarning, showDangerConfirm, showInfo, showPrompt } from '../utils/dialog'

/**
 * 系统设置页面
 *
 * 功能：
 * - 管理文本生成服务商配置
 * - 管理图片生成服务商配置
 * - 测试 API 连接
 * - 用户管理（管理员）
 */

// 使用 composable 管理全局配置表单状态和逻辑
const {
  // 状态
  loading,
  testingText,
  testingImage,

  // 配置数据
  textConfig,
  imageConfig,

  // 文本服务商弹窗
  showTextModal,
  editingTextProvider,
  textForm,

  // 图片服务商弹窗
  showImageModal,
  editingImageProvider,
  imageForm,

  // 方法
  loadConfig,

  // 文本服务商方法
  activateTextProvider,
  openAddTextModal,
  openEditTextModal,
  closeTextModal,
  saveTextProvider,
  deleteTextProvider,
  testTextConnection,
  testTextProviderInList,
  updateTextForm,

  // 图片服务商方法
  activateImageProvider,
  openAddImageModal,
  openEditImageModal,
  closeImageModal,
  saveImageProvider,
  deleteImageProvider,
  testImageConnection,
  testImageProviderInList,
  updateImageForm
} = useProviderForm()

// ==================== 个人配置（存储在 localStorage） ====================
const personalConfig = usePersonalConfig()

// 个人文本服务商弹窗状态
const showPersonalTextModal = ref(false)
const editingPersonalTextProvider = ref<string | null>(null)
const personalTextForm = ref<TextProviderForm>({
  name: '',
  type: 'openai_compatible',
  api_key: '',
  api_key_masked: '',
  base_url: '',
  model: '',
  endpoint_type: '/v1/chat/completions',
  _has_api_key: false
})

// 个人图片服务商弹窗状态
const showPersonalImageModal = ref(false)
const editingPersonalImageProvider = ref<string | null>(null)
const personalImageForm = ref<ImageProviderForm>({
  name: '',
  type: 'image_api',
  api_key: '',
  api_key_masked: '',
  base_url: '',
  model: '',
  high_concurrency: false,
  short_prompt: false,
  endpoint_type: '/v1/images/generations',
  _has_api_key: false
})

// 打开添加个人文本服务商弹窗
function openPersonalTextModal() {
  editingPersonalTextProvider.value = null
  personalTextForm.value = {
    name: '',
    type: 'openai_compatible',
    api_key: '',
    api_key_masked: '',
    base_url: '',
    model: '',
    endpoint_type: '/v1/chat/completions',
    _has_api_key: false
  }
  showPersonalTextModal.value = true
}

// 打开编辑个人文本服务商弹窗
function openEditPersonalTextModal(name: string, provider: any) {
  const p = personalConfig.config.value.text.providers.find(x => x.name === name)
  if (!p) return
  editingPersonalTextProvider.value = name
  personalTextForm.value = {
    name: p.name,
    type: p.type,
    api_key: p.api_key,
    api_key_masked: p.api_key ? '****' + p.api_key.slice(-4) : '',
    base_url: p.base_url || '',
    model: p.model,
    endpoint_type: p.endpoint_type || '/v1/chat/completions',
    _has_api_key: !!p.api_key
  }
  showPersonalTextModal.value = true
}

// 关闭个人文本服务商弹窗
function closePersonalTextModal() {
  showPersonalTextModal.value = false
  editingPersonalTextProvider.value = null
}

// 保存个人文本服务商
function savePersonalTextProvider() {
  const name = editingPersonalTextProvider.value || personalTextForm.value.name
  if (!name) {
    showWarning('请填写服务商名称')
    return
  }
  if (!personalTextForm.value.api_key && !editingPersonalTextProvider.value) {
    showWarning('请填写 API Key')
    return
  }

  const provider: PersonalProvider = {
    name,
    type: personalTextForm.value.type,
    api_key: personalTextForm.value.api_key || personalConfig.config.value.text.providers.find(p => p.name === name)?.api_key || '',
    base_url: personalTextForm.value.base_url,
    model: personalTextForm.value.model,
    endpoint_type: personalTextForm.value.endpoint_type
  }

  if (editingPersonalTextProvider.value) {
    personalConfig.updateTextProvider(name, provider)
  } else {
    personalConfig.addTextProvider(provider)
  }

  closePersonalTextModal()
}

// 测试个人文本服务商连接（弹窗中）
async function testPersonalTextConnection() {
  try {
    const result = await testConnection({
      type: personalTextForm.value.type,
      provider_name: undefined,
      api_key: personalTextForm.value.api_key || undefined,
      base_url: personalTextForm.value.base_url,
      model: personalTextForm.value.model
    })
    if (result.success) {
      showSuccess(result.message || '连接成功', '测试通过')
    }
  } catch (e: any) {
    showError('连接失败：' + (e.response?.data?.error || e.message))
  }
}

// 测试列表中的个人文本服务商
async function testPersonalTextProvider(name: string) {
  const p = personalConfig.config.value.text.providers.find(x => x.name === name)
  if (!p) return

  try {
    const result = await testConnection({
      type: p.type,
      provider_name: undefined,
      api_key: p.api_key,
      base_url: p.base_url,
      model: p.model
    })
    if (result.success) {
      showSuccess(result.message || '连接成功', '测试通过')
    }
  } catch (e: any) {
    showError('连接失败：' + (e.response?.data?.error || e.message))
  }
}

// 打开添加个人图片服务商弹窗
function openPersonalImageModal() {
  editingPersonalImageProvider.value = null
  personalImageForm.value = {
    name: '',
    type: 'image_api',
    api_key: '',
    api_key_masked: '',
    base_url: '',
    model: '',
    high_concurrency: false,
    short_prompt: false,
    endpoint_type: '/v1/images/generations',
    _has_api_key: false
  }
  showPersonalImageModal.value = true
}

// 打开编辑个人图片服务商弹窗
function openEditPersonalImageModal(name: string, provider: any) {
  const p = personalConfig.config.value.image.providers.find(x => x.name === name)
  if (!p) return
  editingPersonalImageProvider.value = name
  personalImageForm.value = {
    name: p.name,
    type: p.type,
    api_key: p.api_key,
    api_key_masked: p.api_key ? '****' + p.api_key.slice(-4) : '',
    base_url: p.base_url || '',
    model: p.model,
    high_concurrency: p.high_concurrency || false,
    short_prompt: p.short_prompt || false,
    endpoint_type: p.endpoint_type || '/v1/images/generations',
    _has_api_key: !!p.api_key
  }
  showPersonalImageModal.value = true
}

// 关闭个人图片服务商弹窗
function closePersonalImageModal() {
  showPersonalImageModal.value = false
  editingPersonalImageProvider.value = null
}

// 保存个人图片服务商
function savePersonalImageProvider() {
  const name = editingPersonalImageProvider.value || personalImageForm.value.name
  if (!name) {
    showWarning('请填写服务商名称')
    return
  }
  if (!personalImageForm.value.api_key && !editingPersonalImageProvider.value) {
    showWarning('请填写 API Key')
    return
  }

  const provider: PersonalProvider = {
    name,
    type: personalImageForm.value.type,
    api_key: personalImageForm.value.api_key || personalConfig.config.value.image.providers.find(p => p.name === name)?.api_key || '',
    base_url: personalImageForm.value.base_url,
    model: personalImageForm.value.model,
    endpoint_type: personalImageForm.value.endpoint_type,
    high_concurrency: personalImageForm.value.high_concurrency,
    short_prompt: personalImageForm.value.short_prompt
  }

  if (editingPersonalImageProvider.value) {
    personalConfig.updateImageProvider(name, provider)
  } else {
    personalConfig.addImageProvider(provider)
  }

  closePersonalImageModal()
}

// 测试个人图片服务商连接（弹窗中）
async function testPersonalImageConnection() {
  try {
    const result = await testConnection({
      type: personalImageForm.value.type,
      provider_name: undefined,
      api_key: personalImageForm.value.api_key || undefined,
      base_url: personalImageForm.value.base_url,
      model: personalImageForm.value.model
    })
    if (result.success) {
      showSuccess(result.message || '连接成功', '测试通过')
    }
  } catch (e: any) {
    showError('连接失败：' + (e.response?.data?.error || e.message))
  }
}

// 测试列表中的个人图片服务商
async function testPersonalImageProvider(name: string) {
  const p = personalConfig.config.value.image.providers.find(x => x.name === name)
  if (!p) return

  try {
    const result = await testConnection({
      type: p.type,
      provider_name: undefined,
      api_key: p.api_key,
      base_url: p.base_url,
      model: p.model
    })
    if (result.success) {
      showSuccess(result.message || '连接成功', '测试通过')
    }
  } catch (e: any) {
    showError('连接失败：' + (e.response?.data?.error || e.message))
  }
}

// 管理员状态
const isAdmin = ref(false)

// 标签页状态
const activeTab = ref('global')

// 动态标签页列表
const tabs = computed(() => {
  const baseTabs = [
    { key: 'global', label: '全局配置' },
    { key: 'personal', label: '个人配置' }
  ]
  // 只有管理员才能看到用户管理标签页
  if (isAdmin.value) {
    baseTabs.push({ key: 'users', label: '用户管理' })
  }
  return baseTabs
})

// 监听标签页变化，当切换到用户管理标签页时加载用户数据
watch(activeTab, (newTab) => {
  if (newTab === 'users' && isAdmin.value) {
    loadUsers()
  }
})

onMounted(async () => {
  loadConfig()
  const me = await getMe()
  isAdmin.value = !!(me.success && me.user && me.user.role === 'admin')
  loadUserProviders()
})



const users = ref<Array<{ id: number; username: string; email?: string; role: string; created_at?: string }>>([])
const userLoading = ref(false)

async function loadUsers() {
  try {
    userLoading.value = true
    const r = await getAdminUsers()
    if (r.success && r.users) {
      users.value = r.users
    } else {
      showError(r.error || '加载失败')
    }
  } finally {
    userLoading.value = false
  }
}

// 格式化日期时间
function formatDateTime(dateStr: string | undefined): string {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hour = String(date.getHours()).padStart(2, '0')
    const minute = String(date.getMinutes()).padStart(2, '0')
    const second = String(date.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hour}:${minute}:${second}`
  } catch {
    return dateStr
  }
}

// 编辑用户（仅修改密码）
async function editUser(u: { id: number; username: string }) {
  const newPass = await showPrompt('请输入新密码', '', '输入新密码', `修改 ${u.username} 的密码`)
  
  if (newPass === null || !newPass.trim()) {
    return
  }
  
  try {
    const r = await updateAdminUser(u.id, { password: newPass.trim() })
    if (!r.success) {
      showError(r.error || '更新失败')
      return
    }
    showSuccess('密码修改成功')
  } catch (error) {
    console.error('修改密码失败:', error)
    showError('更新失败，请检查网络连接')
  }
}

// 删除用户
async function deleteUser(u: { id: number; username: string }) {
  if (!await showDangerConfirm(`确定要删除用户 ${u.username} 吗？此操作不可恢复。`, '删除用户')) {
    return
  }
  
  try {
    const r = await deleteAdminUser(u.id)
    if (!r.success) {
      showError(r.error || '删除失败')
      return
    }
    await loadUsers()
    showSuccess('用户删除成功')
  } catch (error) {
    console.error('删除用户失败:', error)
    showError('删除失败，请检查网络连接')
  }
}

const userTextForm = ref<{ provider_name: string; api_key?: string; base_url?: string; model?: string }>({ provider_name: '' })
const userImageForm = ref<{ provider_name: string; api_key?: string; base_url?: string; model?: string; quality?: string; default_size?: string; default_aspect_ratio?: string }>({ provider_name: '' })

async function loadUserProviders() {
  const t = await getUserProviders('text')
  if (t.success && t.providers && t.providers.length > 0) {
    const p = t.providers[0]
    userTextForm.value = { provider_name: p.provider_name, api_key: p.api_key, base_url: p.base_url, model: p.model }
  }
  const i = await getUserProviders('image')
  if (i.success && i.providers && i.providers.length > 0) {
    const p = i.providers[0]
    userImageForm.value = {
      provider_name: p.provider_name,
      api_key: p.api_key,
      base_url: p.base_url,
      model: p.model,
      quality: p.quality,
      default_size: p.default_size,
      default_aspect_ratio: p.default_aspect_ratio,
    }
  }
}

async function saveUserTextKey() {
  if (!userTextForm.value.provider_name) {
    showWarning('请填写服务商名称')
    return
  }
  const r = await setUserProvider({
    category: 'text',
    provider_name: userTextForm.value.provider_name,
    api_key: userTextForm.value.api_key,
    base_url: userTextForm.value.base_url,
    model: userTextForm.value.model,
  })
  if (!r.success) {
    showError(r.error || '保存失败')
  } else {
    showSuccess('保存成功')
  }
}

async function saveUserImageKey() {
  if (!userImageForm.value.provider_name) {
    showWarning('请填写服务商名称')
    return
  }
  const r = await setUserProvider({
    category: 'image',
    provider_name: userImageForm.value.provider_name,
    api_key: userImageForm.value.api_key,
    base_url: userImageForm.value.base_url,
    model: userImageForm.value.model,
    quality: userImageForm.value.quality,
    default_size: userImageForm.value.default_size,
    default_aspect_ratio: userImageForm.value.default_aspect_ratio,
  })
  if (!r.success) {
    showError(r.error || '保存失败')
  } else {
    showSuccess('保存成功')
  }
}
</script>

<style scoped>
/* 基础布局 */
.settings-container {
  max-width: 900px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #1a1a1a;
}

.section-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 按钮样式 */
.btn-small {
  padding: 6px 12px;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #666;
}

/* 标签页样式 */
.settings-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.tab-item {
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-sub);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
  background: transparent;
  border: none;
  outline: none;
}

.tab-item:hover {
  color: var(--text-primary);
  background: var(--hover-bg);
}

.tab-item.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
  background: var(--hover-bg);
}

.tab-content {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* 卡片样式 */
.card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-global { 
  border: 1px solid #ffd6d6; 
  background: #fffafa; 
  margin-bottom: 24px;
}

.card-personal { 
  border: 1px solid #d6e4ff; 
  background: #f7fbff; 
  margin-bottom: 24px;
}

/* 按钮样式增强 */
.btn-danger {
  background: #ff4d4f;
  color: white;
  border-color: #ff4d4f;
}

.btn-danger:hover {
  background: #f5222d;
  border-color: #f5222d;
}

/* 个人配置提示 */
.personal-notice {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 8px;
  margin-bottom: 20px;
  color: #1890ff;
  font-size: 14px;
}

/* 开关样式 */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  margin-left: 12px;
  vertical-align: middle;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.3s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #1890ff;
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.toggle-label {
  margin-left: 8px;
  font-size: 13px;
  font-weight: 400;
  color: #666;
  vertical-align: middle;
}

/* 提示文本 */
.empty-hint, .disabled-hint {
  padding: 20px;
  text-align: center;
  color: #999;
  font-size: 14px;
  background: #fafafa;
  border-radius: 6px;
  margin-top: 12px;
}

.disabled-hint {
  background: #f5f5f5;
  color: #888;
}
</style>
