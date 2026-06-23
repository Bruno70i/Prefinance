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
          <div style="display:flex; justify-content:space-between; align-items:center; width:100%; flex-wrap:wrap; gap:10px;">
            <div>
              <h2 style="font-size:20px;font-weight:700;color:#1e293b">Cadastro de Formalização</h2>
              <p style="font-size:13px;color:#94a3b8">Preencha os dados jurídicos para iniciar o cadastro</p>
            </div>
            <button type="button" @click="exportEtapa('formalizacao')" class="btn btn-secondary btn-sm" style="display:flex; align-items:center; gap:6px; cursor:pointer;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Exportar Etapa (Excel)
            </button>
          </div>
        </div>

        <!-- Importar planilha/CSV para preencher automaticamente -->
        <div
          class="import-drop"
          :class="{ 'is-over': arrastando }"
          @dragover.prevent="arrastando = true"
          @dragleave.prevent="arrastando = false"
          @drop.prevent="onDrop"
          @click="($refs.inputImport as HTMLInputElement).click()"
        >
          <input ref="inputImport" type="file" accept=".xlsx,.xls,.csv" hidden @change="onSelecionarArquivo" />
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#0b5394" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          <p style="margin:6px 0 0; font-weight:600; color:#1e293b">
            Arraste um Excel/CSV aqui para preencher automaticamente
          </p>
          <span style="font-size:12px; color:#64748b">ou clique para selecionar — .xlsx, .xls ou .csv</span>
          <p v-if="importando" style="margin:8px 0 0; color:#0b5394; font-size:13px">Lendo arquivo…</p>
          <p v-if="importMsg" style="margin:8px 0 0; color:#16a34a; font-size:13px">✓ {{ importMsg }}</p>
          <p v-if="importErro" style="margin:8px 0 0; color:#ef4444; font-size:13px">⚠️ {{ importErro }}</p>
        </div>
        <div style="display:flex; gap:10px; align-items:center; margin-top:-6px; margin-bottom:16px">
          <button type="button" class="btn btn-secondary btn-sm" @click.stop="baixarModeloImportacao('xlsx')">
            ⬇️ Baixar modelo (Excel)
          </button>
          <button type="button" class="btn btn-secondary btn-sm" @click.stop="baixarModeloImportacao('csv')">
            ⬇️ Baixar modelo (CSV)
          </button>
        </div>

        <div style="display:grid;gap:20px">
          <div class="card">
            <div class="card-header"><div><h3>Identificação do Processo</h3><p>Dados do processo administrativo e vínculo com a emenda</p></div></div>
            <div class="card-body">
              <div class="form-grid form-grid-3">
                <div>
                  <label class="field-label">PA Emenda</label>
                  <input type="text" v-model="form.pa_emenda" placeholder="Ex: PA-E-2025/0042"/>
                </div>
                <div>
                  <label class="field-label">PA Formalização</label>
                  <input type="text" v-model="form.pa_formalizacao" placeholder="Ex: PA-F-2025/0042"/>
                </div>
                <div>
                  <label class="field-label">Tipo de Instrumento<span class="field-required">*</span></label>
                  <select v-model="form.situacao" required>
                    <option value="">Selecione…</option>
                    <option value="TERMO DE FOMENTO">TERMO DE FOMENTO</option>
                    <option value="TERMO DE COLABORAÇÃO">TERMO DE COLABORAÇÃO</option>
                    <option value="CONVENIO">CONVENIO</option>
                  </select>
                </div>
                <div>
                  <label class="field-label">N° (Número da Emenda)</label>
                  <input type="text" v-model="form.numero_emenda" placeholder="Ex: Emenda 01/2025"/>
                </div>
                <div>
                  <label class="field-label">Vereador Proponente</label>
                  <input type="text" v-model="form.vereador" placeholder="Nome do Vereador"/>
                </div>
                <div>
                  <label class="field-label">Valor (R$)<span class="field-required">*</span></label>
                  <input type="text" :value="valorExibicao" @input="handleValorInput" placeholder="R$ 0,00" required />
                </div>
                <div>
                  <label class="field-label">Emenda Alterada?</label>
                  <select v-model="form.emenda_alterada">
                    <option value="">Selecione…</option>
                    <option value="Sim">Sim</option>
                    <option value="Não">Não</option>
                  </select>
                </div>
                <div style="grid-column: span 3">
                  <label class="field-label">Justificativa da Emenda</label>
                  <textarea v-model="form.justificativa" placeholder="Justificativa informada no processo..." rows="2" style="width: 100%; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; font-family: inherit; font-size: 14px; outline: none; transition: border-color 0.2s, box-shadow 0.2s;"></textarea>
                </div>
                <div style="grid-column: span 3">
                  <label class="field-label">Histórico (Anotações gerais do processo)</label>
                  <textarea v-model="form.historico" placeholder="Eventos importantes, tramitações, etc..." rows="2" style="width: 100%; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; font-family: inherit; font-size: 14px; outline: none; transition: border-color 0.2s, box-shadow 0.2s;"></textarea>
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
                  <input id="cnpj" type="text" v-model="form.cnpj" placeholder="00.000.000/0000-00" @input="handleCnpjInput" @blur="verificarCnpj(); verificarGrupoRaiz(); consultarBrasilApi()" required />
                  <div style="margin-top: 6px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <span v-if="cnpjPartes.tipo !== 'INDEFINIDO'"
                          :style="{ padding:'2px 8px', borderRadius:'12px', fontSize:'12px', fontWeight:600,
                                    color:'#fff', background: cnpjPartes.tipo === 'MATRIZ' ? '#0b5394' : '#0e7490' }">
                      {{ rotuloEstabelecimento }}
                    </span>
                    <span v-if="cnpjPartes.raiz" style="font-size:12px; color:#64748b;">
                      Raiz: {{ cnpjPartes.raiz }}
                    </span>
                  </div>
                  <div style="margin-top: 4px;" v-if="statusBrasilApi !== 'idle'">
                    <span v-if="statusBrasilApi === 'buscando'" style="font-size:12px;color:#64748b">
                      Consultando dados públicos…
                    </span>
                    <span v-else-if="statusBrasilApi === 'ok'" style="font-size:12px;color:#16a34a">
                      ✓ Dados sugeridos automaticamente (confira e ajuste se necessário).
                    </span>
                    <span v-else-if="statusBrasilApi === 'indisponivel'" style="font-size:12px;color:#94a3b8">
                      Consulta automática indisponível — preencha manualmente.
                    </span>
                  </div>
                  <p class="input-hint" style="color:#ef4444" v-if="errors.cnpj">{{ errors.cnpj }}</p>
                </div>
                <div style="grid-column:span 2">
                  <label class="field-label">Razão Social / Nome da Entidade<span class="field-required">*</span></label>
                  <input id="razao_social" type="text" v-model="form.razao_social" placeholder="Nome completo conforme CNPJ" @input="clearError('razao_social'); avisoRazaoSocial = ''" @blur="verificarQuaseDuplicatasNome" required />
                  <p class="input-hint" style="color:#ef4444" v-if="errors.razao_social">{{ errors.razao_social }}</p>
                  <div v-if="avisoRazaoSocial" style="margin-top:6px; padding:10px; border:1px solid #fde68a; background:#fffbeb; border-radius:6px; font-size:13px; color:#92400e; line-height: 1.4;">
                    ⚠️ {{ avisoRazaoSocial }}
                  </div>
                </div>
                <div>
                  <label class="field-label">E-mail Institucional</label>
                  <input id="email_contato" type="email" v-model="form.configuracoes_extras.email_contato" placeholder="entidade@exemplo.org.br" @input="clearError('email_contato')" />
                  <p class="input-hint" style="color:#ef4444" v-if="errors.email_contato">{{ errors.email_contato }}</p>
                </div>
                <div>
                  <label class="field-label">Telefone / WhatsApp</label>
                  <input id="telefone" type="text" :value="form.configuracoes_extras.telefone" placeholder="(00) 00000-0000" @input="(e) => { handlePhoneInput(e); clearError('telefone') }" />
                  <p class="input-hint" style="color:#ef4444" v-if="errors.telefone">{{ errors.telefone }}</p>
                </div>
                <div>
                  <label class="field-label">Representante Legal</label>
                  <input type="text" v-model="form.responsavel_nome" placeholder="Nome completo" />
                </div>
                <div style="grid-column:span 2">
                  <label class="field-label">Endereço</label>
                  <input type="text" v-model="form.configuracoes_extras.endereco" placeholder="Rua, Número, Bairro, Cidade - UF"/>
                </div>
                <div>
                  <label class="field-label">CPF do Representante Legal</label>
                  <input id="cpf_representante" type="text" :value="form.configuracoes_extras.cpf_representante" placeholder="000.000.000-00" @input="handleCpfInput" @blur="verificarCpf" />
                  <p class="input-hint" style="color:#ef4444" v-if="errors.cpf_representante">{{ errors.cpf_representante }}</p>
                  <p v-if="avisoCpf" style="color:#b45309; font-size:13px; margin-top:4px">⚠️ {{ avisoCpf }}</p>
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

        <!-- Context badge -->
        <div class="context-badge">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          <div class="cb-pill"><span class="cb-label">Processo</span><span class="cb-value">{{ form.pa_formalizacao || '—' }}</span></div>
          <div class="cb-sep"></div>
          <div class="cb-pill"><span class="cb-label">Entidade</span><span class="cb-value">{{ form.razao_social || '—' }}</span></div>
          <div class="cb-sep"></div>
          <div class="cb-pill"><span class="cb-label">CNPJ Raiz</span><span class="cb-value">{{ form.cnpj || '—' }}</span></div>
        </div>

        <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px">
          <div style="width:44px;height:44px;border-radius:11px;background:#eff6ff;display:flex;align-items:center;justify-content:center;flex-shrink:0">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center; width:100%; flex-wrap:wrap; gap:10px;">
            <div>
              <h2 style="font-size:20px;font-weight:700;color:#1e293b">Dados da Parceria</h2>
              <p style="font-size:13px;color:#94a3b8">Termo, vigência, fiscal e metas</p>
            </div>
            <button type="button" @click="exportEtapa('parceria')" class="btn btn-secondary btn-sm" style="display:flex; align-items:center; gap:6px; cursor:pointer;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Exportar Etapa (Excel)
            </button>
          </div>
        </div>

        <div style="display:grid;gap:20px">
          <div class="card">
            <div class="card-header"><div><h3>Unidade Executora</h3><p>Identifica quem executará este contrato</p></div></div>
            <div class="card-body">
              <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:10px;padding:16px 18px;margin-bottom:20px">
                <div class="form-grid form-grid-3">
                  <div>
                    <label class="field-label">PA Emenda</label>
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

              <!-- Listagem do Grupo Raiz (Passo 08) -->
              <div v-if="cnpjPartes.tipo === 'FILIAL' && grupoRaiz.estabelecimentos.length > 0"
                   style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:10px; padding:16px 18px; margin-bottom:20px; font-size:13px; color:#334155;">
                <p style="margin:0 0 8px; font-weight:600; color:#0369a1; display:flex; align-items:center; gap:6px;">
                  🏢 Estabelecimentos cadastrados sob a mesma raiz ({{ cnpjPartes.raiz }}):
                </p>
                <ul style="margin:0; padding-left:18px;">
                  <li v-for="est in grupoRaiz.estabelecimentos" :key="est.entidade_id" style="margin-bottom: 4px;">
                    <strong>{{ est.tipo }} {{ est.ordem }}</strong> — {{ est.razao_social }} ({{ est.cnpj }})
                  </li>
                </ul>
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
                <p v-if="datasVigenciaInvalidas" style="color:#ef4444; font-size:13px; margin-top:4px">
                  A data de início não pode ser posterior à data de término.
                </p>

                <div>
                  <label class="field-label">Categorias e Especialidades</label>
                  <div style="display:flex; gap: 10px; flex-wrap: wrap;">
                    <label v-for="(val, cat) in form.parceria.categorias" :key="cat" style="display:flex; align-items:center; gap: 5px; font-size: 13px;">
                      <input type="checkbox" v-model="form.parceria.categorias[cat]" />
                      {{ cat }}
                    </label>
                  </div>
                </div>
                
                <div class="form-grid form-grid-3">
                  <div>
                    <label class="field-label">Atendimento (Descrição)</label>
                    <input type="text" v-model="form.parceria.atendimento_descricao" placeholder="Descrição do Atendimento" />
                  </div>
                  <div>
                    <label class="field-label">Meta (Mês)</label>
                    <input type="text" v-model="form.parceria.meta_mes_atendimentos" placeholder="960 Atendimentos" />
                  </div>
                  <div>
                    <label class="field-label">Responsável pela Entidade</label>
                    <input type="text" v-model="form.parceria.responsavel_entidade" placeholder="Nome do Responsável" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header"><div><h3>Metas por Especialidade (Numérico)</h3><p>Defina a quantidade meta mensal para cada especialidade</p></div></div>
            <div class="card-body">
              <div class="form-grid" style="grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px;">
                <div v-for="esp in listaEspecialidades" :key="esp" style="display: flex; flex-direction: column; gap: 4px;">
                  <label class="field-label" style="font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" :title="esp">{{ esp.replace('\n', ' ') }}</label>
                  <input type="number" v-model="form.parceria.especialidades[esp]" placeholder="0" min="0" style="padding: 6px 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; font-family: inherit; outline: none; transition: border-color 0.2s;" />
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

        <!-- Context badge -->
        <div class="context-badge">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          <div class="cb-pill"><span class="cb-label">Processo</span><span class="cb-value">{{ form.pa_formalizacao || '—' }}</span></div>
          <div class="cb-sep"></div>
          <div class="cb-pill"><span class="cb-label">Entidade</span><span class="cb-value">{{ form.razao_social || '—' }}</span></div>
          <div class="cb-sep"></div>
          <div class="cb-pill"><span class="cb-label">Unidade</span><span class="cb-value">{{ form.parceria.ajuste_termo || '—' }}</span></div>
        </div>

        <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px">
          <div style="width:44px;height:44px;border-radius:11px;background:#eff6ff;display:flex;align-items:center;justify-content:center;flex-shrink:0">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center; width:100%; flex-wrap:wrap; gap:10px;">
            <div>
              <h2 style="font-size:20px;font-weight:700;color:#1e293b">Controle Financeiro</h2>
              <p style="font-size:13px;color:#94a3b8">Cronograma de parcelas, valores e prestação de contas</p>
            </div>
            <button type="button" @click="exportEtapa('financeiro')" class="btn btn-secondary btn-sm" style="display:flex; align-items:center; gap:6px; cursor:pointer;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Exportar Etapa (Excel)
            </button>
          </div>
        </div>

        <div style="display:grid;gap:20px">
          <div class="card">
            <div class="card-header"><div><h3>Configuração do Repasse</h3></div></div>
            <div class="card-body">
              <div class="form-grid form-grid-3" style="margin-bottom: 20px;">
                <div>
                  <label class="field-label">CÓD. SCIM</label>
                  <input type="number" v-model="form.cod_scim" placeholder="Apenas números" />
                </div>
                <div>
                  <label class="field-label">P.A. EMPENHO</label>
                  <input type="text" v-model="form.pa_empenho" placeholder="52456/2025" />
                </div>
                <div>
                  <label class="field-label">OBJETO</label>
                  <input type="text" v-model="form.objeto_descricao" placeholder="TEA - Atendimento indicados..." />
                </div>
              </div>
              <div class="form-grid form-grid-3">
                <div>
                  <label class="field-label">Valor Total do Repasse (R$)<span class="field-required">*</span></label>
                  <input type="text" :value="valorExibicao" @input="handleValorInput" placeholder="R$ 0,00" required />
                </div>
                <div>
                  <label class="field-label">Número de Parcelas<span class="field-required">*</span></label>
                  <select v-model="form.configuracoes_extras.numero_parcelas" required>
                    <option value="">Selecione…</option>
                    <option :value="1">1 parcela (único)</option>
                    <option :value="2">2 parcelas</option>
                    <option :value="3">3 parcelas</option>
                    <option :value="4">4 parcelas</option>
                    <option :value="6">6 parcelas</option>
                    <option :value="12">12 parcelas</option>
                  </select>
                </div>
                <div>
                  <label class="field-label">Data do Primeiro Repasse</label>
                  <input type="date" v-model="form.configuracoes_extras.data_primeiro_repasse"/>
                </div>
              </div>
            </div>
          </div>

          <!-- Cronograma de Parcelas -->
          <div class="card" v-if="form.repasses && form.repasses.length > 0">
            <div class="card-header">
              <div>
                <h3>Cronograma de Parcelas</h3>
                <p>Defina o valor individual de cada parcela</p>
              </div>
            </div>
            <div class="card-body">
              <div class="parcela-input-header">
                <span>#</span>
                <span>Competência</span>
                <span>Valor da Parcela (R$)</span>
                <span>Data Prevista</span>
                <span></span>
              </div>
              
              <div id="parcelas-dinamicas">
                <div v-for="(rep, index) in form.repasses" :key="index" class="parcela-input-row">
                  <span style="font-weight:700;color:#1d4ed8;font-family:'DM Mono';font-size:12px">
                    {{ String(index + 1).padStart(2,'0') }}/{{ String(form.repasses.length).padStart(2,'0') }}
                  </span>
                  <div style="display: flex; gap: 4px; align-items: center; width: 100%;">
                    <select :value="rep.mes_referencia ? rep.mes_referencia.split('.')[0] : '01'" @change="atualizarMes(rep, ($event.target as HTMLSelectElement).value)" style="flex: 1; padding: 6px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; font-family:'DM Mono',monospace; background: white; color: #1e293b;">
                      <option value="01">01 (Jan)</option>
                      <option value="02">02 (Fev)</option>
                      <option value="03">03 (Mar)</option>
                      <option value="04">04 (Abr)</option>
                      <option value="05">05 (Mai)</option>
                      <option value="06">06 (Jun)</option>
                      <option value="07">07 (Jul)</option>
                      <option value="08">08 (Ago)</option>
                      <option value="09">09 (Set)</option>
                      <option value="10">10 (Out)</option>
                      <option value="11">11 (Nov)</option>
                      <option value="12">12 (Dez)</option>
                    </select>
                    <select :value="rep.mes_referencia ? rep.mes_referencia.split('.')[1] : '2026'" @change="atualizarAno(rep, ($event.target as HTMLSelectElement).value)" style="flex: 1.2; padding: 6px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; font-family:'DM Mono',monospace; background: white; color: #1e293b;">
                      <option v-for="ano in anosDisponiveis" :key="ano" :value="String(ano)">{{ ano }}</option>
                    </select>
                  </div>
                  <input type="text" placeholder="0,00" v-model="rep.repasse_parcela_texto" @input="updateRepasseParcela(rep)" style="font-family:'DM Mono',monospace" />
                  <input type="date" v-model="rep.repasse_vencimento" />
                  <span></span>
                </div>
              </div>
              
              <div style="margin-top:16px;display:flex;align-items:center;gap:12px;flex-wrap:wrap">
                <span style="font-size:13px;color:#64748b">Soma das parcelas: <strong style="color:#1e293b">R$ {{ formatCurrency(somaParcelas) }}</strong></span>
                <span>
                  <span v-if="somaCoincide" class="val-ok">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                    Soma coincide com o valor total
                  </span>
                  <span v-else class="val-err">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                    A soma das parcelas precisa ser igual ao valor total para concluir o cadastro (diferença de R$ {{ formatCurrency(Math.abs(somaParcelas - (form.valor || 0))) }}).
                  </span>
                </span>
              </div>
            </div>
          </div>

          <!-- Upload de Documentos -->
          <div class="card">
            <div class="card-header"><div><h3>Upload de Documentos</h3><p>Comprovantes e prestação de contas em PDF</p></div></div>
            <div class="card-body">
              <div class="drop-zone" id="drop-zone">
                <svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
                <p>Arraste arquivos PDF aqui</p>
                <span>ou clique para selecionar — máx. 20 MB</span>
              </div>
            </div>
          </div>

          <!-- Painel Informativo sobre o Representante Legal (Passo 07) -->
          <div v-if="resumoRepresentante.total_empresas > 0"
               style="margin:16px 0; padding:16px; border:1px solid #fde68a; background:#fffbeb; border-radius:8px;">
            <p style="font-weight:600; color:#92400e; margin:0 0 6px; display:flex; align-items:center; gap:6px;">
              ℹ️ Informação sobre o representante
            </p>
            <p style="margin:0 0 4px; color:#78350f;">
              Esta pessoa (CPF {{ form.configuracoes_extras.cpf_representante }}) já é representante de
              <strong>{{ resumoRepresentante.total_empresas }}</strong> empresa(s).
            </p>
            <p style="margin:0 0 8px; color:#78350f;">
              Total já repassado entre todas:
              <strong>{{ fmtBRL(resumoRepresentante.total_repassado) }}</strong>.
            </p>
            <ul style="margin:0; padding-left:18px; color:#92400e; font-size:13px;">
              <li v-for="emp in resumoRepresentante.empresas" :key="emp.entidade_id" style="margin-bottom: 4px;">
                {{ emp.razao_social }} ({{ emp.cnpj || 's/ CNPJ' }}) — {{ fmtBRL(emp.total_repassado) }}
              </li>
            </ul>
            <p style="margin:8px 0 0; font-size:12px; color:#a16207;">
              Esta é apenas uma informação. Não impede a conclusão do cadastro.
            </p>
          </div>

          <div style="display:flex;justify-content:flex-end;gap:12px">
            <button type="button" class="btn btn-secondary" @click="prevStep">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>Voltar
            </button>
            <button type="submit" class="btn btn-success" :disabled="!podeConcluir">
              <span v-if="isSubmitting">Salvando...</span>
              <span v-else style="display:flex;align-items:center;gap:6px">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                {{ ehEdicao ? 'Salvar Alterações' : 'Efetivar e Concluir Cadastro' }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </form>

    <!-- Modal de Confirmação Final (Passo 10.5) -->
    <div v-if="mostrarConfirmacaoModal" class="modal-overlay" @click.self="mostrarConfirmacaoModal = false">
      <div class="modal-glass-card" style="max-width: 550px; width: 90%; border-radius: 16px; display: flex; flex-direction: column;">
        <div class="modal-header" style="border-bottom: 1px solid rgba(255,255,255,0.1); padding: 16px 20px; display: flex; justify-content: space-between; align-items: center;">
          <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: #f1f5f9;">{{ ehEdicao ? 'Confirmar Alterações' : 'Confirmar Efetivação do Cadastro' }}</h3>
          <button type="button" @click="mostrarConfirmacaoModal = false" class="btn-close-modal" style="background: none; border: none; font-size: 18px; cursor: pointer; color: #94a3b8;">✕</button>
        </div>
        <div class="modal-body" style="padding: 20px; font-size: 14px; color: #cbd5e1; line-height: 1.6; max-height: 60vh; overflow-y: auto;">
          <p style="margin-top: 0; margin-bottom: 16px; color: #94a3b8;">Por favor, revise o resumo dos dados abaixo antes de consolidar a parceria no banco de dados.</p>
          
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px;">
            <div>
              <strong style="color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 2px;">Razão Social</strong>
              <span style="font-weight: 600; color: #0f172a; font-size: 15px;">{{ form.razao_social }}</span>
            </div>
            
            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
              <div style="flex: 1; min-width: 150px;">
                <strong style="color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 2px;">CNPJ</strong>
                <span style="font-weight: 600; color: #0f172a;">{{ form.cnpj || 'Não Informado' }}</span>
                <span v-if="cnpjPartes.tipo !== 'INDEFINIDO'" :style="{ marginLeft: '6px', padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 600, color: '#fff', background: cnpjPartes.tipo === 'MATRIZ' ? '#0b5394' : '#0e7490' }">
                  {{ rotuloEstabelecimento }}
                </span>
              </div>
              <div style="flex: 1; min-width: 150px;">
                <strong style="color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 2px;">Valor Total</strong>
                <span style="font-weight: 600; color: #1e3a8a; font-size: 15px;">R$ {{ formatCurrency(form.valor) }}</span>
              </div>
            </div>

            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
              <div style="flex: 1; min-width: 150px;">
                <strong style="color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 2px;">Nº de Parcelas</strong>
                <span style="font-weight: 600; color: #0f172a;">{{ form.configuracoes_extras.numero_parcelas }} parcela(s)</span>
              </div>
              <div style="flex: 1; min-width: 150px;">
                <strong style="color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 2px;">Soma do Cronograma</strong>
                <span style="font-weight: 600; color: #16a34a;">R$ {{ formatCurrency(somaParcelas) }}</span>
              </div>
            </div>
          </div>

          <!-- Avisos 🟡 Activos no Modal -->
          <div v-if="resumoRepresentante.total_empresas > 0 || avisoRazaoSocial" style="border-radius: 10px; border: 1px solid #fde68a; background: #fffbeb; padding: 12px 16px; margin-bottom: 16px;">
            <h4 style="margin: 0 0 8px; color: #92400e; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px;">
              ⚠️ Avisos Informativos Ativos:
            </h4>
            <ul style="margin: 0; padding-left: 18px; color: #78350f; font-size: 12px; line-height: 1.5; display: flex; flex-direction: column; gap: 6px;">
              <li v-if="avisoRazaoSocial">{{ avisoRazaoSocial }}</li>
              <li v-if="resumoRepresentante.total_empresas > 0">
                Este CPF de representante já possui {{ resumoRepresentante.total_empresas }} empresa(s) cadastrada(s) no sistema (Total repassado de R$ {{ formatCurrency(resumoRepresentante.total_repassado) }}).
              </li>
            </ul>
          </div>

          <p style="margin: 0 0 8px; font-size: 13px; color: #94a3b8; text-align: center; font-style: italic;">
            Deseja gravar essas informações de forma definitiva?
          </p>
        </div>
        <div class="modal-footer" style="border-top: 1px solid rgba(255,255,255,0.1); padding: 16px 20px; display: flex; justify-content: flex-end; gap: 12px; border-bottom-left-radius: 16px; border-bottom-right-radius: 16px;">
          <button type="button" @click="mostrarConfirmacaoModal = false" class="btn btn-ghost" style="padding: 10px 16px; font-size: 14px; border: 1px solid #cbd5e1; background: white; border-radius: 8px; color: #475569; cursor: pointer; font-weight: 600;">
            Cancelar e Ajustar
          </button>
          <button type="button" @click="efetivarCadastro" class="btn btn-success" style="padding: 10px 20px; font-size: 14px; background: #16a34a; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 6px;">
            Confirmar e Salvar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { validarCNPJ, apenasDigitos, validarCPF, parseCnpj } from '~/utils/validadores'

const arrastando = ref(false)
const importando = ref(false)
const importMsg = ref('')
const importErro = ref('')

function onDrop(e: DragEvent) {
  arrastando.value = false
  const arquivo = e.dataTransfer?.files?.[0]
  if (arquivo) importarArquivo(arquivo)
}

function onSelecionarArquivo(e: Event) {
  const arquivo = (e.target as HTMLInputElement).files?.[0]
  if (arquivo) importarArquivo(arquivo)
}

function formTemDados(): boolean {
  return !!(form.razao_social || form.cnpj || form.valor || form.pa_emenda || form.numero_emenda)
}

async function importarArquivo(arquivo: File) {
  importMsg.value = ''; importErro.value = ''
  const ext = arquivo.name.toLowerCase()
  if (!ext.endsWith('.xlsx') && !ext.endsWith('.xls') && !ext.endsWith('.csv')) {
    importErro.value = 'Formato inválido. Use .xlsx, .xls ou .csv.'
    return
  }
  if (formTemDados() && !confirm('Isto vai preencher/sobrescrever os campos com os dados do arquivo. Continuar?')) {
    return
  }

  importando.value = true
  try {
    const fd = new FormData()
    fd.append('file', arquivo)
    const resp = await fetch('/api/import/planilha', { method: 'POST', body: fd })
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}))
      throw new Error(err.detail || 'Falha ao ler o arquivo.')
    }
    const data = await resp.json()
    const qtd = aplicarImportacao(data)
    importMsg.value = `Importado: ${qtd} campo(s) preenchido(s).` +
      (data.avisos?.length ? ' ' + data.avisos.join(' ') : '')
  } catch (e: any) {
    importErro.value = e?.message || 'Erro ao importar o arquivo.'
  } finally {
    importando.value = false
  }
}

