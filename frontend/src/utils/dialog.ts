import { ref, createApp, h } from 'vue'
import AppDialog from '../components/common/AppDialog.vue'

/**
 * 对话框配置选项
 */
interface DialogOptions {
    type?: 'success' | 'error' | 'warning' | 'confirm' | 'info'
    title?: string
    message: string
    showCancel?: boolean
    confirmText?: string
    cancelText?: string
}

/**
 * 显示对话框
 */
/**
 * 显示对话框
 */
function showDialog<T = boolean>(options: DialogOptions & { showInput?: boolean; inputValue?: string; inputPlaceholder?: string }): Promise<T> {
    return new Promise((resolve) => {
        // 创建挂载点
        const mountNode = document.createElement('div')
        document.body.appendChild(mountNode)

        const visible = ref(true)

        const app = createApp({
            render() {
                return h(AppDialog, {
                    visible: visible.value,
                    type: options.type || 'info',
                    title: options.title || '提示',
                    message: options.message,
                    showCancel: options.showCancel || false,
                    confirmText: options.confirmText || '确定',
                    cancelText: options.cancelText || '取消',
                    showInput: options.showInput || false,
                    inputValue: options.inputValue || '',
                    inputPlaceholder: options.inputPlaceholder || '',
                    onConfirm: (value?: any) => {
                        // 如果是输入框模式，返回输入的值（或者空字符串），否则返回 true
                        resolve(options.showInput ? value : true as any)
                    },
                    onCancel: () => {
                        resolve((options.showInput ? null : false) as any)
                    },
                    onClose: () => {
                        visible.value = false
                        // 延迟卸载，等动画完成
                        setTimeout(() => {
                            app.unmount()
                            document.body.removeChild(mountNode)
                        }, 300)
                    }
                })
            }
        })

        app.mount(mountNode)
    })
}

/**
 * 成功提示
 */
export function showSuccess(message: string, title?: string): Promise<boolean> {
    return showDialog({
        type: 'success',
        title: title || '成功',
        message
    })
}

/**
 * 错误提示
 */
export function showError(message: string, title?: string): Promise<boolean> {
    return showDialog({
        type: 'error',
        title: title || '错误',
        message
    })
}

/**
 * 警告提示
 */
export function showWarning(message: string, title?: string): Promise<boolean> {
    return showDialog({
        type: 'warning',
        title: title || '警告',
        message
    })
}

/**
 * 信息提示
 */
export function showInfo(message: string, title?: string): Promise<boolean> {
    return showDialog({
        type: 'info',
        title: title || '提示',
        message
    })
}

/**
 * 确认对话框
 */
export function showConfirm(
    message: string,
    title?: string,
    options?: { confirmText?: string; cancelText?: string; type?: 'warning' | 'confirm' }
): Promise<boolean> {
    return showDialog({
        type: options?.type || 'confirm',
        title: title || '确认',
        message,
        showCancel: true,
        confirmText: options?.confirmText || '确定',
        cancelText: options?.cancelText || '取消'
    })
}

/**
 * 危险确认对话框
 */
export function showDangerConfirm(
    message: string,
    title?: string,
    options?: { confirmText?: string; cancelText?: string }
): Promise<boolean> {
    return showDialog({
        type: 'warning',
        title: title || '警告',
        message,
        showCancel: true,
        confirmText: options?.confirmText || '确定删除',
        cancelText: options?.cancelText || '取消'
    })
}

/**
 * 输入提示框
 */
export function showPrompt(
    message: string,
    defaultValue: string = '',
    placeholder: string = '',
    title: string = '输入'
): Promise<string | null> {
    return showDialog<string | null>({
        type: 'prompt', // 我们需要在 AppDialog 增加 prompt 样式的图标，或者复用 info
        title: title,
        message,
        showCancel: true,
        showInput: true,
        inputValue: defaultValue,
        inputPlaceholder: placeholder
    })
}
