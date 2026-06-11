<template>
  <div>
    <!-- ═══ SIDEBAR ═══ -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <div class="org-badge">Secretaria de Saúde</div>
        <h1>PreFinance</h1>
        <p>Gestão de Parcerias — OSC/ONG</p>
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
      <div class="sidebar-footer">
        <div class="user-card">
          <div class="user-avatar">AS</div>
          <div class="user-info"><div class="u-name">Ana Souza</div><div class="u-role">Gestora de Contratos</div></div>
        </div>
      </div>
    </aside>

    <!-- ═══ MAIN ═══ -->
    <div class="main-content">
      <div class="top-bar">
        <div class="top-bar-left">
          <h2 id="topbar-title">{{ topbarTitle }}</h2>
          <div class="breadcrumb" id="topbar-breadcrumb">PreFinance › {{ topbarBreadcrumb }}</div>
        </div>
        <div style="display:flex;gap:10px">
          <button class="btn btn-ghost btn-sm" @click="exportGeral()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>Exportar Geral (Excel)
          </button>
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
            @update-screen="setScreen"
          />
        </div>
      </div>
    </div>

    <!-- Modal de Edição -->
    <div v-if="isEditModalOpen" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-container">
        <EntityForm />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import EntityForm from '~/components/EntityForm.vue'
import { useEntity } from '~/composables/useEntity'

const activeScreen = ref('dashboard')
const isEditModalOpen = ref(false)
const { selectedEntity, selectEntity, entitiesList } = useEntity()

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
}

function novaParceria() {
  activeScreen.value = 'formalizacao'
}

function openEntity(id: string) {
  const entity = entitiesList.value.find(e => e.id === id)
  if (entity) {
    selectEntity(entity)
    isEditModalOpen.value = true
  }
}

function closeEditModal() {
  selectEntity(null)
  isEditModalOpen.value = false
}

import { watch } from 'vue'
watch(selectedEntity, (newVal) => {
  if (!newVal) {
    isEditModalOpen.value = false
  }
})

function exportGeral() {
  const link = document.createElement('a')
  link.href = '/api/export/geral'
  link.download = 'Prefinance_Exportacao_Geral.xlsx'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
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