function aplicarImportacao(data: any): number {
  let n = 0
  const f = data.formalizacao || {}

  const diretos = [
    'razao_social', 'cnpj', 'situacao', 'historico', 'pa_emenda', 'localizacao_pa_emenda',
    'emenda_alterada', 'pa_formalizacao', 'numero_emenda', 'vereador', 'justificativa',
    'cod_scim', 'pa_empenho', 'objeto_descricao', 'responsavel_nome'
  ]
  for (const k of diretos) {
    if (f[k] !== undefined && f[k] !== null && f[k] !== '') { (form as any)[k] = f[k]; n++ }
  }
  if (f.valor !== undefined && f.valor !== null) { form.valor = Number(f.valor); n++ }

  const extras = ['email_contato', 'telefone', 'endereco', 'cpf_representante']
  for (const k of extras) {
    if (f[k] !== undefined && f[k] !== null && f[k] !== '') {
      (form.configuracoes_extras as any)[k] = f[k]; n++
    }
  }

  if (data.parceria) n += aplicarParceria(data.parceria)
  if (Array.isArray(data.repasses) && data.repasses.length) {
    const fr = data.repasses[0]
    if (fr.repasse_vencimento || fr.repasse_data_pagamento) {
      form.configuracoes_extras.data_primeiro_repasse = fr.repasse_vencimento || fr.repasse_data_pagamento
      n++
    }
    n += aplicarRepasses(data.repasses)
  }

  return n
}

