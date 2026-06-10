<template>
  <div class="entity-create-container">
    
    <!-- Alertas de Feedback da API -->
    <div v-if="apiSuccess" class="toast success show" style="position:relative; margin-bottom: 20px; transform:none; opacity:1; pointer-events:auto; bottom:0; right:0;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      <span>{{ apiSuccess }}</span>
      <button type="button" @click="apiSuccess = ''" style="margin-left:auto; background:none; border:none; color:white; cursor:pointer;">&times;</button>
    </div>

    <div v-if="apiError" class="toast error show" style="position:relative; margin-bottom: 20px; transform:none; opacity:1; pointer-events:auto; bottom:0; right:0;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <span>{{ apiError }}</span>
      <button type="button" @click="apiError = ''" style="margin-left:auto; background:none; border:none; color:white; cursor:pointer;">&times;</button>
    </div>

    <!-- Formulário Principal -->
    <form @submit.prevent="submitForm">

      <!-- ═══════════ SCREEN: FORMALIZAÇÃO (Passo 1) ═══════════ -->
      <div v-if="currentStep === 1" class="screen active">
        <div class="step-bar">
          <div class="step active">
            <div class="step-circle">1</div><span>Formalização</span>
          </div>
          <div class="step-line"></div>
          <div class="step">
            <div class="step-circle">2</div><span>Dados da Parceria</span>
          </div>
          <div class="step-line"></div>
          <div class="step">
            <div class="step-circle">3</div><span>Controle Financeiro</span>
          </div>
        </div>

        <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px">
          <div style="width:44px;height:44px;border-radius:11px;background:#eff6ff;display:flex;align-items:center;justify-content:center;flex-shrink:0">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          </div>
          <div>
            <h2 style="font-size:20px;font-weight:700;color:#1e293b">Cadastro de Formalização</h2>
            <p style="font-size:13px;color:#94a3b8">Preencha os dados jurídicos para iniciar o cadastro</p>
          </div>
        </div>

        <div style="display:grid;gap:20px">
          <div class="card">
            <div class="card-header"><div><h3>Identificação do Processo</h3><p>Dados do processo administrativo e vínculo com a emenda</p></div></div>
            <div class="card-body">
              <div class="form-grid form-grid-3">
                <div>
                  <label class="field-label">Nº do Processo / PA</label>
                  <input type="text" v-model="form.pa_formalizacao" placeholder="Ex: PA-2025/0042"/>
                </div>
                <div>
                  <label class="field-label">Situação<span class="field-required">*</span></label>
                  <select v-model="form.situacao" required>
                    <option value="">Selecione…</option>
                    <option value="Em Análise">Em Análise</option>
                    <option value="Aprovado">Aprovado</option>
                    <option value="Em Formalização">Em Formalização</option>
                    <option value="Pendente">Pendente</option>
                  </select>
                </div>
                <div>
                  <label class="field-label">Número da Emenda</label>
                  <input type="text" v-model="form.numero_emenda" placeholder="Ex: Emenda 01/2025"/>
                </div>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header"><div><h3>Dados da Entidade</h3><p>Informações jurídicas centralizadas — CNPJ Raiz</p></div></div>
            <div class="card-body">
              <div class="form-grid form-grid-3">
                <div>
                  <label class="field-label">CNPJ Raiz<span class="field-required">*</span></label>
                  <input type="text" v-model="form.cnpj" placeholder="00.000.000/0000-00" @input="handleCnpjInput" required />
                  <p class="input-hint" style="color:#ef4444" v-if="errors.cnpj">{{ errors.cnpj }}</p>
                </div>
                <div style="grid-column:span 2">
                  <label class="field-label">Razão Social / Nome da Entidade<span class="field-required">*</span></label>
                  <input type="text" v-model="form.razao_social" placeholder="Nome completo conforme CNPJ" @input="clearError('razao_social')" required />
                  <p class="input-hint" style="color:#ef4444" v-if="errors.razao_social">{{ errors.razao_social }}</p>
                </div>
                <div>
                  <label class="field-label">E-mail Institucional</label>
                  <input type="email" v-model="form.configuracoes_extras.email_contato" placeholder="entidade@exemplo.org.br"/>
                </div>
                <div>
                  <label class="field-label">Telefone / WhatsApp</label>
                  <input type="text" v-model="form.configuracoes_extras.telefone" placeholder="(00) 00000-0000" @input="handlePhoneInput" />
                </div>
                <div>
                  <label class="field-label">Representante Legal</label>
                  <input type="text" v-model="form.responsavel_nome" placeholder="Nome completo" />
                </div>
              </div>
            </div>
          </div>

          <div style="display:flex;justify-content:flex-end;gap:12px">
            <button type="button" class="btn btn-secondary" @click="$emit('update-screen', 'dashboard')">Cancelar</button>
            <button type="button" class="btn btn-primary" @click="nextStep">
              Próximo
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
            </button>
          </div>
        </div>
      </div>

      <!-- ═══════════ SCREEN: DADOS DA PARCERIA (Passo 2) ═══════════ -->
      <div v-if="currentStep === 2" class="screen active">
        <div class="step-bar">
          <div class="step done">
            <div class="step-circle">✓</div><span>Formalização</span>
          </div>
          <div class="step-line done"></div>
          <div class="step active">
            <div class="step-circle">2</div><span>Dados da Parceria</span>
          </div>
          <div class="step-line"></div>
          <div class="step">
            <div class="step-circle">3</div><span>Controle Financeiro</span>
          </div>
        </div>

        <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px">
          <div style="width:44px;height:44px;border-radius:11px;background:#eff6ff;display:flex;align-items:center;justify-content:center;flex-shrink:0">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          </div>
          <div>
            <h2 style="font-size:20px;font-weight:700;color:#1e293b">Dados da Parceria</h2>
            <p style="font-size:13px;color:#94a3b8">Termo, vigência, fiscal e metas</p>
          </div>
        </div>

        <div style="display:grid;gap:20px">
          <div class="card">
            <div class="card-header"><div><h3>Unidade Executora (Filial)</h3><p>Identifica qual filial executará este contrato</p></div></div>
            <div class="card-body">
              <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:10px;padding:16px 18px;margin-bottom:20px">
                <div class="form-grid form-grid-3">
                  <div>
                    <label class="field-label">Nº do Processo / PA</label>
                    <input type="text" :value="form.pa_formalizacao" readonly style="background:#f1f5f9;color:#475569;" />
                  </div>
                  <div>
                    <label class="field-label">CNPJ Raiz</label>
                    <input type="text" :value="form.cnpj" readonly style="background:#f1f5f9;color:#475569;" />
                  </div>
                  <div>
                    <label class="field-label">Razão Social / Nome da ONG</label>
                    <input type="text" :value="form.razao_social" readonly style="background:#f1f5f9;color:#475569;" />
                  </div>
                </div>
              </div>

              <div class="form-grid form-grid-2">
                <div>
                  <label class="field-label">Ajuste / Termo</label>
                  <input type="text" v-model="form.parceria.ajuste_termo" placeholder="Ex: TERMO DE FOMENTO 29/2026"/>
                </div>
                <div>
                  <label class="field-label">Gestor da Parceria</label>
                  <input type="text" v-model="form.parceria.gestor_parceria" placeholder="Nome do Gestor"/>
                </div>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header"><div><h3>Objeto, Vigência e Especialidades</h3></div></div>
            <div class="card-body">
              <div class="form-grid" style="gap:18px">
                <div>
                  <label class="field-label">Projeto / Objeto<span class="field-required">*</span></label>
                  <textarea v-model="form.parceria.projeto" placeholder="Descreva o objeto e escopo da parceria…"></textarea>
                </div>
                <div class="form-grid form-grid-2">
                  <div>
                    <label class="field-label">Início da Vigência</label>
                    <input type="date" v-model="form.parceria.inicio_atividades"/>
                  </div>
                  <div>
                    <label class="field-label">Término da Vigência</label>
                    <input type="date" v-model="form.parceria.termino_atividades"/>
                  </div>
                </div>

                <div>
                  <label class="field-label">Categorias e Especialidades</label>
                  <div style="display:flex; gap: 10px; flex-wrap: wrap;">
                    <label v-for="(val, cat) in form.parceria.categorias" :key="cat" style="display:flex; align-items:center; gap: 5px; font-size: 13px;">
                      <input type="checkbox" v-model="form.parceria.categorias[cat]" />
                      {{ cat }}
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div style="display:flex;justify-content:flex-end;gap:12px">
            <button type="button" class="btn btn-secondary" @click="prevStep">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
              Voltar
            </button>
            <button type="button" class="btn btn-primary" @click="nextStep">
              Próximo
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
            </button>
          </div>
        </div>
      </div>

      <!-- ═══════════ SCREEN: CONTROLE FINANCEIRO (Passo 3) ═══════════ -->
      <div v-if="currentStep === 3" class="screen active">
        <div class="step-bar">
          <div class="step done"><div class="step-circle">✓</div><span>Formalização</span></div>
          <div class="step-line done"></div>
          <div class="step done"><div class="step-circle">✓</div><span>Dados da Parceria</span></div>
          <div class="step-line done"></div>
          <div class="step active"><div class="step-circle">3</div><span>Controle Financeiro</span></div>
        </div>

        <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px">
          <div style="width:44px;height:44px;border-radius:11px;background:#eff6ff;display:flex;align-items:center;justify-content:center;flex-shrink:0">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
          <div>
            <h2 style="font-size:20px;font-weight:700;color:#1e293b">Controle Financeiro</h2>
            <p style="font-size:13px;color:#94a3b8">Cronograma de parcelas, valores e prestação de contas</p>
          </div>
        </div>

        <div style="display:grid;gap:20px">
          <div class="card">
            <div class="card-header"><div><h3>Configuração do Repasse</h3></div></div>
            <div class="card-body">
              <div class="form-grid form-grid-3">
                <div>
                  <label class="field-label">Valor Total (R$)<span class="field-required">*</span></label>
                  <input type="number" v-model="form.valor" placeholder="0.00" />
                </div>
                <div>
                  <label class="field-label">Periodicidade</label>
                  <select v-model="form.configuracoes_extras.periodicidade_repasse">
                    <option value="Mensal">Mensal</option>
                    <option value="Bimestral">Bimestral</option>
                    <option value="Semestral">Semestral</option>
                    <option value="Anual">Anual</option>
                  </select>
                </div>
                <div>
                  <label class="field-label">Dia de Repasse</label>
                  <input type="number" v-model="form.configuracoes_extras.dia_repasse" placeholder="Ex: 10"/>
                </div>
              </div>
            </div>
          </div>

          <div style="display:flex;justify-content:flex-end;gap:12px">
            <button type="button" class="btn btn-secondary" @click="prevStep">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>Voltar
            </button>
            <button type="submit" class="btn btn-success" :disabled="isSubmitting">
              <span v-if="isSubmitting">Salvando...</span>
              <span v-else style="display:flex;align-items:center;gap:6px">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                Efetivar e Concluir Cadastro
              </span>
            </button>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'

