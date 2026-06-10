<template>
  <div class="entity-form-wrapper">
    <transition name="scale-fade" mode="out-in">
      <!-- Se nenhuma entidade estiver selecionada -->
      <div v-if="!selectedEntity" class="no-selection-card">
        <div class="card-icon">⚡</div>
        <h3 class="card-title">Nenhuma Entidade Selecionada</h3>
        <p class="card-description">Escolha uma empresa ou entidade do terceiro setor acima para carregar o formulário de edição e visualizar seus contextos integrados.</p>
      </div>

      <!-- Formulário Ativo com Dados Preenchidos -->
      <form v-else @submit.prevent="handleSubmit" class="entity-form">
        <!-- Cabeçalho Dinâmico -->
        <div class="form-header">
          <div class="title-section">
            <span class="badge">Ajuste Ativo</span>
            <h2 class="form-title">{{ formState.razao_social }}</h2>
            <p class="form-subtitle">ID Único: {{ formState.id }}</p>
          </div>
          <button type="button" @click="clearSelection" class="btn-close" title="Limpar seleção">Fechar ✕</button>
        </div>

        <div class="form-grid">
          <!-- Campo 1: Razão Social -->
          <div class="form-group full-width">
            <label for="form-razao-social" class="form-label">Razão Social</label>
            <input
              id="form-razao-social"
              type="text"
              v-model="formState.razao_social"
              required
              class="form-input"
              placeholder="Ex: Associação de Apoio Social..."
            />
          </div>

          <!-- Campo 2: CNPJ -->
          <div class="form-group">
            <label for="form-cnpj" class="form-label">CNPJ</label>
            <input
              id="form-cnpj"
              type="text"
              v-model="formState.cnpj"
              class="form-input"
              placeholder="00.000.000/0000-00"
            />
          </div>

          <!-- Campo 3: Responsável Principal -->
          <div class="form-group">
            <label for="form-responsavel" class="form-label">Responsável pela Entidade</label>
            <input
              id="form-responsavel"
              type="text"
              v-model="formState.responsavel_nome"
              class="form-input"
              placeholder="Nome do gestor da entidade"
            />
          </div>
        </div>

        <!-- Abas Internas para Configurações Extras (JSONB) -->
        <div class="tabs-container" v-if="hasExtras">
          <div class="tabs-header">
            <button
              v-if="hasFormalizacao"
              type="button"
              class="tab-btn"
              :class="{ 'tab-active': activeTab === 'formalizacao' }"
              @click="activeTab = 'formalizacao'"
            >
              📝 Processo de Formalização
            </button>
            <button
              v-if="hasParceria"
              type="button"
              class="tab-btn"
              :class="{ 'tab-active': activeTab === 'parceria' }"
              @click="activeTab = 'parceria'"
            >
              🤝 Dados da Parceria
            </button>
            <button
              v-if="hasFinanceiro"
              type="button"
              class="tab-btn"
              :class="{ 'tab-active': activeTab === 'financeiro' }"
              @click="activeTab = 'financeiro'"
            >
              💰 Fluxo de Repasses
            </button>
          </div>

          <div class="tab-content-panel">
            <transition name="fade-fast" mode="out-in">
              <!-- Sub-painel 1: Formalização -->
              <div v-if="activeTab === 'formalizacao' && hasFormalizacao" class="sub-panel">
                <div class="meta-grid">
                  <div class="meta-card">
                    <span class="meta-label">Status da Análise</span>
                    <span class="meta-value badge-status">{{ formState.configuracoes_extras.formalizacao.status }}</span>
                  </div>
                  <div class="meta-card">
                    <span class="meta-label">PA Formalização</span>
                    <span class="meta-value">{{ formState.configuracoes_extras.formalizacao.pa_formalizacao || 'Não formalizado' }}</span>
                  </div>
                  <div class="meta-card">
                    <span class="meta-label">Vereador Proponente</span>
                    <span class="meta-value">{{ formState.configuracoes_extras.formalizacao.vereador || 'Sem indicação' }}</span>
                  </div>
                  <div class="meta-card">
                    <span class="meta-label">Valor Destinado</span>
                    <span class="meta-value highlight-value">R$ {{ formState.configuracoes_extras.formalizacao.valor || '0,00' }}</span>
                  </div>
                </div>

                <div class="text-block">
                  <label class="form-label">Histórico de Movimentações</label>
                  <textarea 
                    v-model="formState.configuracoes_extras.formalizacao.historico" 
                    class="form-textarea" 
                    rows="4"
                  ></textarea>
                </div>
              </div>

              <!-- Sub-painel 2: Dados da Parceria -->
              <div v-else-if="activeTab === 'parceria' && hasParceria" class="sub-panel">
                <div class="meta-grid">
                  <div class="meta-card">
                    <span class="meta-label">Ajuste Vigente</span>
                    <span class="meta-value text-bold">{{ formState.configuracoes_extras.parceria.ajuste }}</span>
                  </div>
                  <div class="meta-card">
                    <span class="meta-label">Gestor da Parceria</span>
                    <span class="meta-value">{{ formState.configuracoes_extras.parceria.gestor }}</span>
                  </div>
                  <div class="meta-card">
                    <span class="meta-label">Início / Fim</span>
                    <span class="meta-value">{{ formState.configuracoes_extras.parceria.inicio_atividades }} até {{ formState.configuracoes_extras.parceria.termino_atividades }}</span>
                  </div>
                  <div class="meta-card">
                    <span class="meta-label font-bold">Meta de Atendimentos</span>
                    <span class="meta-value highlight-green">{{ formState.configuracoes_extras.parceria.meta_mensal }}</span>
                  </div>
                </div>

                <div v-if="formState.configuracoes_extras.parceria.metas_detalhadas" class="metas-detalhadas-section">
                  <h4 class="section-subtitle">Distribuição por Especialidade</h4>
                  <div class="badges-grid">
                    <div 
                      v-for="(valor, esp) in formState.configuracoes_extras.parceria.metas_detalhadas" 
                      :key="esp" 
                      class="especialidade-badge"
                    >
                      <span class="esp-name">{{ esp }}:</span>
                      <span class="esp-val">{{ valor }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Sub-painel 3: Repasse Financeiro -->
              <div v-else-if="activeTab === 'financeiro' && hasFinanceiro" class="sub-panel">
                <div class="financial-card">
                  <div class="financial-field">
                    <strong>Código SCIM:</strong>
                    <span>{{ formState.configuracoes_extras.financeiro_detalhes.codigo_scim }}</span>
                  </div>
                  <div class="financial-field">
                    <strong>PA Empenho:</strong>
                    <span>{{ formState.configuracoes_extras.financeiro_detalhes.pa_empenho }}</span>
                  </div>
                  <div class="financial-field block">
                    <strong>Objeto da Parceria:</strong>
                    <p class="objeto-desc">{{ formState.configuracoes_extras.financeiro_detalhes.objeto }}</p>
                  </div>
                </div>
              </div>
            </transition>
          </div>
        </div>

        <!-- Ações do Formulário -->
        <div class="form-actions">
          <span v-if="errorMsg" class="error-alert">⚠️ {{ errorMsg }}</span>
          <span v-if="successMsg" class="success-alert">✓ {{ successMsg }}</span>
          <button type="submit" :disabled="isLoading" class="btn-save">
            <span v-if="isLoading" class="spinner"></span>
            {{ isLoading ? 'Gravando...' : 'Salvar Alterações' }}
          </button>
        </div>
      </form>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { useEntity, type Entity } from '~/composables/useEntity'

const { selectedEntity, saveEntity, clearSelection, isLoading, errorMsg } = useEntity()

const formState = ref<Entity | null>(null)
const successMsg = ref<string | null>(null)
const activeTab = ref<'formalizacao' | 'parceria' | 'financeiro'>('formalizacao')

// Observa mudanças na entidade selecionada para popular o formulário
watch(selectedEntity, (newEntity) => {
  if (newEntity) {
    formState.value = JSON.parse(JSON.stringify(newEntity)) // Deep clone para isolar o formulário
    successMsg.value = null
    
    // Escolhe aba inicial ativa baseado nos dados disponíveis
    if (newEntity.configuracoes_extras?.formalizacao) {
      activeTab.value = 'formalizacao'
    } else if (newEntity.configuracoes_extras?.parceria) {
      activeTab.value = 'parceria'
    } else if (newEntity.configuracoes_extras?.financeiro_detalhes) {
      activeTab.value = 'financeiro'
    }
  } else {
    formState.value = null
  }
}, { immediate: true })

// Atalhos lógicos para verificar os dados
const hasExtras = computed(() => !!formState.value?.configuracoes_extras)
const hasFormalizacao = computed(() => !!formState.value?.configuracoes_extras?.formalizacao)
const hasParceria = computed(() => !!formState.value?.configuracoes_extras?.parceria)
const hasFinanceiro = computed(() => !!formState.value?.configuracoes_extras?.financeiro_detalhes)

const handleSubmit = async () => {
  if (!formState.value) return
  successMsg.value = null
  try {
    await saveEntity(formState.value)
    successMsg.value = 'Entidade gravada e atualizada no banco!'
    setTimeout(() => {
      successMsg.value = null
    }, 4000)
  } catch (err) {
    // Erros já tratados no composable
  }
}
</script>

<style scoped>
.entity-form-wrapper {
  --primary-color: #6366f1;
  --primary-hover: #4f46e5;
  --bg-panel: #ffffff;
  --bg-subpanel: #f8fafc;
  --text-color: #1e293b;
  --text-muted: #64748b;
  --border-light: rgba(99, 102, 241, 0.1);
  --success-color: #10b981;
  --error-color: #ef4444;
  --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);

  width: 100%;
  font-family: 'Outfit', 'Inter', sans-serif;
  color: var(--text-color);
}