function aplicarParceria(p: any): number {
  let n = 0
  const campos = ['ajuste_termo', 'gestor_parceria', 'projeto', 'inicio_atividades',
    'termino_atividades', 'meta_mes_atendimentos', 'atendimento_descricao', 'responsavel_entidade']
  for (const k of campos) {
    if (p[k] !== undefined && p[k] !== null && p[k] !== '') { (form.parceria as any)[k] = p[k]; n++ }
  }
  if (p.categorias && typeof p.categorias === 'object') {
    const mapped: any = {}
    if (p.categorias['Saúde Mental']) mapped['Saúde Mental'] = true
    if (p.categorias['Fisioterapia']) mapped['Fisioterapia'] = true
    if (p.categorias['Fono'] || p.categorias['Fonoaudiologia']) mapped['Fono'] = true
    if (p.categorias['Animal'] || p.categorias['Causa Animal']) mapped['Animal'] = true
    if (p.categorias['Outros']) mapped['Outros'] = true

    form.parceria.categorias = {
      'Saúde Mental': !!mapped['Saúde Mental'],
      'Fisioterapia': !!mapped['Fisioterapia'],
      'Fono': !!mapped['Fono'],
      'Animal': !!mapped['Animal'],
      'Outros': !!mapped['Outros']
    }
    n++
  }
  if (p.especialidades && typeof p.especialidades === 'object') {
    form.parceria.especialidades = { ...p.especialidades }
    n++
  }
  return n
}

