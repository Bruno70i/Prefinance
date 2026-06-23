# Passo 04 — Frontend: tela de login + guarda de rotas

> **Objetivo:** criar o composable de auth, a página `/login`, o middleware que protege as rotas e o
> botão "Sair". Como o token está em cookie `httpOnly`, as chamadas de API existentes continuam
> funcionando sem alteração.

**Depende de:** 02.
**Arquivos novos:** `composables/useAuth.ts`, `pages/login.vue`, `middleware/auth.global.ts`.
**Arquivos alterados:** `pages/index.vue` (botão Sair + link Admin, opcional).

---

## 4.1 Composable — `composables/useAuth.ts`

Segue o padrão de estado global de `useEntity.ts` (ref no escopo do módulo).

```ts
// composables/useAuth.ts
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
```

## 4.2 Página de login — `pages/login.vue`

```vue
<template>
  <div style="min-height:100vh; display:flex; align-items:center; justify-content:center; background:#f1f5f9">
    <form @submit.prevent="entrar" style="background:#fff; padding:32px; border-radius:14px; width:360px; max-width:92vw; box-shadow:0 20px 40px rgba(0,0,0,.1)">
      <h1 style="margin:0 0 4px; color:#0b5394; font-size:22px">PreFinance</h1>
      <p style="margin:0 0 20px; color:#64748b; font-size:13px">Acesso ao sistema</p>

      <label style="font-size:13px; color:#334155">Usuário</label>
      <input v-model="username" type="text" autocomplete="username" required
             style="width:100%; padding:10px; margin:4px 0 14px; border:1px solid #cbd5e1; border-radius:8px" />

      <label style="font-size:13px; color:#334155">Senha</label>
      <input v-model="senha" type="password" autocomplete="current-password" required
             style="width:100%; padding:10px; margin:4px 0 14px; border:1px solid #cbd5e1; border-radius:8px" />

      <p v-if="erro" style="color:#ef4444; font-size:13px; margin:0 0 12px">⚠️ {{ erro }}</p>

      <button type="submit" :disabled="carregando"
              style="width:100%; padding:11px; background:#0b5394; color:#fff; border:none; border-radius:8px; font-weight:600; cursor:pointer">
        {{ carregando ? 'Entrando…' : 'Entrar' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '~/composables/useAuth'

definePageMeta({ layout: false }) // tela cheia, sem o layout do app
const { login } = useAuth()
const username = ref(''); const senha = ref('')
const erro = ref(''); const carregando = ref(false)

const entrar = async () => {
  erro.value = ''; carregando.value = true
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
```

## 4.3 Middleware global — `middleware/auth.global.ts`

```ts
// middleware/auth.global.ts
import { useAuth } from '~/composables/useAuth'

export default defineNuxtRouteMiddleware(async (to) => {
  // Guarda apenas no cliente (o backend valida o token em cada chamada de API).
  if (import.meta.server) return

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
```

## 4.4 Botão "Sair" (e link Admin) no app

Em `pages/index.vue`, na sidebar (perto do card do usuário "Ana Souza"), troque o nome fixo pelo do
usuário logado e adicione ações:
```html
<div class="user-info">
  <div class="u-name">{{ usuario?.nome || 'Usuário' }}</div>
  <div class="u-role">{{ isAdmin ? 'Administrador' : 'Usuário' }}</div>
</div>
<button v-if="isAdmin" @click="navigateTo('/admin')" class="btn btn-ghost btn-sm">Admin</button>
<button @click="sair" class="btn btn-ghost btn-sm">Sair</button>
```
```ts
import { useAuth } from '~/composables/useAuth'
const { usuario, isAdmin, logout } = useAuth()
const sair = async () => { await logout(); await navigateTo('/login') }
```

---

## 4.5 Critérios de aceite

- [ ] Acessar qualquer rota sem login redireciona para `/login`.
- [ ] Login com admin (`.env`) e com usuário do banco funciona; credencial errada mostra erro.
- [ ] Depois de logar, o dashboard carrega e as chamadas de API funcionam (cookie enviado).
- [ ] "Sair" limpa a sessão e volta para `/login`.
- [ ] Usuário comum que tentar abrir `/admin` é redirecionado para `/`.

## 4.6 Verificação importante (cookie via proxy)

Após implementar, confirme no DevTools → Network que, após o login, as chamadas `/api/...` enviam o
cookie `access_token` e retornam `200`. Se retornarem `401` (cookie não repassado pelo proxy), use o
**fallback Bearer**: no `useAuth.login`, capture o token do corpo da resposta e envie via header em um
wrapper de `$fetch`. (O `auth.py` já aceita `Authorization: Bearer`.)

## 4.7 Segurança / reversão

Reverter = remover os 3 arquivos novos e os ajustes na sidebar. (As rotas do backend continuam
protegidas; para "abrir" o app sem login, remova os `Depends` do passo 02.)

> Próximo: `05-frontend-painel-admin.md`.