const props = defineProps<{
  activeScreen?: string
}>()
const emit = defineEmits(['update-screen'])

// Definição das chaves esperadas e da estrutura de dados da parceria
interface ParceriaForm {
  ajuste_termo: string
  inicio_atividades: string
  termino_atividades: string
  gestor_parceria: string
  projeto: string
  categorias: Record<string, boolean>
  atendimento_descricao: string
  meta_mes_atendimentos: number | null
  responsavel_entidade: string
  especialidades: Record<string, number>
}

// Definição das chaves esperadas e da estrutura de dados da entidade (Relação 1:1)
interface EntityForm {
  razao_social: string
  cnpj: string
  responsavel_nome: string
  situacao: string
  historico: string
  pa_emenda: string
  localizacao_pa_emenda: string
  emenda_alterada: string
  pa_formalizacao: string
  numero_emenda: string
  vereador: string
  justificativa: string
  valor: number | null
  parceria: ParceriaForm
  configuracoes_extras: {
    email_contato: string
    telefone: string
    meta_atendimentos: number | null
    historico_formalizacao: string
    periodicidade_repasse: string
    dia_repasse: number | null
    status_prestacao: string
  }
}

// Lista pré-definida de especialidades médicas/atendimentos comuns para seleção rápida
const poolEspecialidades = [
  'Fisioterapia', 'Fonoaudiologia', 'Psicologia', 'Terapia Ocupacional',
  'Nutrição', 'Assistência Social', 'Psicopedagogia', 'Psiquiatria',
  'Pediatria', 'Equoterapia', 'Pilates', 'Saúde Mental'
]

