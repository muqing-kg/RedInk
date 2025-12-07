import axios from 'axios'

const API_BASE_URL = '/api'

export async function syncGlobalProvider(category: 'image' | 'text', providerName: string) {
  const res = await axios.post(`${API_BASE_URL}/admin/providers/sync`, {
    category,
    provider_name: providerName
  })
  return res.data as { success: boolean; synced?: number; error?: string }
}
