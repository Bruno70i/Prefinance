// D:\github\Prefinance\composables\useAuth.ts
import { ref, computed } from 'vue'

export interface UsuarioLogado { username: string; nome: string; papel: 'admin' | 'usuario' }

const usuario = ref<UsuarioLogado | null>(null)
const carregado = ref(false)

export const useAuth = () => {
  const isAuth = computed(() => !!usuario.value)
  const isAdmin = computed(() => usuario.value?.papel === 'admin')

  const carregarMe = async () => {
    try {
      usuario.value = await $fetch<UsuarioLogado>('/api/auth/me')
    } catch {
      usuario.value = null
    } finally {
      carregado.value = true
    }
  }

  const login = async (username: string, senha: string) => {
    await $fetch('/api/auth/login', { method: 'POST', body: { username, senha } })
    await carregarMe()
  }

  const logout = async () => {
    try { await $fetch('/api/auth/logout', { method: 'POST' }) } catch {}
    usuario.value = null
  }

  return { usuario, carregado, isAuth, isAdmin, carregarMe, login, logout }
}
