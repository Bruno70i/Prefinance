<template>
  <div>
    <!-- ═══ SIDEBAR BACKDROP ═══ -->
    <div v-if="sidebarAberta" class="sidebar-backdrop" @click="sidebarAberta = false"></div>

    <!-- ═══ SIDEBAR ═══ -->
    <aside class="sidebar" :class="{ 'sidebar-open': sidebarAberta }">
      <div class="sidebar-logo">
        <div class="org-badge">Bem Vindo</div>
        <h1>PreFinance</h1>
        <p>Gestão de Parcerias</p>
      </div>
      <div class="nav-section-label">Visão Geral</div>
      <button class="nav-item" :class="{ active: activeScreen === 'dashboard' }" @click="setScreen('dashboard')">
        <span class="nav-icon-wrap">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
        </span>
        <div><div>Dashboard de Consulta</div><div class="nav-label-sub">Visão geral e busca</div></div>
      </button>
      <div class="nav-section-label">Módulos</div>
      <button class="nav-item" :class="{ active: activeScreen === 'formalizacao' }" @click="novaParceria()">
        <span class="nav-num">1</span>
        <div><div>Cadastro de Formalização</div><div class="nav-label-sub">Dados jurídicos da entidade</div></div>
      </button>
      <button class="nav-item" :class="{ active: activeScreen === 'parceria' }" @click="setScreen('parceria')">
        <span class="nav-num">2</span>
        <div><div>Dados da Parceria</div><div class="nav-label-sub">Contrato, filial e metas</div></div>
      </button>
      <button class="nav-item" :class="{ active: activeScreen === 'financeiro' }" @click="setScreen('financeiro')">
        <span class="nav-num">3</span>
        <div><div>Controle Financeiro</div><div class="nav-label-sub">Repasses e prestação de contas</div></div>
      </button>
      <div class="sidebar-footer" style="padding: 16px; border-top: 1px solid #e2e8f0; display: flex; flex-direction: column; gap: 12px; background: #f8fafc;">
        <div class="user-card" style="display: flex; align-items: center; gap: 10px;">
          <div class="user-avatar" style="width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%); color: #ffffff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; flex-shrink: 0; box-shadow: 0 2px 4px rgba(29,78,216,0.15);">
            {{ obterIniciais(usuario?.nome || usuario?.username || 'U') }}
          </div>
          <div class="user-info" style="flex: 1; min-width: 0;">
            <div class="u-name" style="font-weight: 700; color: #0f172a; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
              {{ usuario?.nome || usuario?.username || 'Usuário' }}
            </div>
            <div class="u-role" style="color: #475569; font-size: 10px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">
              {{ isAdmin ? 'Administrador' : 'Colaborador' }}
            </div>
          </div>
        </div>
        <div style="display: flex; gap: 8px;">
          <button v-if="isAdmin" @click="navigateTo('/admin')" class="btn btn-ghost btn-sm" style="flex: 1; padding: 8px; font-size: 12px; font-weight: 600; color: #1e40af; border: 1px solid #bfdbfe; border-radius: 8px; background: #eff6ff; cursor: pointer; transition: all 0.2s;">
            Painel Admin
          </button>
          <button @click="sair" class="btn btn-ghost btn-sm" style="flex: 1; padding: 8px; font-size: 12px; font-weight: 600; color: #c53030; border: 1px solid #feb2b2; border-radius: 8px; background: #fff5f5; cursor: pointer; transition: all 0.2s;">
            Sair
          </button>
        </div>
      </div>
    </aside>

    <!-- ═══ MAIN ═══ -->
    <div class="main-content">
      <div class="top-bar">
        <div style="display:flex;align-items:center;gap:12px">
          <button class="menu-toggle" @click="sidebarAberta = !sidebarAberta" aria-label="Abrir Menu">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>
          <div class="top-bar-left">
            <h2 id="topbar-title">{{ topbarTitle }}</h2>
            <div class="breadcrumb" id="topbar-breadcrumb">PreFinance › {{ topbarBreadcrumb }}</div>
          </div>
        </div>
        <div style="display:flex;gap:10px">
          <button class="btn btn-primary btn-sm" @click="novaParceria()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>Nova Parceria
          </button>
        </div>
      </div>

      <div class="page-body">
        <div v-if="activeScreen === 'dashboard'" class="screen active">
          <EntitySelector @edit-entity="openEntity" />
        </div>

        <div v-else class="screen active">
          <EntityCreateForm 
            :active-screen="activeScreen"
            :modo="editId ? 'editar' : 'criar'"
            :entidade-id="editId"
            @update-screen="setScreen"
            @salvo="onSalvo"
          />
        </div>
      </div>
    </div>
    <AssistenteIA />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuth } from '~/composables/useAuth'

const { usuario, isAdmin, logout } = useAuth()
const sidebarAberta = ref(false)

const sair = async () => {
  await logout()
  await navigateTo('/login')
}

const obterIniciais = (nomeCompleto: string) => {
  const partes = nomeCompleto.trim().split(/\s+/)
  if (partes.length >= 2) {
    return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase()
  }
  return partes[0] ? partes[0].slice(0, 2).toUpperCase() : 'U'
}

const activeScreen = ref('dashboard')
const editId = ref<string | null>(null)

const topbarTitle = computed(() => {
  if (activeScreen.value === 'dashboard') return 'Dashboard de Consulta'
  if (activeScreen.value === 'formalizacao') return 'Cadastro de Formalização'
  if (activeScreen.value === 'parceria') return 'Dados da Parceria'
  if (activeScreen.value === 'financeiro') return 'Controle Financeiro'
  return 'PreFinance'
})

const topbarBreadcrumb = computed(() => {
  if (activeScreen.value === 'dashboard') return 'Início'
  if (activeScreen.value === 'formalizacao') return 'Módulos › Cadastro'
  if (activeScreen.value === 'parceria') return 'Módulos › Parceria'
  if (activeScreen.value === 'financeiro') return 'Módulos › Financeiro'
  return 'Módulos'
})

function setScreen(screen: string) {
  activeScreen.value = screen
  sidebarAberta.value = false
}

function novaParceria() {
  editId.value = null
  activeScreen.value = 'formalizacao'
  sidebarAberta.value = false
}

function openEntity(id: string) {
  editId.value = id
  activeScreen.value = 'formalizacao'
  sidebarAberta.value = false
}

function onSalvo() {
  editId.value = null
  activeScreen.value = 'dashboard'
  sidebarAberta.value = false
}

useHead({
  title: 'Gestão de Entidades | PreFinance',
  meta: [
    { name: 'description', content: 'Painel centralizado de controle, cadastro e edição de convênios das entidades do terceiro setor.' }
  ]
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-container {
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 16px;
  background: transparent;
}
</style>

<style>
/* Removeremos a folha de estilo local já que incluímos globalmente o main.css */
</style>