function aplicarRepasses(lista: any[]): number {
  form.repasses = lista.map((r: any) => ({
    ...r,
    repasse_parcela: Number(r.repasse_parcela || 0),
    repasse_parcela_texto: Number(r.repasse_parcela || 0)
      .toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
    repasse_vencimento: r.repasse_vencimento || '',
  }))
  form.configuracoes_extras.numero_parcelas = lista.length
  return form.repasses.length
}

function baixarModeloImportacao(formato: 'xlsx' | 'csv' = 'xlsx') {
  const link = document.createElement('a')
  link.href = `/api/import/modelo?formato=${formato}`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const props = withDefaults(defineProps<{
  activeScreen?: string
  modo?: 'criar' | 'editar'
  entidadeId?: string | null
}>(), {
  modo: 'criar',
  entidadeId: null
})
const emit = defineEmits(['update-screen', 'salvo'])

const ehEdicao = computed(() => props.modo === 'editar' && !!props.entidadeId)

const carregarEntidade = async (id: string) => {
  try {
    const e = await $fetch<any>(`/api/entidades/${id}`)

    // Formalização (colunas reais)
    form.razao_social = e.razao_social || ''
    form.cnpj = e.cnpj || ''
    form.responsavel_nome = e.responsavel_nome || ''
    form.situacao = e.situacao || ''
    form.historico = e.historico || ''
    form.pa_emenda = e.pa_emenda || ''
    form.localizacao_pa_emenda = e.localizacao_pa_emenda || ''
    form.emenda_alterada = e.emenda_alterada || ''
    form.pa_formalizacao = e.pa_formalizacao || ''
    form.numero_emenda = e.numero_emenda || ''
    form.vereador = e.vereador || ''
    form.justificativa = e.justificativa || ''
    form.valor = e.valor ?? null
    form.cod_scim = e.cod_scim || ''
    form.pa_empenho = e.pa_empenho || ''
    form.objeto_descricao = e.objeto_descricao || ''

    // configuracoes_extras
    const ex = e.configuracoes_extras || {}
    form.configuracoes_extras.email_contato = ex.email_contato || ''
    form.configuracoes_extras.telefone = ex.telefone || ''
    form.configuracoes_extras.endereco = ex.endereco || ''
    form.configuracoes_extras.cpf_representante = ex.cpf_representante || ''
    form.configuracoes_extras.meta_atendimentos = ex.meta_atendimentos ?? null
    form.configuracoes_extras.historico_formalizacao = ex.historico_formalizacao || ''
    form.configuracoes_extras.periodicidade_repasse = ex.periodicidade_repasse || 'Mensal'
    form.configuracoes_extras.dia_repasse = ex.dia_repasse ?? 10
    form.configuracoes_extras.status_prestacao = ex.status_prestacao || 'Em análise'
    form.configuracoes_extras.numero_parcelas = ex.numero_parcelas ?? 1
    form.configuracoes_extras.data_primeiro_repasse = ex.data_primeiro_repasse || ''

    // Parceria
    const p = e.parceria || {}
    form.parceria.ajuste_termo = p.ajuste_termo || ''
    form.parceria.gestor_parceria = p.gestor_parceria || ''
    form.parceria.projeto = p.projeto || ''
    form.parceria.inicio_atividades = p.inicio_atividades || ''   // 'YYYY-MM-DD'
    form.parceria.termino_atividades = p.termino_atividades || ''
    form.parceria.meta_mes_atendimentos = p.meta_mes_atendimentos || ''
    form.parceria.atendimento_descricao = p.atendimento_descricao || ''
    form.parceria.responsavel_entidade = p.responsavel_entidade || ''
    const pc = p.categorias || {}
    form.parceria.categorias = {
      'Saúde Mental': !!(pc['Saúde Mental']),
      'Fisioterapia': !!(pc['Fisioterapia']),
      'Fono': !!(pc['Fono'] || pc['Fonoaudiologia']),
      'Animal': !!(pc['Animal'] || pc['Causa Animal']),
      'Outros': !!(pc['Outros'])
    }
    form.parceria.especialidades = p.especialidades || {}

    // Repasses
    form.repasses = (e.repasses || []).map((r: any) => ({
      ...r,
      repasse_parcela_texto: (r.repasse_parcela ?? 0)
        .toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
      repasse_vencimento: r.repasse_vencimento || '',
      repasse_data_pagamento: r.repasse_data_pagamento || '',
      prestacao_data_entrega: r.prestacao_data_entrega || ''
    }))
  } catch (err) {
    apiError.value = 'Não foi possível carregar a entidade para edição.'
    console.error(err)
  }
}

onMounted(() => {
  if (ehEdicao.value && props.entidadeId) carregarEntidade(props.entidadeId)
})

watch(() => props.entidadeId, (novo) => {
  if (ehEdicao.value && novo) carregarEntidade(novo)
})

// Definição das chaves esperadas para cada lançamento de repasse
interface RepasseForm {
  mes_referencia: string
  repasse_oficio?: string
  repasse_periodo?: string
  repasse_parcela: number
  repasse_parcela_texto?: string // Campo auxiliar para digitação amigável (BR)
  repasse_retencao?: number
  repasse_valor_final: number
  repasse_vencimento: string
  repasse_pa?: string
  repasse_data_pagamento?: string
  prestacao_oficio?: string
  prestacao_data_entrega?: string
  prestacao_pa?: string
  prestacao_sugestao_glosa?: number
  prestacao_reconsideracao?: number
  prestacao_mts?: string
}

// Definição das chaves esperadas e da estrutura de dados da parceria
interface ParceriaForm {
  ajuste_termo: string
  inicio_atividades: string
  termino_atividades: string
  gestor_parceria: string
  projeto: string
  categorias: Record<string, boolean>
  atendimento_descricao: string
  meta_mes_atendimentos: string | null
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
  cod_scim?: string
  pa_empenho?: string
  objeto_descricao?: string
  parceria: ParceriaForm
  repasses: RepasseForm[]
  configuracoes_extras: {
    email_contato: string
    telefone: string
    meta_atendimentos: number | null
    historico_formalizacao: string
    periodicidade_repasse: string
    dia_repasse: number | null
    status_prestacao: string
    endereco?: string
    cpf_representante?: string
    numero_parcelas?: number | string
    data_primeiro_repasse?: string
  }
}

// Lista pré-definida de especialidades médicas/atendimentos comuns para seleção rápida
const poolEspecialidades = [
  'Fisioterapia', 'Fonoaudiologia', 'Psicologia', 'Terapia Ocupacional',
  'Nutrição', 'Assistência Social', 'Psicopedagogia', 'Psiquiatria',
  'Pediatria', 'Equoterapia', 'Pilates', 'Saúde Mental'
]

const listaEspecialidades = [
  "Academia Clínica", "Acupuntura", "Assistente Social", "Atividade Educativa",
  "Educador Físico", "Fisio", "Fono", "Hidroginástica/\nHidroterapia", "Massoterapeuta",
  "Médico (Neurologista)", "Musicoterapia", "Neuropediatra", "Neuropsicologia",
  "Nutricionista", "Odonto", "Oficinas Lúdicas", "Oftalmologia", "Ortopedista",
  "Pediatria", "Pilates", "Psicologia", "Psicanalista", "Psiquiatria",
  "Psicomotricista", "Psicopedagogo", "Práticas Integrativas", "Reflexologia", "T.O.", "Veterinário"
]

// Passo atual do Stepper
const currentStep = ref(1)

// Helper para converter string de moeda BR (ex: "1.500,50" ou "1500,50") em float numérico
function parseMoeda(str: string | number): number {
  if (typeof str === 'number') return str
  if (!str) return 0
  const s = String(str).trim()
  if (/^\d{1,3}(\.\d{3})*(,\d+)?$/.test(s)) {
    return parseFloat(s.replace(/\./g, '').replace(',', '.')) || 0
  }
  if (/^\d+(,\d+)?$/.test(s)) {
    return parseFloat(s.replace(',', '.')) || 0
  }
  return parseFloat(s.replace(/[^\d.]/g, '')) || 0
}

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
  cod_scim: '',
  pa_empenho: '',
  objeto_descricao: '',
  parceria: {
    ajuste_termo: '',
    inicio_atividades: '',
    termino_atividades: '',
    gestor_parceria: '',
    projeto: '',
    categorias: {
      'Saúde Mental': false,
      'Fisioterapia': false,
      'Fono': false,
      'Animal': false,
      'Outros': false
    },
    atendimento_descricao: '',
    meta_mes_atendimentos: '',
    responsavel_entidade: '',
    especialidades: {}
  },
  repasses: [],
  configuracoes_extras: {
    email_contato: '',
    telefone: '',
    meta_atendimentos: null,
    historico_formalizacao: '',
    periodicidade_repasse: 'Mensal',
    dia_repasse: 10,
    status_prestacao: 'Em análise',
    endereco: '',
    cpf_representante: '',
    numero_parcelas: 1,
    data_primeiro_repasse: ''
  }
})

