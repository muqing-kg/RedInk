import { ref, computed } from 'vue'

/**
 * 个人配置管理 Composable
 *
 * 个人配置存储在浏览器 localStorage 中，不保存到数据库
 * 每个用户的配置完全独立，互不影响
 */

// localStorage 存储键
const PERSONAL_CONFIG_KEY = 'redink_personal_config'

// 个人服务商配置类型
export interface PersonalProvider {
    name: string
    type: string
    api_key: string
    base_url?: string
    model: string
    endpoint_type?: string
    high_concurrency?: boolean
    short_prompt?: boolean
}

// 个人配置类型
export interface PersonalConfig {
    text: {
        enabled: boolean  // 是否启用个人配置（启用后全局配置失效）
        providers: PersonalProvider[]
        active_provider: string
    }
    image: {
        enabled: boolean
        providers: PersonalProvider[]
        active_provider: string
    }
}

// 默认空配置
function createEmptyConfig(): PersonalConfig {
    return {
        text: {
            enabled: false,
            providers: [],
            active_provider: ''
        },
        image: {
            enabled: false,
            providers: [],
            active_provider: ''
        }
    }
}

/**
 * 从 localStorage 加载个人配置
 */
function loadFromStorage(): PersonalConfig {
    try {
        const saved = localStorage.getItem(PERSONAL_CONFIG_KEY)
        if (saved) {
            return JSON.parse(saved)
        }
    } catch (e) {
        console.error('加载个人配置失败:', e)
    }
    return createEmptyConfig()
}

/**
 * 保存个人配置到 localStorage
 */
function saveToStorage(config: PersonalConfig) {
    try {
        localStorage.setItem(PERSONAL_CONFIG_KEY, JSON.stringify(config))
    } catch (e) {
        console.error('保存个人配置失败:', e)
    }
}

/**
 * 个人配置管理 Hook
 */
export function usePersonalConfig() {
    // 配置数据
    const config = ref<PersonalConfig>(loadFromStorage())

    // 文本个人配置
    const personalTextConfig = computed(() => config.value.text)
    const personalImageConfig = computed(() => config.value.image)

    // 是否启用个人配置
    const isTextPersonalEnabled = computed(() => config.value.text.enabled)
    const isImagePersonalEnabled = computed(() => config.value.image.enabled)

    /**
     * 保存配置
     */
    function save() {
        saveToStorage(config.value)
    }

    // ==================== 文本配置操作 ====================

    /**
     * 启用/禁用文本个人配置
     */
    function toggleTextPersonal(enabled: boolean) {
        config.value.text.enabled = enabled
        save()
    }

    /**
     * 添加文本服务商
     */
    function addTextProvider(provider: PersonalProvider) {
        config.value.text.providers.push(provider)
        // 如果是第一个，自动激活
        if (config.value.text.providers.length === 1) {
            config.value.text.active_provider = provider.name
        }
        save()
    }

    /**
     * 编辑文本服务商
     */
    function updateTextProvider(name: string, provider: PersonalProvider) {
        const index = config.value.text.providers.findIndex(p => p.name === name)
        if (index !== -1) {
            config.value.text.providers[index] = provider
            save()
        }
    }

    /**
     * 删除文本服务商
     */
    function deleteTextProvider(name: string) {
        config.value.text.providers = config.value.text.providers.filter(p => p.name !== name)
        if (config.value.text.active_provider === name) {
            config.value.text.active_provider = config.value.text.providers[0]?.name || ''
        }
        save()
    }

    /**
     * 激活文本服务商
     */
    function activateTextProvider(name: string) {
        config.value.text.active_provider = name
        save()
    }

    // ==================== 图片配置操作 ====================

    /**
     * 启用/禁用图片个人配置
     */
    function toggleImagePersonal(enabled: boolean) {
        config.value.image.enabled = enabled
        save()
    }

    /**
     * 添加图片服务商
     */
    function addImageProvider(provider: PersonalProvider) {
        config.value.image.providers.push(provider)
        if (config.value.image.providers.length === 1) {
            config.value.image.active_provider = provider.name
        }
        save()
    }

    /**
     * 编辑图片服务商
     */
    function updateImageProvider(name: string, provider: PersonalProvider) {
        const index = config.value.image.providers.findIndex(p => p.name === name)
        if (index !== -1) {
            config.value.image.providers[index] = provider
            save()
        }
    }

    /**
     * 删除图片服务商
     */
    function deleteImageProvider(name: string) {
        config.value.image.providers = config.value.image.providers.filter(p => p.name !== name)
        if (config.value.image.active_provider === name) {
            config.value.image.active_provider = config.value.image.providers[0]?.name || ''
        }
        save()
    }

    /**
     * 激活图片服务商
     */
    function activateImageProvider(name: string) {
        config.value.image.active_provider = name
        save()
    }

    /**
     * 获取当前激活的文本服务商配置（用于 API 调用）
     */
    function getActiveTextProvider(): PersonalProvider | null {
        if (!config.value.text.enabled) return null
        return config.value.text.providers.find(
            p => p.name === config.value.text.active_provider
        ) || null
    }

    /**
     * 获取当前激活的图片服务商配置（用于 API 调用）
     */
    function getActiveImageProvider(): PersonalProvider | null {
        if (!config.value.image.enabled) return null
        return config.value.image.providers.find(
            p => p.name === config.value.image.active_provider
        ) || null
    }

    /**
     * 将 providers 数组转换为 ProviderTable 需要的 Record 格式
     */
    function getTextProvidersAsRecord(): Record<string, any> {
        const result: Record<string, any> = {}
        for (const p of config.value.text.providers) {
            result[p.name] = {
                type: p.type,
                model: p.model,
                base_url: p.base_url,
                api_key_masked: p.api_key ? '****' + p.api_key.slice(-4) : '',
                endpoint_type: p.endpoint_type
            }
        }
        return result
    }

    function getImageProvidersAsRecord(): Record<string, any> {
        const result: Record<string, any> = {}
        for (const p of config.value.image.providers) {
            result[p.name] = {
                type: p.type,
                model: p.model,
                base_url: p.base_url,
                api_key_masked: p.api_key ? '****' + p.api_key.slice(-4) : '',
                endpoint_type: p.endpoint_type,
                high_concurrency: p.high_concurrency,
                short_prompt: p.short_prompt
            }
        }
        return result
    }

    /**
     * 重新加载配置
     */
    function reload() {
        config.value = loadFromStorage()
    }

    return {
        // 配置数据
        config,
        personalTextConfig,
        personalImageConfig,
        isTextPersonalEnabled,
        isImagePersonalEnabled,

        // 文本操作
        toggleTextPersonal,
        addTextProvider,
        updateTextProvider,
        deleteTextProvider,
        activateTextProvider,
        getActiveTextProvider,
        getTextProvidersAsRecord,

        // 图片操作
        toggleImagePersonal,
        addImageProvider,
        updateImageProvider,
        deleteImageProvider,
        activateImageProvider,
        getActiveImageProvider,
        getImageProvidersAsRecord,

        // 通用
        reload,
        save
    }
}
