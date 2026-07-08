// middleware/auth.global.ts
import { useAuth } from '~/composables/useAuth'

export default defineNuxtRouteMiddleware(async (to) => {

  const { usuario, carregado, isAdmin, carregarMe } = useAuth()
  if (!carregado.value) await carregarMe()

  // não logado → manda para /login (exceto se já estiver lá)
  if (!usuario.value && to.path !== '/login') {
    return navigateTo('/login')
  }
  // logado tentando ver /login → manda para o app
  if (usuario.value && to.path === '/login') {
    return navigateTo('/')
  }
  // /admin é só para admin
  if (to.path.startsWith('/admin') && !isAdmin.value) {
    return navigateTo('/')
  }
})