// Atualiza o valor numérico com base no texto digitado da parcela (moeda BR) e formata o input
const updateRepasseParcela = (rep: RepasseForm) => {
  if (rep.repasse_parcela_texto !== undefined) {
    let raw = String(rep.repasse_parcela_texto).replace(/\D/g, '')
    if (!raw) raw = '0'
    const formatter = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    rep.repasse_parcela_texto = formatter.format(Number(raw) / 100)
    rep.repasse_parcela = parseMoeda(rep.repasse_parcela_texto)
    rep.repasse_valor_final = rep.repasse_parcela - (rep.repasse_retencao || 0)
  }
}

const formatarMesReferencia = (val: string): string => {
  let v = val.replace(/\D/g, '').slice(0, 6)
  if (v.length > 2) {
    v = `${v.slice(0, 2)}.${v.slice(2)}`
  }
  return v
}

const anosDisponiveis = Array.from({ length: 16 }, (_, i) => 2020 + i)

const atualizarMes = (rep: any, mes: string) => {
  const partes = (rep.mes_referencia || '01.2026').split('.')
  const ano = partes[1] || '2026'
  rep.mes_referencia = `${mes}.${ano}`
}

const atualizarAno = (rep: any, ano: string) => {
  const partes = (rep.mes_referencia || '01.2026').split('.')
  const mes = partes[0] || '01'
  rep.mes_referencia = `${mes}.${ano}`
}