// Passo atual do Stepper
const currentStep = ref(1)

// Estado reativo do formulário contemplando todos os novos campos do termo de parceria e tabelas 1:1
const form = reactive<EntityForm>({
  razao_social: '',
  cnpj: '',
  responsavel_nome: '',
  situacao: '',
  historico: '',
  pa_emenda: '',
  localizacao_pa_emenda: '',
  emenda_alterada: '',
  pa_formalizacao: '',
  numero_emenda: '',
  vereador: '',
  justificativa: '',
  valor: null,
  parceria: {
    ajuste_termo: '',
    inicio_atividades: '',
    termino_atividades: '',
    gestor_parceria: '',
    projeto: '',
    categorias: {
      'Saúde Mental': false,
      'Fisioterapia': false,
      'Fonoaudiologia': false,
      'Causa Animal': false,
      'Outros': false
    },
    atendimento_descricao: '',
    meta_mes_atendimentos: null,
    responsavel_entidade: '',
    especialidades: {}
  },
  configuracoes_extras: {
    email_contato: '',
    telefone: '',
    meta_atendimentos: null,
    historico_formalizacao: '',
    periodicidade_repasse: 'Mensal',
    dia_repasse: 10,
    status_prestacao: 'Em análise'
  }
})

// Estados auxiliares de interface e carregamento
const isSubmitting = ref(false)
const apiError = ref('')
const apiSuccess = ref('')

const errors = reactive({
  razao_social: '',
  cnpj: ''
})

