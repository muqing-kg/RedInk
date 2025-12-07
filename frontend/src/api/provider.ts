import axios from 'axios'

const API_BASE_URL = '/api'

export async function setGlobalProvider(payload: {
  category: 'image' | 'text'
  provider_name: string
  type?: string
  api_key?: string
  base_url?: string
  model?: string
  quality?: string
  default_size?: string
  default_aspect_ratio?: string
}) {
  const res = await axios.post(`${API_BASE_URL}/admin/providers`, payload)
  return res.data
}

export async function setUserProvider(payload: {
  category: 'image' | 'text'
  provider_name: string
  api_key?: string
  base_url?: string
  model?: string
  quality?: string
  default_size?: string
  default_aspect_ratio?: string
}) {
  const res = await axios.post(`${API_BASE_URL}/user/providers`, payload)
  return res.data
}

export async function getUserProviders(category?: 'image' | 'text') {
  const res = await axios.get(`${API_BASE_URL}/user/providers`, { params: { category } })
  return res.data as {
    success: boolean
    providers?: Array<{
      category: 'image' | 'text'
      provider_name: string
      api_key?: string
      base_url?: string
      model?: string
      quality?: string
      default_size?: string
      default_aspect_ratio?: string
    }>
    error?: string
  }
}