// Estados auxiliares de interface e carregamento
const isSubmitting = ref(false)
const apiError = ref('')
const apiSuccess = ref('')

const errors = reactive({
  razao_social: '',
  cnpj: '',
  cpf_representante: '',
  email_contato: '',
  telefone: ''
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
  else if (newVal === 3) {
    emit('update-screen', 'financeiro');
    carregarResumoRepresentante();
  }
})

const gerarCronograma = () => {
  const num = parseInt(form.configuracoes_extras.numero_parcelas as string) || 0
  const dataInicioStr = form.configuracoes_extras.data_primeiro_repasse
  if (num <= 0) {
    form.repasses = []
    return
  }

  const repassesNovos = [...form.repasses]
  const valorSugerido = form.valor ? Number((form.valor / num).toFixed(2)) : 0
  const valorSugeridoFmt = valorSugerido.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  
  if (repassesNovos.length > num) {
    repassesNovos.splice(num)
  } else {
    const baseDate = dataInicioStr ? new Date(dataInicioStr + 'T12:00:00') : new Date()
    
    for (let i = repassesNovos.length; i < num; i++) {
      const dataPrevista = new Date(baseDate)
      dataPrevista.setMonth(baseDate.getMonth() + i)
      
      const ano = dataPrevista.getFullYear()
      const mesNum = String(dataPrevista.getMonth() + 1).padStart(2, '0')
      const competenciaSugerida = `${mesNum}.${ano}`
      const dataPrevistaStr = dataPrevista.toISOString().split('T')[0]
      
      repassesNovos.push({
        mes_referencia: competenciaSugerida,
        repasse_parcela: valorSugerido,
        repasse_parcela_texto: valorSugeridoFmt,
        repasse_retencao: 0,
        repasse_valor_final: valorSugerido,
        repasse_vencimento: dataPrevistaStr,
        repasse_oficio: '',
        repasse_periodo: '',
        repasse_pa: '',
        repasse_data_pagamento: '',
        prestacao_oficio: '',
        prestacao_data_entrega: '',
        prestacao_pa: '',
        prestacao_sugestao_glosa: 0,
        prestacao_reconsideracao: 0,
        prestacao_mts: ''
      })
    }
  }

  // Atualiza todas as parcelas para o valor dividido igualmente
  for (let i = 0; i < repassesNovos.length; i++) {
    repassesNovos[i].repasse_parcela = valorSugerido
    repassesNovos[i].repasse_parcela_texto = valorSugeridoFmt
    repassesNovos[i].repasse_valor_final = valorSugerido
  }
  
  form.repasses = repassesNovos
}

// Watcher para gerar o cronograma automaticamente
watch(
  [
    () => form.valor,
    () => form.configuracoes_extras.numero_parcelas,
    () => form.configuracoes_extras.data_primeiro_repasse
  ],
  () => {
    gerarCronograma()
  }
)

const somaParcelas = computed(() => {
  return form.repasses.reduce((acc, r) => acc + (Number(r.repasse_parcela) || 0), 0)
})

const somaCoincide = computed(() => {
  if (!form.valor) return somaParcelas.value === 0
  return Math.abs(somaParcelas.value - form.valor) < 0.01
})

const datasVigenciaInvalidas = computed(() => {
  const ini = form.parceria.inicio_atividades
  const fim = form.parceria.termino_atividades
  return !!(ini && fim && ini > fim)
})

