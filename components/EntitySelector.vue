<template>
  <div>
    <!-- Hero Search -->
    <div class="search-hero">
      <div class="search-eyebrow">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        Busca Principal <span class="search-eyebrow-line"></span>
      </div>
      <div class="search-input-wrap">
        <span class="search-icon-abs">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        </span>
        <input 
          type="text" 
          id="main-search" 
          v-model="searchQuery"
          placeholder="Digite o Processo Administrativo (PA) ou CNPJ Raiz para pesquisar instantaneamente..." 
        />
        <span class="search-kbd">⌘ K</span>
      </div>
      <div class="search-hints">
        <span style="display:flex;align-items:center;gap:5px">Ex. PA: <strong style="color:#475569;margin-left:3px">PA-2024/0012</strong></span>
        <span style="display:flex;align-items:center;gap:5px">Ex. CNPJ: <strong style="color:#475569;margin-left:3px">12.345.678</strong></span>
        <span id="search-count" style="font-size:12px;color:#3b82f6;font-weight:600;margin-left:auto" v-if="searchQuery">
          {{ filteredEntities.length }} resultado(s)
        </span>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <div class="kpi-card" :class="{ 'active-filter': statusFilter === 'todos' }" @click="statusFilter = 'todos'">
        <div class="kpi-top">
          <div class="kpi-icon-box" style="background:#eff6ff">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          </div>
          <span class="kpi-trend trend-neutral">Total</span>
        </div>
        <div class="kpi-value">{{ entitiesList.length }}</div>
        <div class="kpi-label">Total de Parcerias</div>
        <div class="kpi-sub">Clique para ver todas</div>
      </div>
      
      <div class="kpi-card" :class="{ 'active-filter': statusFilter === 'Ativa' }" @click="statusFilter = 'Ativa'">
        <div class="kpi-top">
          <div class="kpi-icon-box" style="background:#dcfce7">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
          <span class="kpi-trend trend-up">Ativas</span>
        </div>
        <div class="kpi-value">{{ countByStatus('Ativa') }}</div>
        <div class="kpi-label">Parcerias Ativas</div>
        <div class="kpi-sub">Clique para filtrar</div>
      </div>
      

      
      <div class="kpi-card" style="cursor:default">
        <div class="kpi-top">
          <div class="kpi-icon-box" style="background:#fef9c3">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ca8a04" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
          <span class="kpi-trend trend-neutral">Geral</span>
        </div>
        <div class="kpi-value" style="font-size:22px">R$ {{ formatCurrency(totalVolume) }}</div>
        <div class="kpi-label">Volume Repassado</div>
        <div class="kpi-sub">Soma dos contratos</div>
      </div>
    </div>

    <!-- Table -->
    <div class="card">
      <div class="card-header">
        <div>
          <h3>Parcerias Cadastradas</h3>
          <p>{{ filteredEntities.length }} registros</p>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
          <button class="filter-pill" :class="{ active: statusFilter === 'todos' }" @click="statusFilter = 'todos'">Todos</button>
          <button class="filter-pill" :class="{ active: statusFilter === 'Ativa' }" @click="statusFilter = 'Ativa'"><span style="width:7px;height:7px;background:#16a34a;border-radius:50%;display:inline-block"></span>Ativa</button>
          <button class="filter-pill" :class="{ active: statusFilter === 'Em Análise' }" @click="statusFilter = 'Em Análise'"><span style="width:7px;height:7px;background:#ca8a04;border-radius:50%;display:inline-block"></span>Em Análise</button>

        </div>
      </div>
      
      <div style="overflow-x:auto">
        <table class="data-table">
          <thead>
            <tr>
              <th>Nº PA</th>
              <th>Entidade</th>
              <th>CNPJ</th>
              <th>Resp. Legal</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entity in filteredEntities" :key="entity.id">
              <td style="font-family:'DM Mono', monospace; font-weight: 500;">
                {{ entity.numero_emenda || entity.configuracoes_extras?.pa_emenda || 'Sem PA' }}
              </td>
              <td style="font-weight: 600;">{{ entity.razao_social }}</td>
              <td>{{ entity.cnpj }}</td>
              <td>{{ entity.responsavel_nome || '-' }}</td>
              <td>
                <span class="badge" :class="getBadgeClass(entity.situacao)">
                  <span class="badge-dot"></span> {{ entity.situacao || 'Desconhecido' }}
                </span>
              </td>
              <td>
                <div style="display:flex; gap:8px">
                  <button class="btn btn-ghost btn-sm" @click="$emit('edit-entity', entity.id)">
                    Editar
                  </button>
                  <button class="btn btn-ghost btn-sm" @click="exportarEntidade(entity)">
                    Exportar
                  </button>
                  <button class="btn btn-ghost btn-sm" style="color:#ef4444" @click="confirmDelete(entity.id, entity.razao_social)" :disabled="isDeletingId === entity.id">
                    {{ isDeletingId === entity.id ? 'Excluindo...' : 'Excluir' }}
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredEntities.length === 0">
              <td colspan="6" style="text-align: center; color: #94a3b8; padding: 30px;">
                Nenhum registro encontrado.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="pagination">
        <span class="pagination-info">Mostrando <span>{{ filteredEntities.length }}</span> registro(s)</span>
        <div class="pagination-btns">
          <button class="pg-btn">‹</button>
          <button class="pg-btn active">1</button>
          <button class="pg-btn">›</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useEntity, type Entity } from '~/composables/useEntity'