// Watchers para controle de passos
watch(() => props.activeScreen, (newVal) => {
  if (newVal === 'formalizacao') currentStep.value = 1;
  else if (newVal === 'parceria') currentStep.value = 2;
  else if (newVal === 'financeiro') currentStep.value = 3;
}, { immediate: true })

watch(currentStep, (newVal) => {
  if (newVal === 1) emit('update-screen', 'formalizacao');
  else if (newVal === 2) emit('update-screen', 'parceria');
  else if (newVal === 3) emit('update-screen', 'financeiro');
})

// Controle dinâmico das especialidades no JSONB
const hasEspecialidade = (name: string) => {
  return form.parceria.especialidades[name] !== undefined
}

const addEspecialidade = (name: string) => {
  if (!hasEspecialidade(name)) {
    form.parceria.especialidades[name] = 50 // valor inicial padrão
  }
}

const removeEspecialidade = (name: string) => {
  delete form.parceria.especialidades[name]
}

// Navegação de Passos
const nextStep = () => {
  if (currentStep.value === 1) {
    let hasErrors = false
    
    if (!form.razao_social.trim()) {
      errors.razao_social = 'A Razão Social é obrigatória para prosseguir.'
      hasErrors = true
    }

    if (form.cnpj) {
      const cnpjLimpo = form.cnpj.replace(/\D/g, '')
      if (cnpjLimpo.length !== 14) {
        errors.cnpj = 'O CNPJ deve conter exatamente 14 dígitos.'
        hasErrors = true
      }
    }

    if (hasErrors) return
  }
  
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

// Máscara dinâmica para o CNPJ
const handleCnpjInput = (event: Event) => {
  const input = event.target as HTMLInputElement
  let value = input.value.replace(/\D/g, '')
  
  if (value.length > 14) {
    value = value.slice(0, 14)
  }

  if (value.length > 12) {
    value = value.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
  } else if (value.length > 8) {
    value = value.replace(/^(\d{2})(\d{3})(\d{3})(\d{0,4})$/, '$1.$2.$3/$4')
  } else if (value.length > 5) {
    value = value.replace(/^(\d{2})(\d{3})(\d{0,3})$/, '$1.$2.$3')
  } else if (value.length > 2) {
    value = value.replace(/^(\d{2})(\d{0,3})$/, '$1.$2')
  }

  form.cnpj = value
  clearError('cnpj')
}

// Máscara dinâmica para telefone
const handlePhoneInput = (event: Event) => {
  const input = event.target as HTMLInputElement
  let value = input.value.replace(/\D/g, '')

  if (value.length > 11) {
    value = value.slice(0, 11)
  }

  if (value.length > 10) {
    value = value.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3')
  } else if (value.length > 6) {
    value = value.replace(/^(\d{2})(\d{4})(\d{0,4})$/, '($1) $2-$3')
  } else if (value.length > 2) {
    value = value.replace(/^(\d{2})(\d{0,4})$/, '($1) $2')
  } else if (value.length > 0) {
    value = value.replace(/^(\d{0,2})$/, '($1')
  }

  form.configuracoes_extras.telefone = value
}

// Limpeza de erros específicos
const clearError = (field: 'razao_social' | 'cnpj') => {
  errors[field] = ''
}

// Controle de Modal do Repasse Mensal
const isRepasseModalOpen = ref(false)
const editingRepasseIndex = ref<number | null>(null)

const tempRepasse = reactive<RepasseForm>({
  mes_referencia: '',
  repasse_oficio: '',
  repasse_periodo: '',
  repasse_parcela: 0,
  repasse_retencao: 0,
  repasse_valor_final: 0,
  repasse_vencimento: '',
  repasse_pa: '',
  repasse_data_pagamento: '',
  prestacao_oficio: '',
  prestacao_data_entrega: '',
  prestacao_pa: '',
  prestacao_sugestao_glosa: 0,
  prestacao_reconsideracao: 0,
  prestacao_mts: ''
})

const openRepasseModal = (index: number | null = null) => {
  editingRepasseIndex.value = index
  if (index !== null && form.repasses[index]) {
    Object.assign(tempRepasse, JSON.parse(JSON.stringify(form.repasses[index])))
  } else {
    tempRepasse.mes_referencia = ''
    tempRepasse.repasse_oficio = ''
    tempRepasse.repasse_periodo = ''
    tempRepasse.repasse_parcela = 0
    tempRepasse.repasse_retencao = 0
    tempRepasse.repasse_valor_final = 0
    tempRepasse.repasse_vencimento = ''
    tempRepasse.repasse_pa = ''
    tempRepasse.repasse_data_pagamento = ''
    tempRepasse.prestacao_oficio = ''
    tempRepasse.prestacao_data_entrega = ''
    tempRepasse.prestacao_pa = ''
    tempRepasse.prestacao_sugestao_glosa = 0
    tempRepasse.prestacao_reconsideracao = 0
    tempRepasse.prestacao_mts = ''
  }
  isRepasseModalOpen.value = true
}

const closeRepasseModal = () => {
  isRepasseModalOpen.value = false
  editingRepasseIndex.value = null
}

const calculateFinalValue = () => {
  tempRepasse.repasse_valor_final = Number((tempRepasse.repasse_parcela - tempRepasse.repasse_retencao).toFixed(2))
}

const handleMesInput = (event: Event) => {
  const input = event.target as HTMLInputElement
  let value = input.value.replace(/\D/g, '')
  if (value.length > 6) value = value.slice(0, 6)
  if (value.length > 2) {
    value = value.replace(/^(\d{2})(\d{0,4})$/, '$1.$2')
  }
  tempRepasse.mes_referencia = value
}

const saveRepasse = () => {
  if (!tempRepasse.mes_referencia || tempRepasse.mes_referencia.length !== 7) {
    alert('Por favor, preencha o mês de referência no formato MM.AAAA (Ex: 01.2026)')
    return
  }
  
  const repasseCopy = JSON.parse(JSON.stringify(tempRepasse))
  
  if (editingRepasseIndex.value !== null) {
    form.repasses[editingRepasseIndex.value] = repasseCopy
  } else {
    const existe = form.repasses.some(r => r.mes_referencia === repasseCopy.mes_referencia)
    if (existe) {
      alert('Já existe um lançamento para este mês de referência!')
      return
    }
    form.repasses.push(repasseCopy)
  }
  closeRepasseModal()
}

const removeRepasse = (index: number) => {
  if (confirm('Tem certeza de que deseja remover este repasse mensal?')) {
    form.repasses.splice(index, 1)
  }
}

const formatCurrency = (val: number | null) => {
  if (val === null || isNaN(val)) return '0,00'
  return val.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// Reset completo do formulário com as novas chaves
const resetForm = () => {
  form.razao_social = ''
  form.cnpj = ''
  form.responsavel_nome = ''
  form.situacao = ''
  form.historico = ''
  form.pa_emenda = ''
  form.localizacao_pa_emenda = ''
  form.emenda_alterada = ''
  form.pa_formalizacao = ''
  form.numero_emenda = ''
  form.vereador = ''
  form.justificativa = ''
  form.valor = null
  form.cod_scim = ''
  form.pa_empenho = ''
  form.objeto_descricao = ''
  
  form.parceria.ajuste_termo = ''
  form.parceria.inicio_atividades = ''
  form.parceria.termino_atividades = ''
  form.parceria.gestor_parceria = ''
  form.parceria.projeto = ''
  form.parceria.categorias = {
    'Saúde Mental': false,
    'Fisioterapia': false,
    'Fonoaudiologia': false,
    'Causa Animal': false,
    'Outros': false
  }
  form.parceria.atendimento_descricao = ''
  form.parceria.meta_mes_atendimentos = null
  form.parceria.responsavel_entidade = ''
  form.parceria.especialidades = {}
  form.repasses = []

  form.configuracoes_extras.email_contato = ''
  form.configuracoes_extras.telefone = ''
  form.configuracoes_extras.meta_atendimentos = null
  form.configuracoes_extras.historico_formalizacao = ''
  form.configuracoes_extras.periodicidade_repasse = 'Mensal'
  form.configuracoes_extras.dia_repasse = 10
  form.configuracoes_extras.status_prestacao = 'Em análise'
  
  errors.razao_social = ''
  errors.cnpj = ''
  currentStep.value = 1
}

// Função de submissão integrada com a API Python (Passo 3)
const submitForm = async () => {
  apiError.value = ''
  apiSuccess.value = ''
  isSubmitting.value = true

  try {
    const payload = {
      razao_social: form.razao_social.trim(),
      cnpj: form.cnpj ? form.cnpj.replace(/\D/g, '') : null,
      responsavel_nome: form.responsavel_nome.trim() || null,
      situacao: form.situacao.trim() || null,
      historico: form.historico.trim() || null,
      pa_emenda: form.pa_emenda.trim() || null,
      localizacao_pa_emenda: form.localizacao_pa_emenda.trim() || null,
      emenda_alterada: form.emenda_alterada.trim() || null,
      pa_formalizacao: form.pa_formalizacao.trim() || null,
      numero_emenda: form.numero_emenda.trim() || null,
      vereador: form.vereador.trim() || null,
      justificativa: form.justificativa.trim() || null,
      valor: form.valor,
      cod_scim: form.cod_scim.trim() || null,
      pa_empenho: form.pa_empenho.trim() || null,
      objeto_descricao: form.objeto_descricao.trim() || null,
      
      parceria: {
        ajuste_termo: form.parceria.ajuste_termo.trim() || null,
        inicio_atividades: form.parceria.inicio_atividades || null,
        termino_atividades: form.parceria.termino_atividades || null,
        gestor_parceria: form.parceria.gestor_parceria.trim() || null,
        projeto: form.parceria.projeto.trim() || null,
        categorias: form.parceria.categorias,
        atendimento_descricao: form.parceria.atendimento_descricao.trim() || null,
        meta_mes_atendimentos: form.parceria.meta_mes_atendimentos || 0,
        responsavel_entidade: form.parceria.responsavel_entidade.trim() || null,
        especialidades: form.parceria.especialidades
      },
      repasses: form.repasses,
      
      configuracoes_extras: {
        email_contato: form.configuracoes_extras.email_contato.trim() || null,
        telefone: form.configuracoes_extras.telefone.replace(/\D/g, '') || null,
        meta_atendimentos: form.configuracoes_extras.meta_atendimentos,
        historico_formalizacao: form.configuracoes_extras.historico_formalizacao.trim() || null,
        periodicidade_repasse: form.configuracoes_extras.periodicidade_repasse,
        dia_repasse: form.configuracoes_extras.dia_repasse,
        status_prestacao: form.configuracoes_extras.status_prestacao
      }
    }

    const response = await $fetch<{ status: string; message: string; id: string }>('/api/entidades', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: payload
    })

    if (response && response.status === 'success') {
      apiSuccess.value = `Parceria, Entidade e Lançamentos Mensais cadastrados de forma atômica no PostgreSQL com sucesso! ID: ${response.id}`
      resetForm()
    } else {
      throw new Error('Retorno inválido ou status inconsistente vindo do servidor.')
    }

  } catch (error: any) {
    console.error('Falha na integração com o servidor backend:', error)
    
    if (error.data && error.data.detail) {
      apiError.value = typeof error.data.detail === 'string' 
        ? error.data.detail 
        : JSON.stringify(error.data.detail)
    } else if (error.message) {
      apiError.value = `Falha na requisição: ${error.message}`
    } else {
      apiError.value = 'Não foi possível se comunicar com o backend em Python. Certifique-se de que a API está ativa na porta 8000.'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>
<style scoped>
/* Estilização Premium - Design Fluido & Glassmorphic */

.entity-create-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: 1.5rem;
  font-family: 'Inter', sans-serif;
}

.glass-card {
  width: 100%;
  max-width: 800px;
  background: rgba(18, 18, 26, 0.75);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  padding: 2.5rem;
  color: #f3f4f6;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
}

/* Header do Card */
.card-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding-bottom: 1.25rem;
}

.header-icon {
  width: 3.2rem;
  height: 3.2rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(168, 85, 247, 0.15));
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #a855f7;
  flex-shrink: 0;
}

.header-icon svg {
  width: 1.6rem;
  height: 1.6rem;
}

.header-text h2 {
  font-family: 'Outfit', sans-serif;
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  background: linear-gradient(90deg, #f3f4f6, #e5e7eb);
  -webkit-background-clip: text;
  color: transparent;
  margin: 0;
}

.header-text p {
  font-size: 0.85rem;
  color: #9ca3af;
  margin: 0.2rem 0 0 0;
}

/* Stepper (Indicador de Passos) */
.stepper-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2.5rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
  padding: 1rem 1.5rem;
  border-radius: 14px;
}

.stepper-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 2;
  transition: all 0.3s ease;
}