const podeConcluir = computed(() => {
  if (isSubmitting.value) return false
  if (!form.valor || form.valor <= 0) return false
  if (!form.repasses || form.repasses.length === 0) return false
  return somaCoincide.value && !datasVigenciaInvalidas.value
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
      const cnpjLimpo = apenasDigitos(form.cnpj)
      if (cnpjLimpo.length !== 14 || !validarCNPJ(cnpjLimpo)) {
        errors.cnpj = 'CNPJ inválido (verifique os 14 dígitos e o dígito verificador).'
        hasErrors = true
      }
    }

    if (form.configuracoes_extras.cpf_representante) {
      const cpfLimpo = apenasDigitos(form.configuracoes_extras.cpf_representante)
      if (cpfLimpo.length !== 11 || !validarCPF(cpfLimpo)) {
        errors.cpf_representante = 'CPF do representante inválido (dígito verificador).'
        hasErrors = true
      }
    }

    // Validação de E-mail
    if (form.configuracoes_extras.email_contato) {
      const email = form.configuracoes_extras.email_contato.trim()
      const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/
      if (!emailRegex.test(email)) {
        errors.email_contato = 'E-mail institucional com formato inválido.'
        hasErrors = true
      }
    }

    // Validação de Telefone
    if (form.configuracoes_extras.telefone) {
      const telLimpo = apenasDigitos(form.configuracoes_extras.telefone)
      if (telLimpo && telLimpo.length !== 10 && telLimpo.length !== 11) {
        errors.telefone = 'O telefone deve conter exatamente 10 ou 11 dígitos numéricos.'
        hasErrors = true
      }
    }

    if (errors.cnpj || errors.cpf_representante || errors.razao_social || errors.email_contato || errors.telefone) {
      hasErrors = true
    }

    if (hasErrors) {
      focarPrimeiroErro()
      return
    }
  }
  
  if (currentStep.value === 2) {
    if (datasVigenciaInvalidas.value) {
      return
    }
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

const avisoRazaoSocial = ref('')

const idParaIgnorar = computed(() => (ehEdicao.value ? props.entidadeId : undefined))

const verificarQuaseDuplicatasNome = async () => {
  const nome = form.razao_social.trim()
  if (!nome || nome.length < 4) {
    avisoRazaoSocial.value = ''
    return
  }
  try {
    const r = await $fetch<{ duplicatas: { razao_social: string; cnpj: string }[] }>(
      '/api/entidades/check-razao', { params: { nome, ignorar_id: idParaIgnorar.value } }
    )
    if (r.duplicatas && r.duplicatas.length > 0) {
      const nomes = r.duplicatas.map(d => `${d.razao_social} (${d.cnpj || 'Sem CNPJ'})`).join(', ')
      avisoRazaoSocial.value = `Razão social muito semelhante já cadastrada: ${nomes}`
    } else {
      avisoRazaoSocial.value = ''
    }
  } catch (err) {
    console.error('Erro ao verificar quase duplicatas de nome:', err)
    avisoRazaoSocial.value = ''
  }
}

const verificarCnpj = async () => {
  const digitos = apenasDigitos(form.cnpj)
  if (!digitos) { errors.cnpj = ''; return }
  if (digitos.length !== 14) { errors.cnpj = 'O CNPJ deve conter 14 dígitos.'; return }
  if (!validarCNPJ(digitos)) { errors.cnpj = 'CNPJ inválido (dígito verificador).'; return }
  try {
    const r = await $fetch<{ existe: boolean; razao_social: string | null }>(
      '/api/entidades/check-cnpj', { params: { cnpj: digitos, ignorar_id: idParaIgnorar.value } }
    )
    if (r.existe) {
      const formatarCnpjLocal = (v: string) => {
        if (!v) return 's/ CNPJ'
        const dig = v.replace(/\D/g, '')
        if (dig.length !== 14) return v
        return dig.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
      }
      errors.cnpj = `CNPJ já cadastrado para: ${formatarCnpjLocal(digitos)} - ${r.razao_social}`
    } else {
      errors.cnpj = ''
    }
  } catch {
    errors.cnpj = '' // se a checagem online falhar, não bloqueia a digitação; o backend valida no submit
  }
}

const avisoCpf = ref<string>('')

const verificarCpf = async () => {
  avisoCpf.value = ''
  const d = apenasDigitos(form.configuracoes_extras.cpf_representante)
  if (d.length !== 11) return
  if (!validarCPF(d)) { errors.cpf_representante = 'CPF inválido (dígito verificador).'; return }
  errors.cpf_representante = ''
  try {
    const r = await $fetch<{ total_empresas: number; empresas: any[] }>(
      '/api/representantes/check-cpf', { params: { cpf: d, ignorar_id: idParaIgnorar.value } }
    )
    if (r.total_empresas > 0) {
      const formatarCnpjLocal = (v: string) => {
        if (!v) return 's/ CNPJ'
        const dig = v.replace(/\D/g, '')
        if (dig.length !== 14) return v
        return dig.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
      }
      const lista = r.empresas.map(e => `${formatarCnpjLocal(e.cnpj)} - ${e.razao_social}`).join(', ')
      avisoCpf.value = `Este CPF já é representante de ${r.total_empresas} empresa(s): ${lista}.`
    }
  } catch {
    avisoCpf.value = '' // sem conexão = sem aviso; nunca bloqueia
  }
}

interface ResumoRepresentante {
  total_empresas: number
  total_repassado: number
  empresas: { entidade_id: string; razao_social: string; cnpj: string; total_repassado: number }[]
}

const resumoRepresentante = ref<ResumoRepresentante>({
  total_empresas: 0, total_repassado: 0, empresas: []
})

const carregarResumoRepresentante = async () => {
  const d = apenasDigitos(form.configuracoes_extras.cpf_representante)
  if (d.length !== 11) {
    resumoRepresentante.value = { total_empresas: 0, total_repassado: 0, empresas: [] }
    return
  }
  try {
    resumoRepresentante.value = await $fetch<ResumoRepresentante>(
      '/api/representantes/check-cpf', { params: { cpf: d, ignorar_id: idParaIgnorar.value } }
    )
  } catch {
    // Falha de rede não pode atrapalhar a conclusão: zera o resumo e segue.
    resumoRepresentante.value = { total_empresas: 0, total_repassado: 0, empresas: [] }
  }
}

const fmtBRL = (v: number) =>
  (v || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

const cnpjPartes = computed(() => parseCnpj(form.cnpj))

const rotuloEstabelecimento = computed(() => {
  const p = cnpjPartes.value
  if (p.tipo === 'MATRIZ') return 'MATRIZ'
  if (p.tipo === 'FILIAL') return `FILIAL nº ${String(p.numeroFilial).padStart(4, '0')}`
  return '—'
})

const grupoRaiz = ref<{ estabelecimentos: any[] }>({ estabelecimentos: [] })

const verificarGrupoRaiz = async () => {
  const p = cnpjPartes.value
  if (p.raiz.length !== 8) { grupoRaiz.value = { estabelecimentos: [] }; return }
  try {
    grupoRaiz.value = await $fetch(`/api/entidades/por-raiz/${p.raiz}`)
  } catch {
    grupoRaiz.value = { estabelecimentos: [] } // tolerante a falha
  }
}

const statusBrasilApi = ref<'idle' | 'buscando' | 'ok' | 'indisponivel'>('idle')

const consultarBrasilApi = async () => {
  const d = apenasDigitos(form.cnpj)
  if (d.length !== 14 || !validarCNPJ(d)) return // só consulta CNPJ formalmente válido
  statusBrasilApi.value = 'buscando'

  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), 4000) // timeout de 4s

  try {
    const resp = await fetch(`https://brasilapi.com.br/api/cnpj/v1/${d}`, { signal: ctrl.signal })
    clearTimeout(timer)
    if (!resp.ok) { statusBrasilApi.value = 'indisponivel'; return } // 404/429/5xx → segue manual
    const dados = await resp.json()

    // Pré-preenche SOMENTE campos vazios (não sobrescreve o que o usuário já digitou).
    if (!form.razao_social && dados.razao_social) form.razao_social = dados.razao_social
    if (!form.configuracoes_extras.endereco && dados.logradouro) {
      form.configuracoes_extras.endereco =
        [dados.logradouro, dados.numero, dados.bairro, dados.municipio, dados.uf]
          .filter(Boolean).join(', ')
    }
    if (!form.configuracoes_extras.telefone && dados.ddd_telefone_1) {
      // Formata o telefone sugerido
      let tel = String(dados.ddd_telefone_1).replace(/\D/g, '')
      if (tel.length === 10) {
        form.configuracoes_extras.telefone = tel.replace(/^(\d{2})(\d{4})(\d{4})$/, '($1) $2-$3')
      } else if (tel.length === 11) {
        form.configuracoes_extras.telefone = tel.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3')
      } else {
        form.configuracoes_extras.telefone = tel
      }
    }
    statusBrasilApi.value = 'ok'
  } catch {
    clearTimeout(timer)
    statusBrasilApi.value = 'indisponivel' // abort/offline/erro → NUNCA bloqueia
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

// Máscara dinâmica para CPF
const handleCpfInput = (event: Event) => {
  const input = event.target as HTMLInputElement
  let value = input.value.replace(/\D/g, '')
  
  if (value.length > 11) {
    value = value.slice(0, 11)
  }

  if (value.length > 9) {
    value = value.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4')
  } else if (value.length > 6) {
    value = value.replace(/^(\d{3})(\d{3})(\d{0,3})$/, '$1.$2.$3')
  } else if (value.length > 3) {
    value = value.replace(/^(\d{3})(\d{0,3})$/, '$1.$2')
  }

  form.configuracoes_extras.cpf_representante = value
  errors.cpf_representante = ''
}

const valorExibicao = ref('')

const handleValorInput = (event: Event) => {
  const input = event.target as HTMLInputElement
  let value = input.value.replace(/\D/g, '')
  if (!value) {
    form.valor = null
    valorExibicao.value = ''
    return
  }
  const numValue = parseFloat(value) / 100
  form.valor = numValue
  valorExibicao.value = numValue.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  })
}

