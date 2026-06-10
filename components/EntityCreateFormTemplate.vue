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
