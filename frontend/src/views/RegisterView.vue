<template>
  <div class="auth-bg">
    <div class="auth-card glass">
      <h1 class="auth-title">注册</h1>
      <form @submit.prevent="onSubmit" class="auth-form">
        <div>
          <label>用户名</label>
          <input class="input" v-model="username" placeholder="请输入用户名" />
        </div>
        <div>
          <label>邮箱（可选）</label>
          <input class="input" v-model="email" placeholder="请输入邮箱" />
        </div>
        <div>
          <label>密码</label>
          <input class="input" type="password" v-model="password" placeholder="请输入密码" />
        </div>
        <div v-if="errorMsg" class="auth-error">{{ errorMsg }}</div>
        <button class="btn btn-primary" type="submit" :disabled="loading">{{ loading ? '注册中...' : '注册' }}</button>
        <div class="auth-links">已有账号？<router-link to="/login">登录</router-link></div>
      </form>
    </div>
  </div>
  </template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register, login } from '../api/auth'

const router = useRouter()
const username = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

async function onSubmit() {
  errorMsg.value = ''
  if (!username.value || !password.value) {
    errorMsg.value = '请填写用户名和密码'
    return
  }
  loading.value = true
  try {
    const r = await register(username.value, email.value || undefined, password.value)
    if (!r.success) {
      errorMsg.value = r.error || '注册失败，请检查输入'
      return
    }
    const l = await login(username.value, password.value)
    if (!l.success) {
      errorMsg.value = '注册成功但自动登录失败，请手动登录'
    }
    const redirect = (router.currentRoute.value.query.redirect as string) || '/'
    router.replace(redirect)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-bg {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 24px;
  background: radial-gradient(1200px circle at 12% 80%, rgba(255,36,66,0.12), transparent 40%),
              radial-gradient(800px circle at 88% 30%, rgba(64,147,255,0.12), transparent 40%),
              linear-gradient(135deg, #fffafa 0%, #f7fbff 100%);
}
.auth-card {
  width: 420px;
  border-radius: 18px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.20);
  padding: 28px 26px 22px;
}
.glass {
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.35);
  backdrop-filter: blur(16px) saturate(120%);
}
.auth-title {
  font-size: 22px;
  font-weight: 800;
  margin: 0 0 6px;
}
.auth-form { display: grid; gap: 12px; }
.btn-primary { background: #ff2442; color: #fff; }
.auth-links { font-size: 13px; color: #666; }
.auth-error { color: #e53935; font-size: 13px; }
</style>
