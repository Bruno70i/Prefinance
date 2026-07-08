<template>
  <div class="login-wrapper">
    <div class="login-glass-card">
      <div class="login-header">
        <div class="logo-box">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="1" x2="12" y2="23" />
            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
          </svg>
        </div>
        <h1>PreFinance</h1>
        <p>Insira suas credenciais para acessar o painel de gestão</p>
      </div>

      <form @submit.prevent="entrar" class="login-form">
        <div class="form-group">
          <label for="username">Nome de Usuário</label>
          <div class="input-wrapper">
            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            <input 
              id="username"
              v-model="username" 
              type="text" 
              autocomplete="username" 
              placeholder="Digite seu usuário..."
              required 
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password">Senha</label>
          <div class="input-wrapper">
            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
            <input 
              id="password"
              v-model="senha" 
              type="password" 
              autocomplete="current-password" 
              placeholder="Digite sua senha..."
              required 
            />
          </div>
        </div>

        <transition name="fade">
          <div v-if="erro" class="error-alert">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>{{ erro }}</span>
          </div>
        </transition>

        <button type="submit" :disabled="carregando" class="btn-submit">
          <span v-if="carregando" class="spinner"></span>
          <span>{{ carregando ? 'Autenticando...' : 'Entrar no Sistema' }}</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '~/composables/useAuth'

definePageMeta({ layout: false })

const { login } = useAuth()
const username = ref('')
const senha = ref('')
const erro = ref('')
const carregando = ref(false)

const entrar = async () => {
  erro.value = ''
  carregando.value = true
  try {
    await login(username.value, senha.value)
    await navigateTo('/')
  } catch (e: any) {
    erro.value = e?.data?.detail || 'Usuário ou senha inválidos.'
  } finally {
    carregando.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at 10% 20%, rgb(18, 28, 54) 0%, rgb(12, 17, 34) 90%);
  font-family: 'DM Sans', sans-serif;
  overflow: hidden;
  position: relative;
}

/* Glassmorphism card styling */
.login-glass-card {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 40px;
  width: 420px;
  max-width: 90vw;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.4);
  z-index: 2;
  transition: all 0.3s ease;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo-box {
  background: linear-gradient(135deg, #F5791E 0%, #E0241F 100%);
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: #ffffff;
  box-shadow: 0 8px 24px rgba(29, 78, 216, 0.3);
}

.login-header h1 {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.5px;
}

.login-header p {
  margin: 8px 0 0;
  font-size: 14px;
  color: #94a3b8;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #cbd5e1;
  letter-spacing: 0.2px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: #64748b;
  pointer-events: none;
  transition: color 0.2s ease;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 14px 12px 42px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #ffffff;
  font-size: 14px;
  outline: none;
  transition: all 0.2s ease;
}

.input-wrapper input::placeholder {
  color: #475569;
}

.input-wrapper input:focus {
  border-color: #F5791E;
  box-shadow: 0 0 0 3px rgba(245, 121, 30, 0.18);
  background: rgba(15, 23, 42, 0.8);
}

.input-wrapper input:focus + .input-icon {
  color: #F5791E;
}

.error-alert {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 10px;
  padding: 12px 14px;
  color: #f87171;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-submit {
  width: 100%;
  padding: 13px;
  background: linear-gradient(135deg, #F5791E 0%, #E0241F 100%);
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(245, 121, 30, 0.3);
}

.btn-submit:hover {
  background: linear-gradient(135deg, #E0241F 0%, #FBBE12 100%);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(245, 121, 30, 0.4);
}

.btn-submit:active {
  transform: translateY(0);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2.5px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #ffffff;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