.step-counter {
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'Outfit', sans-serif;
  font-weight: 700;
  font-size: 0.95rem;
  color: #9ca3af;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.step-name {
  font-family: 'Outfit', sans-serif;
  font-size: 0.875rem;
  font-weight: 600;
  color: #9ca3af;
  transition: all 0.3s ease;
}

/* Stepper Actives e Completeds */
.stepper-item.active .step-counter {
  background: linear-gradient(135deg, #6366f1, #a855f7);
  border-color: transparent;
  color: #ffffff;
  box-shadow: 0 0 12px rgba(168, 85, 247, 0.4);
}

.stepper-item.active .step-name {
  color: #c084fc;
}

.stepper-item.completed .step-counter {
  background: rgba(16, 185, 129, 0.2);
  border-color: #10b981;
  color: #10b981;
}

.stepper-item.completed .step-name {
  color: #10b981;
}

.step-connector {
  flex-grow: 1;
  height: 2px;
  background: rgba(255, 255, 255, 0.08);
  margin: 0 1rem;
  transition: all 0.4s ease;
  position: relative;
}

.step-connector.completed {
  background: linear-gradient(90deg, #10b981, #10b981);
}

@media (max-width: 640px) {
  .step-name {
    display: none;
  }
}

/* Alertas de Feedback */
.alert-box {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  animation: fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.alert-success {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.25);
  color: #a7f3d0;
}

.alert-error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  color: #fca5a5;
}

.alert-icon svg {
  width: 1.5rem;
  height: 1.5rem;
  flex-shrink: 0;
}

.alert-content {
  flex-grow: 1;
}

.alert-content strong {
  display: block;
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 0.2rem;
}

.alert-content p {
  font-size: 0.85rem;
  margin: 0;
  opacity: 0.9;
}

.alert-close {
  background: transparent;
  border: none;
  color: currentColor;
  font-size: 1.25rem;
  cursor: pointer;
  opacity: 0.6;
  padding: 0;
  line-height: 1;
  transition: opacity 0.2s;
}

.alert-close:hover {
  opacity: 1;
}

/* Seções e Estrutura */
.create-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section-step {
  animation: slideIn 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.section-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.125rem;
  font-weight: 600;
  color: #c084fc;
  margin: 0 0 1.5rem 0;
  letter-spacing: -0.01em;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  padding-bottom: 0.5rem;
}

/* Layout em Grid */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.col-span-2 {
  grid-column: span 2;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .col-span-2 {
    grid-column: span 1;
  }
}

/* Inputs e Elementos de Formulário */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.825rem;
  font-weight: 500;
  color: #d1d5db;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.required {
  color: #f43f5e;
}

