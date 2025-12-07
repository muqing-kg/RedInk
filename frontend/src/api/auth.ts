import axios from 'axios'

const API_BASE_URL = '/api'

export async function login(username: string, password: string) {
  const res = await axios.post(`${API_BASE_URL}/auth/login`, { username, password })
  const data = res.data as { success: boolean; access_token?: string; role?: string; error?: string }
  if (data.success && data.access_token) {
    try {
      localStorage.setItem('access_token', data.access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
    } catch {}
  }
  return data
}

export async function getMe() {
  const res = await axios.get(`${API_BASE_URL}/auth/me`)
  return res.data as { success: boolean; user?: { id: number; username: string; email?: string; role: string } }
}

export async function register(username: string, email: string | undefined, password: string) {
  const res = await axios.post(`${API_BASE_URL}/auth/register`, { username, email, password })
  return res.data as { success: boolean; error?: string }
}