@media (prefers-color-scheme: dark) {
  .entity-form-wrapper {
    --bg-panel: #1e293b;
    --bg-subpanel: #0f172a;
    --text-color: #f1f5f9;
    --text-muted: #94a3b8;
    --border-light: rgba(255, 255, 255, 0.08);
  }
}

/* Card sem seleção */
.no-selection-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  border-radius: 16px;
  border: 2px dashed var(--border-light);
  background: var(--bg-panel);
  text-align: center;
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(8px);
}

.card-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, var(--text-color) 30%, var(--primary-color) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.card-description {
  font-size: 0.95rem;
  color: var(--text-muted);
  max-width: 420px;
}

/* Formulário Principal */
.entity-form {
  background: var(--bg-panel);
  border-radius: 16px;
  border: 1px solid var(--border-light);
  padding: 2rem;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid var(--border-light);
  padding-bottom: 1.25rem;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.badge {
  align-self: flex-start;
  font-size: 0.7rem;
  font-weight: 700;
  background: rgba(99, 102, 241, 0.15);
  color: var(--primary-color);
  padding: 0.25rem 0.6rem;
  border-radius: 9999px;
  text-transform: uppercase;
}

.form-title {
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0.25rem 0;
}

.form-subtitle {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: monospace;
}

.btn-close {
  background: none;
  border: none;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: rgba(239, 68, 68, 0.08);
  color: var(--error-color);
}

/* Grid layout form */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.full-width {
  grid-column: span 2;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--text-muted);
}

