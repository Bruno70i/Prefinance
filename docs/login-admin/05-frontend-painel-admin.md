# Passo 05 — Frontend: painel admin `/admin` (gestão de usuários)

> **Objetivo:** página `/admin` (somente admin) para **listar, criar, editar, excluir** usuários e
> **redefinir senha**. Consome os endpoints do passo 03. O acesso já é protegido pelo middleware
> (passo 04) e pelo backend (`get_current_admin`).

**Depende de:** 03, 04.
**Arquivos novos:** `pages/admin.vue`.

---

## 5.1 `pages/admin.vue`

```vue
<template>
  <div style="max-width:980px; margin:32px auto; padding:0 16px">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
      <div>
        <h1 style="margin:0; color:#0b5394">Painel do Administrador</h1>
        <p style="margin:4px 0 0; color:#64748b; font-size:13px">Gestão de usuários do PreFinance</p>
      </div>
      <div style="display:flex; gap:8px">
        <button class="btn btn-secondary btn-sm" @click="navigateTo('/')">← Voltar ao sistema</button>
        <button class="btn btn-primary btn-sm" @click="abrirNovo">+ Novo usuário</button>
      </div>
    </div>

    <div class="card">
      <table class="data-table" style="width:100%">
        <thead><tr>
          <th>Nome</th><th>Usuário</th><th>Status</th><th>Último acesso</th><th>Ações</th>
        </tr></thead>
        <tbody>
          <tr v-for="u in usuarios" :key="u.id">
            <td style="font-weight:600">{{ u.nome }}</td>
            <td>{{ u.username }}</td>
            <td>
              <span :style="{color: u.ativo ? '#16a34a' : '#ef4444'}">{{ u.ativo ? 'Ativo' : 'Inativo' }}</span>
            </td>
            <td>{{ u.ultimo_login ? formatarData(u.ultimo_login) : '—' }}</td>
            <td style="display:flex; gap:8px">
              <button class="btn btn-ghost btn-sm" @click="abrirEdicao(u)">Editar</button>
              <button class="btn btn-ghost btn-sm" style="color:#ef4444" @click="excluir(u)">Excluir</button>
            </td>
          </tr>
          <tr v-if="usuarios.length === 0"><td colspan="5" style="text-align:center; color:#94a3b8; padding:24px">Nenhum usuário cadastrado.</td></tr>
        </tbody>
      </table>
    </div>

    <!-- Modal criar/editar -->
    <div v-if="modalAberto" class="modal-overlay" @click.self="modalAberto = false"
         style="position:fixed; inset:0; background:rgba(15,23,42,.4); display:flex; align-items:center; justify-content:center; z-index:999">
      <div style="background:#fff; border-radius:12px; padding:24px; width:420px; max-width:92vw">
        <h3 style="margin:0 0 16px">{{ editando ? 'Editar usuário' : 'Novo usuário' }}</h3>

        <label class="lbl">Nome</label>
        <input v-model="form.nome" class="inp" />

        <label class="lbl">Usuário (login)</label>
        <input v-model="form.username" class="inp" :disabled="editando" />

        <label class="lbl">{{ editando ? 'Nova senha (deixe em branco para manter)' : 'Senha' }}</label>
        <input v-model="form.senha" type="password" class="inp" />

        <label style="display:flex; align-items:center; gap:8px; margin:8px 0 16px; font-size:14px">
          <input type="checkbox" v-model="form.ativo" /> Ativo
        </label>

        <p v-if="erro" style="color:#ef4444; font-size:13px">⚠️ {{ erro }}</p>

        <div style="display:flex; justify-content:flex-end; gap:8px">
          <button class="btn btn-secondary btn-sm" @click="modalAberto = false">Cancelar</button>
          <button class="btn btn-primary btn-sm" :disabled="salvando" @click="salvar">
            {{ salvando ? 'Salvando…' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

interface Usuario { id: string; username: string; nome: string; ativo: boolean; ultimo_login: string | null }

const usuarios = ref<Usuario[]>([])
const modalAberto = ref(false)
const editando = ref<string | null>(null) // id em edição
const salvando = ref(false)
const erro = ref('')
const form = reactive({ username: '', nome: '', senha: '', ativo: true })

const carregar = async () => { usuarios.value = await $fetch<Usuario[]>('/api/admin/usuarios') }
onMounted(carregar)

const abrirNovo = () => {
  editando.value = null; erro.value = ''
  Object.assign(form, { username: '', nome: '', senha: '', ativo: true })
  modalAberto.value = true
}
const abrirEdicao = (u: Usuario) => {
  editando.value = u.id; erro.value = ''
  Object.assign(form, { username: u.username, nome: u.nome, senha: '', ativo: u.ativo })
  modalAberto.value = true
}

const salvar = async () => {
  erro.value = ''; salvando.value = true
  try {
    if (editando.value) {
      const body: any = { nome: form.nome, ativo: form.ativo }
      if (form.senha) body.senha = form.senha
      await $fetch(`/api/admin/usuarios/${editando.value}`, { method: 'PUT', body })
    } else {
      await $fetch('/api/admin/usuarios', { method: 'POST', body: { ...form } })
    }
    modalAberto.value = false
    await carregar()
  } catch (e: any) {
    erro.value = e?.data?.detail || 'Erro ao salvar usuário.'
  } finally {
    salvando.value = false
  }
}

const excluir = async (u: Usuario) => {
  if (!confirm(`Excluir o usuário "${u.nome}"?`)) return
  await $fetch(`/api/admin/usuarios/${u.id}`, { method: 'DELETE' })
  await carregar()
}

const formatarData = (iso: string) => new Date(iso).toLocaleString('pt-BR')
</script>

<style scoped>
.lbl { display:block; font-size:13px; color:#334155; margin-top:10px }
.inp { width:100%; padding:9px; margin-top:4px; border:1px solid #cbd5e1; border-radius:8px }
</style>
```

> O middleware (passo 04) já bloqueia não-admins; o backend (`get_current_admin`) é a barreira real.
> "Redefinir senha" = abrir Editar e preencher o campo de nova senha.

---

## 5.2 Critérios de aceite

- [ ] Como admin, `/admin` lista os usuários e permite criar/editar/excluir.
- [ ] Criar usuário e depois logar com ele funciona.
- [ ] Editar e preencher "Nova senha" redefine a senha (o usuário loga com a nova).
- [ ] Marcar "Inativo" impede o login daquele usuário (backend já checa `ativo`).
- [ ] Usuário comum não consegue abrir `/admin` (redireciona).

## 5.3 Segurança / reversão

Reverter = apagar `pages/admin.vue`.

> Próximo: `06-autoria-criador-e-datahora.md`.