.input-wrapper {
  position: relative;
  width: 100%;
}

.form-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  color: #f3f4f6;
  outline: none;
  box-sizing: border-box;
  transition: all 0.2s ease-in-out;
}

.form-select {
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml;utf8,<svg fill='white' height='24' viewBox='0 0 24 24' width='24' xmlns='http://www.w3.org/2000/svg'><path d='M7 10l5 5 5-5z'/><path d='M0 0h24v24H0z' fill='none'/></svg>");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 30px;
  cursor: pointer;
}

.form-select option {
  background: #111118;
  color: #f3f4f6;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
  line-height: 1.5;
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Feedback visual de Foco Moderno */
.focus-border {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  transition: all 0.3s ease-in-out;
  transform: translateX(-50%);
  border-radius: 0 0 10px 10px;
}

.form-input:focus {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(168, 85, 247, 0.4);
  box-shadow: 0 0 12px rgba(168, 85, 247, 0.15);
}

.form-input:focus + .focus-border {
  width: 100%;
}

/* Erros de Validação */
.input-error {
  border-color: rgba(244, 63, 94, 0.5) !important;
  background: rgba(244, 63, 94, 0.02) !important;
}

.input-error:focus {
  box-shadow: 0 0 12px rgba(244, 63, 94, 0.15) !important;
}

.error-text {
  font-size: 0.75rem;
  color: #fb7185;
  margin-top: 0.15rem;
  animation: fadeIn 0.2s ease-in-out;
}

/* Checkboxes Customizados Premium */
.checkbox-group-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1rem;
  background: rgba(255, 255, 255, 0.01);
  border: 1px solid rgba(255, 255, 255, 0.04);
  padding: 1rem;
  border-radius: 10px;
}

