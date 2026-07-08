<template>
  <div style="max-width: 1020px; margin: 40px auto; padding: 0 24px;">
    <!-- Cabeçalho do Painel -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px;">
      <div>
        <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #F5791E; letter-spacing: 1px;">Área Administrativa</div>
        <h1 style="margin: 4px 0 0; color: #0f172a; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">Painel de Gestão de Usuários</h1>
        <p style="margin: 4px 0 0; color: #64748b; font-size: 14px;">Gerencie os acessos, crie novos colaboradores e redefina credenciais do PreFinance.</p>
      </div>
      <div style="display: flex; gap: 10px;">
        <button class="btn btn-secondary btn-sm" @click="navigateTo('/')" style="display: flex; align-items: center; gap: 6px;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Voltar ao Sistema
        </button>
        <button class="btn btn-primary btn-sm" @click="abrirNovo" style="display: flex; align-items: center; gap: 6px;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Novo Usuário
        </button>
      </div>
    </div>

    <!-- Tabela de Usuários -->
    <div class="card" style="border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.03); border-radius: 12px; overflow: hidden;">
      <table class="data-table" style="width: 100%; border-collapse: collapse;">
        <thead>
          <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
            <th style="padding: 14px 16px; text-align: left; font-weight: 600; color: #475569; font-size: 13px;">Nome Completo</th>
            <th style="padding: 14px 16px; text-align: left; font-weight: 600; color: #475569; font-size: 13px;">Nome de Usuário</th>
            <th style="padding: 14px 16px; text-align: left; font-weight: 600; color: #475569; font-size: 13px;">Status</th>
            <th style="padding: 14px 16px; text-align: left; font-weight: 600; color: #475569; font-size: 13px;">Último Acesso</th>
            <th style="padding: 14px 16px; text-align: right; font-weight: 600; color: #475569; font-size: 13px;">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in usuarios" :key="u.id" style="border-bottom: 1px solid #f1f5f9; transition: background 0.2s;">
            <td style="padding: 14px 16px; font-weight: 600; color: #0f172a; font-size: 14px;">{{ u.nome }}</td>
            <td style="padding: 14px 16px; color: #475569; font-size: 14px; font-family: monospace;">{{ u.username }}</td>
            <td style="padding: 14px 16px; font-size: 14px;">
              <span :style="{
                background: u.ativo ? '#dcfce7' : '#fee2e2',
                color: u.ativo ? '#15803d' : '#b91c1c',
                padding: '4px 8px',
                borderRadius: '6px',
                fontSize: '12px',
                fontWeight: '600'
              }">
                {{ u.ativo ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td style="padding: 14px 16px; color: #64748b; font-size: 13px;">
              {{ u.ultimo_login ? formatarData(u.ultimo_login) : 'Nunca acessou' }}
            </td>
            <td style="padding: 14px 16px; text-align: right;">
              <div style="display: flex; gap: 8px; justify-content: flex-end;">
                <button class="btn btn-ghost btn-sm" @click="abrirEdicao(u)" style="padding: 5px 10px; font-size: 13px;">
                  Editar
                </button>
                <button class="btn btn-ghost btn-sm" style="color: #ef4444; padding: 5px 10px; font-size: 13px;" @click="excluir(u)">
                  Excluir
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="usuarios.length === 0">
            <td colspan="5" style="text-align: center; color: #94a3b8; padding: 36px; font-size: 14px;">
              Nenhum usuário cadastrado além do administrador padrão.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Criar / Editar Usuário -->
    <div v-if="modalAberto" class="modal-overlay" @click.self="modalAberto = false">
      <div class="modal-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
          <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: #0f172a;">
            {{ editando ? 'Editar Usuário' : 'Novo Usuário' }}
          </h3>
          <button @click="modalAberto = false" class="close-btn">&times;</button>
        </div>

        <div style="display: flex; flex-direction: column; gap: 14px;">
          <div class="form-group">
            <label class="lbl">Nome Completo</label>
            <input v-model="form.nome" class="inp" placeholder="Ex: Ana Souza" />
          </div>

          <div class="form-group">
            <label class="lbl">Nome de Usuário (Login)</label>
            <input v-model="form.username" class="inp" :disabled="!!editando" placeholder="Ex: anasouza" />
          </div>

          <div class="form-group">
            <label class="lbl">
              {{ editando ? 'Nova Senha (deixe em branco para manter)' : 'Senha de Acesso' }}
            </label>
            <input v-model="form.senha" type="password" class="inp" placeholder="Mínimo de 4 caracteres..." />
          </div>

          <div style="margin: 6px 0;">
            <label style="display: flex; align-items: center; gap: 8px; font-size: 14px; color: #334155; cursor: pointer;">
              <input type="checkbox" v-model="form.ativo" style="width: 16px; height: 16px; border-radius: 4px;" />
              Permitir que este usuário faça login (Ativo)
            </label>
          </div>

          <transition name="fade">
            <p v-if="erro" style="color: #ef4444; font-size: 13px; margin: 4px 0 0; display: flex; align-items: center; gap: 6px;">
              <span>⚠️</span> <span>{{ erro }}</span>
            </p>
          </transition>
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 24px; border-top: 1px solid #f1f5f9; padding-top: 16px;">
          <button class="btn btn-secondary btn-sm" @click="modalAberto = false">Cancelar</button>
          <button class="btn btn-primary btn-sm" :disabled="salvando" @click="salvar">
            {{ salvando ? 'Salvando...' : 'Salvar Usuário' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

interface Usuario { 
  id: string; 
  username: string; 
  nome: string; 
  ativo: boolean; 
  ultimo_login: string | null 
}

const usuarios = ref<Usuario[]>([])
const modalAberto = ref(false)
const editando = ref<string | null>(null) // ID do usuário em edição
const salvando = ref(false)
const erro = ref('')
const form = reactive({ username: '', nome: '', senha: '', ativo: true })

const carregar = async () => {
  try {
    usuarios.value = await $fetch<Usuario[]>('/api/admin/usuarios')
  } catch (err: any) {
    alert(err?.data?.detail || 'Erro ao carregar lista de usuários.')
  }
}

onMounted(carregar)

const abrirNovo = () => {
  editando.value = null
  erro.value = ''
  Object.assign(form, { username: '', nome: '', senha: '', ativo: true })
  modalAberto.value = true
}

const abrirEdicao = (u: Usuario) => {
  editando.value = u.id
  erro.value = ''
  Object.assign(form, { username: u.username, nome: u.nome, senha: '', ativo: u.ativo })
  modalAberto.value = true
}

const salvar = async () => {
  erro.value = ''
  salvando.value = true
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
  if (!confirm(`Excluir permanentemente o usuário "${u.nome}"?`)) return
  try {
    await $fetch(`/api/admin/usuarios/${u.id}`, { method: 'DELETE' })
    await carregar()
  } catch (err: any) {
    alert(err?.data?.detail || 'Erro ao excluir usuário.')
  }
}

const formatarData = (iso: string) => {
  return new Date(iso).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 28px;
  width: 440px;
  max-width: 92vw;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border: 1px solid #f1f5f9;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
  padding: 0;
}

.close-btn:hover {
  color: #0f172a;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.lbl {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.inp {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  outline: none;
  font-size: 14px;
  transition: all 0.2s;
  background: #f8fafc;
}

.inp:focus {
  border-color: #F5791E;
  box-shadow: 0 0 0 3px rgba(245, 121, 30, 0.12);
  background: #ffffff;
}

.inp:disabled {
  background: #e2e8f0;
  color: #64748b;
  cursor: not-allowed;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
