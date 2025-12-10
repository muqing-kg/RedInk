<template>
  <div class="auth-container">
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
    
    <div class="auth-card-glass">
      <!-- 左侧品牌展示 -->
      <div class="auth-brand">
        <div class="brand-content">
          <div class="brand-logo-circle">
            <img src="/logo.png" alt="RedInk" class="logo-img" />
          </div>
          <h1 class="brand-title">RedInk</h1>
          <p class="brand-subtitle">✨ 你的灵感魔法工坊 ✨</p>
          <div class="brand-desc">
            开始你的创作之旅<br>
            和数万名创作者一起成长
          </div>
        </div>
        <!-- 装饰圆圈 -->
        <div class="circle-decoration c1"></div>
        <div class="circle-decoration c2"></div>
      </div>
      
      <!-- 右侧表单区 -->
      <div class="auth-form-side">
        <div class="form-header">
          <h2 class="auth-title">欢迎加入! 🎈</h2>
          <p class="auth-sub">填写下面的信息，领取你的魔法棒</p>
        </div>
        
        <form @submit.prevent="onSubmit" class="cute-form">
          <div class="form-group">
            <label class="form-label">用户名</label>
            <div class="input-wrapper">
              <input 
                class="cute-input" 
                v-model="username" 
                placeholder="起个好听的名字..." 
                autocomplete="username"
              />
              <span class="input-icon">👋</span>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">邮箱 (可选)</label>
            <div class="input-wrapper">
              <input 
                class="cute-input" 
                v-model="email" 
                type="email"
                placeholder="方便找回密码哦..." 
                autocomplete="email"
              />
              <span class="input-icon">📧</span>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">密码</label>
            <div class="input-wrapper">
              <input 
                class="cute-input" 
                type="password" 
                v-model="password" 
                placeholder="设置一个安全密码..." 
                autocomplete="new-password"
              />
              <span class="input-icon">🔐</span>
            </div>
          </div>
          
          <div v-if="errorMsg" class="error-bubble">
            {{ errorMsg }}
          </div>
          
          <button 
            class="btn-jelly" 
            type="submit" 
            :disabled="loading"
          >
            <span v-if="loading" class="spinner-small"></span>
            {{ loading ? '✨ 正在创建...' : '💖 立即注册' }}
          </button>
          
          <div class="auth-footer">
            <span class="text-gray">已经有账号啦？</span>
            <router-link to="/login" class="link-primary">直接登录鸭!</router-link>
          </div>
        </form>
      </div>
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
    errorMsg.value = '用户名和密码都要填哦~'
    return
  }
  loading.value = true
  try {
    const r = await register(username.value, email.value || undefined, password.value)
    if (!r.success) {
      errorMsg.value = r.error || '注册失败，请检查一下信息'
      return
    }
    const l = await login(username.value, password.value)
    if (!l.success) {
      errorMsg.value = '注册成功但自动登录失败，请手动登录'
      setTimeout(() => router.push('/login'), 1500)
      return
    }
    const redirect = (router.currentRoute.value.query.redirect as string) || '/'
    router.replace(redirect)
  } catch (e: any) {
    if (e.response && e.response.data && e.response.data.error) {
      errorMsg.value = e.response.data.error
    } else {
      errorMsg.value = '注册遇到点小问题，请稍后再试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 复用 LoginView 的样式，确保一致性 */
.auth-container {
  width: 100%;
  min-height: 100vh;
  background: 
    radial-gradient(circle at 10% 20%, #FFE5EC, transparent 40%),
    radial-gradient(circle at 90% 10%, #E0C3FC, transparent 40%),
    radial-gradient(circle at 50% 90%, #D4F1F4, transparent 50%),
    #FFF0F5;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  z-index: 0;
  opacity: 0.6;
}
.blob-1 {
  width: 400px;
  height: 400px;
  background: #FFD6E0;
  top: -100px;
  left: -100px;
  animation: float 15s infinite ease-in-out;
}
.blob-2 {
  width: 300px;
  height: 300px;
  background: #C4FAF8;
  bottom: -50px;
  right: -50px;
  animation: float 12s infinite ease-in-out reverse;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, 30px); }
}

.auth-card-glass {
  display: flex;
  width: 100%;
  max-width: 900px;
  height: auto; /* 高度自适应 */
  min-height: 550px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 4px solid rgba(255, 255, 255, 0.8);
  border-radius: 40px;
  box-shadow: 0 20px 60px rgba(159, 134, 192, 0.15);
  overflow: hidden;
  z-index: 1;
}

.auth-brand {
  flex: 1;
  background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  color: white;
  text-align: center;
  padding: 40px;
  min-height: 300px;
}

.brand-content { position: relative; z-index: 2; }

.brand-logo-circle {
  width: 100px; width: 100px; height: 100px;
  background: white; border-radius: 50%; padding: 10px;
  margin: 0 auto 20px;
  box-shadow: 0 10px 25px rgba(255, 92, 141, 0.3);
  animation: bounce-slow 3s infinite;
}

.logo-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }

.brand-title {
  font-family: 'Quicksand', sans-serif;
  font-size: 32px; font-weight: 800;
  margin-bottom: 8px; text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.brand-subtitle { font-size: 16px; font-weight: 600; opacity: 0.9; margin-bottom: 24px; }
.brand-desc { font-size: 14px; line-height: 1.6; opacity: 0.8; }

.circle-decoration {
  position: absolute; border-radius: 50%; background: rgba(255, 255, 255, 0.1);
}
.c1 { width: 200px; height: 200px; top: -50px; left: -50px; }
.c2 { width: 150px; height: 150px; bottom: 20px; right: -30px; }

.auth-form-side {
  flex: 1.2;
  padding: 40px 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: rgba(255, 255, 255, 0.4);
}

.form-header { margin-bottom: 24px; }
.auth-title { font-size: 28px; font-weight: 800; color: #4A4063; margin-bottom: 8px; }
.auth-sub { color: #8D84A3; font-size: 14px; }

.cute-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 13px; font-weight: 700; color: #FF85A1; margin-left: 4px; }
.input-wrapper { position: relative; }

.cute-input {
  width: 100%; padding: 14px 16px 14px 45px;
  border: 2px solid #F0E6EF; border-radius: 20px;
  font-size: 15px; color: #4A4063; background: white;
  transition: all 0.3s ease;
}
.cute-input:focus { outline: none; border-color: #FF85A1; box-shadow: 0 4px 12px rgba(255, 133, 161, 0.15); }
.input-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); font-size: 18px; }

.error-bubble {
  background: #FFE5E5; color: #FF5C5C;
  padding: 10px 16px; border-radius: 12px;
  font-size: 13px; text-align: center;
  animation: shake 0.4s;
}

.btn-jelly {
  margin-top: 10px; padding: 16px;
  border: none; border-radius: 20px;
  background: linear-gradient(45deg, #FF85A1, #FF5C8D);
  color: white; font-size: 16px; font-weight: 700;
  cursor: pointer; transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 8px 20px rgba(255, 92, 141, 0.3);
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.btn-jelly:hover:not(:disabled) { transform: translateY(-3px) scale(1.02); box-shadow: 0 12px 25px rgba(255, 92, 141, 0.4); }
.btn-jelly:active:not(:disabled) { transform: scale(0.95); }
.btn-jelly:disabled { opacity: 0.6; cursor: not-allowed; }

.auth-footer { text-align: center; margin-top: 20px; font-size: 14px; }
.text-gray { color: #A096B4; }
.link-primary { color: #FF85A1; font-weight: 700; text-decoration: none; margin-left: 6px; transition: color 0.2s; }
.link-primary:hover { color: #FF5C8D; text-decoration: underline; }

@keyframes bounce-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
@keyframes shake {
  0% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  50% { transform: translateX(5px); }
  75% { transform: translateX(-5px); }
  100% { transform: translateX(0); }
}
.spinner-small {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3); border-top-color: white;
  border-radius: 50%; animation: spinner 0.8s linear infinite;
}
@keyframes spinner { to { transform: rotate(360deg); } }

@media (max-width: 800px) {
  .auth-card-glass { flex-direction: column; width: 95%; }
  .auth-brand { padding: 30px; }
  .auth-form-side { padding: 30px; }
}
</style>