const emit = defineEmits(['edit-entity'])

const { entitiesList, isLoading, fetchEntities, deleteEntity } = useEntity()
const isDeletingId = ref<string | null>(null)

const searchQuery = ref('')
const statusFilter = ref('todos')

onMounted(async () => {
  await fetchEntities()
})

function exportarEntidade(entity: Entity) {
  const nome = (entity.razao_social || 'Entidade').replace(/ /g, '_')
  const link = document.createElement('a')
  link.href = `/api/export/entidade/${entity.id}?etapa=todos`
  link.download = `Prefinance_${nome}.xlsx`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

async function confirmDelete(id: string, name: string) {
  if (confirm(`Tem certeza que deseja excluir a entidade "${name}"? Esta ação removerá em cascata os dados da parceria e os lançamentos financeiros relacionados.`)) {
    isDeletingId.value = id
    try {
      await deleteEntity(id)
    } catch (err) {
      alert('Erro ao excluir a entidade.')
    } finally {
      isDeletingId.value = null
    }
  }
}

const filteredEntities = computed(() => {
  let list = entitiesList.value

  if (statusFilter.value !== 'todos') {
    if (statusFilter.value === 'Ativa') {
      list = list.filter(e => getBadgeClass(e.situacao || '') === 'badge-ativa')
    } else if (statusFilter.value === 'Em Análise') {
      list = list.filter(e => getBadgeClass(e.situacao || '') === 'badge-em_analise')
    } else {
      list = list.filter(e => e.situacao === statusFilter.value)
    }
  }

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase().trim()
    list = list.filter(e => 
      e.razao_social.toLowerCase().includes(q) || 
      (e.cnpj && e.cnpj.includes(q)) ||
      (e.numero_emenda && e.numero_emenda.toLowerCase().includes(q)) ||
      (e.configuracoes_extras?.pa_emenda && e.configuracoes_extras.pa_emenda.toLowerCase().includes(q))
    )
  }

  return list
})

function countByStatus(filterType: string) {
  if (filterType === 'Ativa') {
    return entitiesList.value.filter(e => getBadgeClass(e.situacao || '') === 'badge-ativa').length
  }
  return entitiesList.value.filter(e => e.situacao === filterType).length
}

const totalVolume = computed(() => {
  return entitiesList.value.reduce((acc, entity) => {
    // Tenta usar entity.valor direto, faz fallback pra configuracoes_extras.valor se existir legado
    const valStr = entity.valor !== undefined && entity.valor !== null ? entity.valor : (entity.configuracoes_extras?.valor || 0)
    
    if (typeof valStr === 'string') {
      // Remove tudo exceto números, vírgula e ponto
      let cleanStr = valStr.replace(/[^\d.,]/g, '')
      // Se tiver vírgula (formato brasileiro 1.000,50)
      if (cleanStr.includes(',')) {
        cleanStr = cleanStr.replace(/\./g, '') // remove pontos de milhar
        cleanStr = cleanStr.replace(',', '.')  // troca vírgula decimal por ponto
      }
      return acc + (parseFloat(cleanStr) || 0)
    }
    return acc + (Number(valStr) || 0)
  }, 0)
})

function formatCurrency(val: number) {
  return val.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function getBadgeClass(status: string) {
  if (!status) return 'badge-encerrada'
  const st = status.toLowerCase()
  if (st.includes('fomento') || st.includes('colaboração') || st.includes('colaboracao') || st.includes('convenio') || st.includes('convênio') || st.includes('aprovado') || st.includes('ativa')) return 'badge-ativa'
  if (st.includes('análise') || st.includes('formalização')) return 'badge-em_analise'
  return 'badge-encerrada'
}
</script>

<style scoped>
/* Os estilos principais já estão globais no main.css */
</style>