.checkbox-custom-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  user-select: none;
  font-size: 0.85rem;
  color: #d1d5db;
  transition: color 0.2s ease;
}

.checkbox-custom {
  display: none;
}

.checkbox-box {
  width: 1.15rem;
  height: 1.15rem;
  border: 1.5px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.02);
  display: inline-block;
  position: relative;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.checkbox-custom:checked + .checkbox-box {
  background: linear-gradient(135deg, #6366f1, #a855f7);
  border-color: transparent;
  box-shadow: 0 0 8px rgba(168, 85, 247, 0.4);
}

.checkbox-custom:checked + .checkbox-box::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: bold;
}

.checkbox-custom-label:hover {
  color: #c084fc;
}

.checkbox-custom-label:hover .checkbox-box {
  border-color: rgba(168, 85, 247, 0.5);
}

/* Especialidades Interativas Pool & Tags */
.especialidades-selector-pool {
  background: rgba(255, 255, 255, 0.01);
  border: 1px solid rgba(255, 255, 255, 0.04);
  padding: 1rem;
  border-radius: 10px 10px 0 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.selector-pool-title {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #a855f7;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.pool-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.pool-tag-btn {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #d1d5db;
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: all 0.2s ease-in-out;
}

.pool-tag-btn:hover:not(:disabled) {
  background: rgba(99, 102, 241, 0.15);
  border-color: rgba(99, 102, 241, 0.4);
  color: #c084fc;
  transform: scale(1.05);
}

.pool-tag-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.especialidades-list-wrapper {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-top: none;
  padding: 1.25rem;
  border-radius: 0 0 10px 10px;
  min-height: 80px;
  box-sizing: border-box;
}

.empty-especialidades {
  text-align: center;
  color: #6b7280;
  font-size: 0.85rem;
  font-style: italic;
  padding: 1.5rem 0;
}

.especialidade-rows {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.especialidade-row-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 0.6rem 1rem;
  border-radius: 8px;
  animation: fadeIn 0.25s ease-in-out;
}

.esp-row-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #f3f4f6;
}