.form-input, .form-textarea {
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  border-radius: 10px;
  border: 1px solid var(--border-light);
  background: var(--bg-subpanel);
  color: var(--text-color);
  transition: all 0.25s ease;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  background: var(--bg-panel);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
}

/* Painel de Abas */
.tabs-container {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  overflow: hidden;
  background: var(--bg-subpanel);
}

.tabs-header {
  display: flex;
  border-bottom: 1px solid var(--border-light);
  background: rgba(0, 0, 0, 0.02);
}

.tab-btn {
  flex: 1;
  padding: 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  border: none;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: rgba(99, 102, 241, 0.04);
}

.tab-active {
  background: var(--bg-panel) !important;
  color: var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
}

.tab-content-panel {
  padding: 1.5rem;
  background: var(--bg-panel);
}

/* Meta Data Panels */
.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.meta-card {
  padding: 1rem;
  background: var(--bg-subpanel);
  border-radius: 10px;
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.meta-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 600;
}

.meta-value {
  font-weight: 600;
  font-size: 0.95rem;
}

.highlight-value {
  color: var(--primary-color);
  font-weight: 800;
  font-size: 1.1rem;
}

.highlight-green {
  color: var(--success-color);
  font-weight: 800;
  font-size: 1.1rem;
}

.badge-status {
  align-self: flex-start;
  padding: 0.15rem 0.5rem;
  font-size: 0.75rem;
  border-radius: 6px;
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
  font-weight: 700;
}

.metas-detalhadas-section {
  margin-top: 1.5rem;
  border-top: 1px solid var(--border-light);
  padding-top: 1rem;
}

.section-subtitle {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}

.badges-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.especialidade-badge {
  display: flex;
  gap: 0.5rem;
  background: var(--bg-subpanel);
  border: 1px solid var(--border-light);
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
}

.esp-name {
  color: var(--text-muted);
}

.esp-val {
  color: var(--primary-color);
}

.financial-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.financial-field {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-light);
  padding-bottom: 0.5rem;
}

.financial-field.block {
  flex-direction: column;
  border: none;
  gap: 0.25rem;
}

.objeto-desc {
  font-size: 0.875rem;
  color: var(--text-muted);
  line-height: 1.45;
}

/* Actions e alerts */
.form-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 1.5rem;
  border-top: 1px solid var(--border-light);
  padding-top: 1.25rem;
}

.btn-save {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 4px 10px rgba(99, 102, 241, 0.2);
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(99, 102, 241, 0.3);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.success-alert {
  color: var(--success-color);
  font-weight: 600;
  font-size: 0.9rem;
}

.error-alert {
  color: var(--error-color);
  font-weight: 600;
  font-size: 0.9rem;
}

/* Transições com efeitos premium */
.scale-fade-enter-active, .scale-fade-leave-active {
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.scale-fade-enter-from, .scale-fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.fade-fast-enter-active, .fade-fast-leave-active {
  transition: opacity 0.15s ease;
}
.fade-fast-enter-from, .fade-fast-leave-to {
  opacity: 0;
}
</style>
