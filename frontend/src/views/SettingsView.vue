<template>
  <div class="container">
    <div class="page-header">
      <h1 class="page-title">系统设置</h1>
      <p class="page-subtitle">配置文本生成和图片生成的 API 服务</p>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>加载配置中...</p>
    </div>

    <div v-else class="settings-container">
      <!-- 文本生成配置（全局） -->
      <div class="card card-global">
        <div class="section-header">
          <div>
            <h2 class="section-title">文本生成配置</h2>
            <p class="section-desc">用于生成小红书图文大纲</p>
          </div>
          <div>
            <button class="btn btn-small" @click="syncTextKeys" style="margin-right:8px;">
              同步全局Key到所有用户
            </button>
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
          <div>
            <button class="btn btn-small" @click="syncImageKeys" style="margin-right:8px;">
              同步全局Key到所有用户
            </button>
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
          @activate="activateImageProvider"
          @edit="openEditImageModal"
          @delete="deleteImageProvider"
          @test="testImageProviderInList"
        />
      </div>
      <div class="card" v-if="isAdmin">
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
              <td style="padding:8px;">{{ u.created_at || '-' }}</td>
              <td style="padding:8px;">
                <button class="btn btn-small" @click="editUser(u)">编辑</button>
              </td>
            </tr>
            <tr v-if="users.length === 0">
              <td colspan="5" style="padding:12px; color:#666;">暂无用户数据</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card card-personal">
        <div class="section-header">
          <div>
            <h2 class="section-title">个人文本 Key 配置</h2>
            <p class="section-desc">仅对当前用户生效</p>
          </div>
          <div>
            <button class="btn btn-small" @click="saveUserTextKey">保存</button>
          </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <div>
            <label>服务商名称</label>
            <input class="input" v-model="userTextForm.provider_name" placeholder="google_gemini 或 openai_compatible" />
          </div>
          <div>
            <label>API Key</label>
            <input class="input" v-model="userTextForm.api_key" placeholder="用户自己的 Key" />
          </div>
          <div>
            <label>Base URL</label>
            <input class="input" v-model="userTextForm.base_url" placeholder="可选" />
          </div>
          <div>
            <label>Model</label>
            <input class="input" v-model="userTextForm.model" placeholder="如 gemini-2.0-flash-exp" />
          </div>
        </div>
      </div>

      <div class="card card-personal">
        <div class="section-header">
          <div>
            <h2 class="section-title">个人图片 Key 配置</h2>
            <p class="section-desc">仅对当前用户生效</p>
          </div>
          <div>
            <button class="btn btn-small" @click="saveUserImageKey">保存</button>
          </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <div>
            <label>服务商名称</label>
            <input class="input" v-model="userImageForm.provider_name" placeholder="openai_compatible / google_genai / image_api" />
          </div>
          <div>
            <label>API Key</label>
            <input class="input" v-model="userImageForm.api_key" placeholder="用户自己的 Key" />
          </div>
          <div>
            <label>Base URL</label>
            <input class="input" v-model="userImageForm.base_url" placeholder="兼容/私有中转站可填" />
          </div>
          <div>
            <label>Model</label>
            <input class="input" v-model="userImageForm.model" placeholder="如 dall-e-3 / nano-banana-2" />
          </div>
          <div>
            <label>Quality</label>
            <input class="input" v-model="userImageForm.quality" placeholder="standard / hd" />
          </div>
          <div>
            <label>Default Size</label>
            <input class="input" v-model="userImageForm.default_size" placeholder="1024x1024" />
          </div>
          <div>
            <label>Aspect Ratio</label>
            <input class="input" v-model="userImageForm.default_aspect_ratio" placeholder="3:4 / 1:1 / 16:9" />
          </div>
        </div>
      </div>
    </div>

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
import { onMounted, ref } from 'vue'
import ProviderTable from '../components/settings/ProviderTable.vue'
import ProviderModal from '../components/settings/ProviderModal.vue'
import ImageProviderModal from '../components/settings/ImageProviderModal.vue'
import {
  useProviderForm,
  textTypeOptions,
  imageTypeOptions
} from '../composables/useProviderForm'
import { syncGlobalProvider } from '../api/admin'
import { getAdminUsers, updateAdminUser } from '../api/adminUsers'
import { getUserProviders, setUserProvider } from '../api/provider'
import { getMe } from '../api/auth'

/**
 * 系统设置页面
 *
 * 功能：
 * - 管理文本生成服务商配置
 * - 管理图片生成服务商配置
 * - 测试 API 连接
 */

// 使用 composable 管理表单状态和逻辑
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

const isAdmin = ref(false)

onMounted(async () => {
  loadConfig()
  const me = await getMe()
  isAdmin.value = !!(me.success && me.user && me.user.role === 'admin')
  if (isAdmin.value) {
    loadUsers()
  }
  loadUserProviders()
})

async function syncTextKeys() {
  const active = textConfig.value.active_provider
  if (!active) return
  const r = await syncGlobalProvider('text', active)
  if (!r.success) {
    alert(r.error || '同步失败')
  } else {
    alert(`已同步 ${r.synced} 个用户`)
  }
}

async function syncImageKeys() {
  const active = imageConfig.value.active_provider
  if (!active) return
  const r = await syncGlobalProvider('image', active)
  if (!r.success) {
    alert(r.error || '同步失败')
  } else {
    alert(`已同步 ${r.synced} 个用户`)
  }
}

const users = ref<Array<{ id: number; username: string; email?: string; role: string; created_at?: string }>>([])
const userLoading = ref(false)

async function loadUsers() {
  try {
    userLoading.value = true
    const r = await getAdminUsers()
    if (r.success && r.users) {
      users.value = r.users
    } else {
      alert(r.error || '加载失败')
    }
  } finally {
    userLoading.value = false
  }
}

async function editUser(u: { id: number; username: string }) {
  const newName = window.prompt('请输入新用户名', u.username)
  if (newName === null) return
  const newPass = window.prompt('请输入新密码(留空则不修改)', '')
  const payload: any = {}
  if (newName && newName.trim() && newName !== u.username) payload.username = newName.trim()
  if (newPass && newPass.trim()) payload.password = newPass.trim()
  if (!payload.username && !payload.password) return
  const r = await updateAdminUser(u.id, payload)
  if (!r.success) {
    alert(r.error || '更新失败')
  } else {
    await loadUsers()
    alert('更新成功')
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
    alert('请填写服务商名称')
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
    alert(r.error || '保存失败')
  } else {
    alert('保存成功')
  }
}

async function saveUserImageKey() {
  if (!userImageForm.value.provider_name) {
    alert('请填写服务商名称')
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
    alert(r.error || '保存失败')
  } else {
    alert('保存成功')
  }
}
</script>

<style scoped>
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
</style>
<style scoped>
.card-global { border: 1px solid #ffd6d6; background: #fffafa; }
.card-personal { border: 1px solid #d6e4ff; background: #f7fbff; }
</style>