.esp-row-input-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.esp-mini-label {
  font-size: 0.75rem;
  color: #9ca3af;
}

.esp-mini-input {
  width: 90px !important;
  padding: 0.4rem 0.6rem !important;
  font-size: 0.85rem !important;
  border-radius: 6px !important;
  text-align: center;
}

.btn-delete-esp {
  background: rgba(244, 63, 94, 0.1);
  border: 1px solid rgba(244, 63, 94, 0.2);
  color: #fb7185;
  width: 1.8rem;
  height: 1.8rem;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-delete-esp:hover:not(:disabled) {
  background: rgba(244, 63, 94, 0.25);
  border-color: #fb7185;
  transform: scale(1.05);
}

/* Botões e Barra de Ações */
.form-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 1.5rem;
}

.form-actions button:only-child, .form-actions .btn-primary:first-child {
  margin-left: auto;
}

.btn-primary, .btn-secondary {
  font-family: 'Outfit', sans-serif;
  font-size: 0.925rem;
  font-weight: 600;
  padding: 0.75rem 1.75rem;
  border-radius: 10px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-primary {
  background: linear-gradient(135deg, #6366f1, #a855f7);
  border: none;
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(168, 85, 247, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(168, 85, 247, 0.45);
  background: linear-gradient(135deg, #4f46e5, #9333ea);
}

.btn-save {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
}

.btn-save:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669, #047857);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Spinner no botão */
.spinner-btn {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #ffffff;
  animation: spin 0.8s linear infinite;
}

/* Animações */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(12px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Premium Header Box no Passo 3 */
.premium-header-box {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 2rem;
}

/* Repasses Section & Subtitles */
.repasses-section {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-top: 1rem;
}

.repasses-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: 0.75rem;
}

.repasses-subtitle {
  font-family: 'Outfit', sans-serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: #c084fc;
  margin: 0;
}

.btn-add-repasse {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2));
  border: 1px solid rgba(168, 85, 247, 0.4);
  color: #c084fc;
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-add-repasse:hover:not(:disabled) {
  background: linear-gradient(135deg, #6366f1, #a855f7);
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
}

/* Table Design */
.table-container {
  background: rgba(255, 255, 255, 0.01);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 10px;
  overflow-x: auto;
  width: 100%;
}

.premium-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.85rem;
}

.premium-table th {
  background: rgba(255, 255, 255, 0.03);
  padding: 0.85rem 1rem;
  font-family: 'Outfit', sans-serif;
  font-weight: 600;
  color: #9ca3af;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.premium-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  color: #e5e7eb;
}

.premium-table tr:hover {
  background: rgba(255, 255, 255, 0.01);
}

.empty-repasses-box {
  padding: 2.5rem;
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
  font-style: italic;
}

/* Mini Ações Tabela */
.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-edit-mini, .btn-delete-mini {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 0.85rem;
  width: 1.85rem;
  height: 1.85rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit-mini:hover {
  background: rgba(99, 102, 241, 0.2);
  border-color: #6366f1;
}

.btn-delete-mini:hover {
  background: rgba(244, 63, 94, 0.2);
  border-color: #f43f5e;
}

/* Overlay do Modal Glassmorphic */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: modalFadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-glass-card {
  width: 90% !important;
  max-width: 680px !important;
  background: rgba(15, 15, 22, 0.85) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.6) !important;
  border-radius: 16px !important;
  padding: 1.75rem !important;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding-bottom: 0.75rem;
}

.modal-header h3 {
  margin: 0;
  font-family: 'Outfit', sans-serif;
  font-size: 1.15rem;
  font-weight: 700;
  color: #c084fc;
}

.btn-close-modal {
  background: transparent;
  border: none;
  color: #9ca3af;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
  transition: color 0.2s;
}

.btn-close-modal:hover {
  color: #ffffff;
}

.modal-body {
  padding: 0.5rem 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 1rem;
}

.section-divider-modal {
  font-family: 'Outfit', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #a855f7;
  letter-spacing: 0.05em;
  margin-top: 1.25rem;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.08);
  padding-bottom: 0.25rem;
}

.bg-dark-locked {
  background: rgba(0, 0, 0, 0.25) !important;
  cursor: not-allowed;
}

.font-bold {
  font-weight: 700;
}

.text-indigo-400 {
  color: #818cf8 !important;
}

.text-rose-400 {
  color: #fb7185 !important;
}

.text-emerald-400 {
  color: #34d399 !important;
}

.text-amber-400 {
  color: #fbbf24 !important;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    backdrop-filter: blur(0px);
    -webkit-backdrop-filter: blur(0px);
  }
  to {
    opacity: 1;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
  }
}
</style>