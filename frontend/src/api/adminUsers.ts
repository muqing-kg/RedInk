import axios from 'axios'

const API_BASE_URL = '/api'

export async function getAdminUsers() {
  const res = await axios.get(`${API_BASE_URL}/admin/users`)
  return res.data as { success: boolean; users?: Array<{ id: number; username: string; email?: string; role: string; created_at?: string }>; error?: string }
}

export async function updateAdminUser(userId: number, payload: { username?: string; password?: string }) {
  const res = await axios.put(`${API_BASE_URL}/admin/users/${userId}`, payload)
  return res.data as { success: boolean; error?: string }
}