watch(() => form.valor, (newVal) => {
  if (newVal === null || newVal === undefined) {
    valorExibicao.value = ''
  } else {
    valorExibicao.value = newVal.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    })
  }
}, { immediate: true })

// Limpeza de erros específicos
const clearError = (field: 'razao_social' | 'cnpj' | 'cpf_representante' | 'email_contato' | 'telefone') => {
  errors[field] = ''
}

const focarPrimeiroErro = () => {
  nextTick(() => {
    const ordemCampos = ['cnpj', 'razao_social', 'email_contato', 'telefone', 'cpf_representante']
    for (const key of ordemCampos) {
      if (errors[key as keyof typeof errors]) {
        const el = document.getElementById(key)
        if (el) {
          el.focus()
          el.scrollIntoView({ behavior: 'smooth', block: 'center' })
          break
        }
      }
    }
  })
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
    'Fono': false,
    'Animal': false,
    'Outros': false
  }
  form.parceria.atendimento_descricao = ''
  form.parceria.meta_mes_atendimentos = ''
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
  form.configuracoes_extras.endereco = ''
  form.configuracoes_extras.cpf_representante = ''
  form.configuracoes_extras.numero_parcelas = 1
  form.configuracoes_extras.data_primeiro_repasse = ''
  
  errors.razao_social = ''
  errors.cnpj = ''
  errors.cpf_representante = ''
  currentStep.value = 1
}

const mostrarConfirmacaoModal = ref(false)

// Função de submissão integrada com a API Python (Passo 3)
const submitForm = async () => {
  apiError.value = ''
  apiSuccess.value = ''

  if (!form.valor || form.valor <= 0) {
    apiError.value = 'Informe o valor total do repasse antes de concluir.'
    return
  }
  if (!somaCoincide.value) {
    const dif = Math.abs(somaParcelas.value - (form.valor || 0))
    apiError.value = `A soma das parcelas (R$ ${somaParcelas.value.toFixed(2)}) difere do total ` +
      `(R$ ${(form.valor || 0).toFixed(2)}). Diferença de R$ ${dif.toFixed(2)}.`
    return
  }
  if (datasVigenciaInvalidas.value) {
    apiError.value = 'A data de início não pode ser posterior à data de término.'
    return
  }

  // Abre o modal de confirmação visual com resumo dos dados antes de salvar
  mostrarConfirmacaoModal.value = true
}

const efetivarCadastro = async () => {
  mostrarConfirmacaoModal.value = false
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
      cod_scim: form.cod_scim ? String(form.cod_scim).trim() : null,
      pa_empenho: form.pa_empenho ? String(form.pa_empenho).trim() : null,
      objeto_descricao: form.objeto_descricao ? String(form.objeto_descricao).trim() : null,
      
      parceria: {
        ajuste_termo: form.parceria.ajuste_termo.trim() || null,
        inicio_atividades: form.parceria.inicio_atividades || null,
        termino_atividades: form.parceria.termino_atividades || null,
        gestor_parceria: form.parceria.gestor_parceria.trim() || null,
        projeto: form.parceria.projeto.trim() || null,
        categorias: form.parceria.categorias,
        atendimento_descricao: form.parceria.atendimento_descricao.trim() || null,
        meta_mes_atendimentos: form.parceria.meta_mes_atendimentos || "",
        responsavel_entidade: form.parceria.responsavel_entidade.trim() || null,
        especialidades: form.parceria.especialidades
      },
      repasses: form.repasses.map(r => ({
        ...r,
        repasse_vencimento: r.repasse_vencimento || null,
        repasse_data_pagamento: r.repasse_data_pagamento || null,
        prestacao_data_entrega: r.prestacao_data_entrega || null
      })),
      
      configuracoes_extras: {
        email_contato: form.configuracoes_extras.email_contato.trim() || null,
        telefone: form.configuracoes_extras.telefone.replace(/\D/g, '') || null,
        meta_atendimentos: form.configuracoes_extras.meta_atendimentos,
        historico_formalizacao: form.configuracoes_extras.historico_formalizacao.trim() || null,
        periodicidade_repasse: form.configuracoes_extras.periodicidade_repasse,
        dia_repasse: form.configuracoes_extras.dia_repasse,
        status_prestacao: form.configuracoes_extras.status_prestacao,
        endereco: form.configuracoes_extras.endereco ? form.configuracoes_extras.endereco.trim() : null,
        cpf_representante: form.configuracoes_extras.cpf_representante ? form.configuracoes_extras.cpf_representante.replace(/\D/g, '') : null,
        numero_parcelas: form.configuracoes_extras.numero_parcelas,
        data_primeiro_repasse: form.configuracoes_extras.data_primeiro_repasse || null
      }
    }

    const url = ehEdicao.value ? `/api/entidades/${props.entidadeId}` : '/api/entidades'
    const metodo = ehEdicao.value ? 'PUT' : 'POST'

    const response = await $fetch<{ status: string; message: string; id: string }>(url, {
      method: metodo,
      headers: {
        'Content-Type': 'application/json'
      },
      body: payload
    })

    if (response && response.status === 'success') {
      if (ehEdicao.value) {
        apiSuccess.value = 'Alterações salvas com sucesso!'
        emit('salvo')
        emit('update-screen', 'dashboard')
      } else {
        apiSuccess.value = `Parceria, Entidade e Lançamentos Mensais cadastrados de forma atômica no PostgreSQL com sucesso! ID: ${response.id}`
        resetForm()
      }
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

const exportEtapa = async (etapa: string) => {
  try {
    if (ehEdicao.value && props.entidadeId) {
      const response = await fetch(`/api/export/entidade/${props.entidadeId}?etapa=${etapa}`)
      if (!response.ok) throw new Error('Falha ao exportar planilha Excel')
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      const secao = etapa === 'financeiro' ? 'Controle Financeiro' : (etapa === 'parceria' ? 'Dados da Parceria' : 'Formalização')
      link.download = `${form.razao_social || 'Entidade'} - ${secao}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      return
    }

    const parsedValor = form.valor ? parseMoeda(form.valor) : null
    const repassesFormatados = form.repasses ? form.repasses.map(rep => ({
      ...rep,
      repasse_parcela: rep.repasse_parcela ? parseMoeda(rep.repasse_parcela_texto || rep.repasse_parcela) : 0,
      repasse_retencao: rep.repasse_retencao ? parseMoeda(rep.repasse_retencao) : 0,
      repasse_valor_final: rep.repasse_valor_final ? parseMoeda(rep.repasse_valor_final) : 0
    })) : []

    const payload = {
      ...form,
      valor: parsedValor,
      repasses: repassesFormatados
    }

    const response = await fetch(`/api/export/dados?etapa=${etapa}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
    if (!response.ok) throw new Error('Falha ao exportar planilha Excel')
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `Prefinance_Exportacao_${(form.razao_social || 'Nova_Parceria').replace(/ /g, '_')}_${etapa}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    alert('Erro ao exportar dados da etapa.')
    console.error(error)
  }
}
</script>
<style scoped>
.import-drop {
  border: 2px dashed #93c5fd; border-radius: 12px; padding: 18px; text-align: center;
  background: #f8fafc; cursor: pointer; transition: all .2s ease; margin-bottom: 16px;
}
.import-drop.is-over { background: #eff6ff; border-color: #0b5394; }

.entity-create-container {
  width: 100%;
}

/* Header do Card */
.card-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 1.25rem;
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

/* Fim dos botões */

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