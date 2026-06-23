# Passo 02 — Frontend: drag & drop na etapa 1 + preenchimento automático

> **Objetivo:** na **etapa 1 (Cadastro de Formalização)** do `EntityCreateForm.vue`, adicionar uma
> área de **arrastar e soltar** que aceite `.xlsx`/`.xls`/`.csv`, chame a rota do passo 01 e
> **preencha o formulário** com os dados retornados.

**Depende de:** 01.
**Arquivos alterados:** `components/EntityCreateForm.vue`.

---

## 2.1 Onde colocar

Dentro da etapa 1, logo abaixo do cabeçalho "Cadastro de Formalização" (perto do botão "Exportar
Etapa (Excel)"). Assim o usuário entende que é o par "importar ↔ exportar".

## 2.2 Marcação (template)

Adicione este bloco no `<template>`, na seção da etapa 1:

```html
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
```

## 2.3 Lógica (script setup)

```ts
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

// Verifica se o formulário já tem dados (para pedir confirmação antes de sobrescrever)
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

// Aplica os dados retornados ao `form`. Retorna a quantidade de campos preenchidos.
function aplicarImportacao(data: any): number {
  let n = 0
  const f = data.formalizacao || {}

  // chaves que vão direto em form.*
  const diretos = [
    'razao_social', 'cnpj', 'situacao', 'historico', 'pa_emenda', 'localizacao_pa_emenda',
    'emenda_alterada', 'pa_formalizacao', 'numero_emenda', 'vereador', 'justificativa',
    'cod_scim', 'pa_empenho', 'objeto_descricao'
  ]
  for (const k of diretos) {
    if (f[k] !== undefined && f[k] !== null && f[k] !== '') { (form as any)[k] = f[k]; n++ }
  }
  // valor é número; o watch de form.valor atualiza o display (valorExibicao) sozinho
  if (f.valor !== undefined && f.valor !== null) { form.valor = Number(f.valor); n++ }

  // chaves de configuracoes_extras, se vierem
  const extras = ['email_contato', 'telefone', 'endereco', 'cpf_representante']
  for (const k of extras) {
    if (f[k] !== undefined && f[k] !== null && f[k] !== '') {
      (form.configuracoes_extras as any)[k] = f[k]; n++
    }
  }

  // Fase 2: se vier parceria/repasses, preenche etapas 2 e 3 (ver passo 03)
  if (data.parceria) n += aplicarParceria?.(data.parceria) ?? 0
  if (Array.isArray(data.repasses) && data.repasses.length) n += aplicarRepasses?.(data.repasses) ?? 0

  return n
}
```

> `aplicarParceria` e `aplicarRepasses` são definidas no passo 03 (Fase 2). O uso opcional
> (`?.(...) ?? 0`) evita erro caso ainda não existam.

## 2.4 Estilo (opcional)

```html
<style scoped>
.import-drop {
  border: 2px dashed #93c5fd; border-radius: 12px; padding: 18px; text-align: center;
  background: #f8fafc; cursor: pointer; transition: all .2s ease; margin-bottom: 16px;
}
.import-drop.is-over { background: #eff6ff; border-color: #0b5394; }
</style>
```

---

## 2.5 Critérios de aceite

- [ ] Na etapa 1 aparece a área "Arraste um Excel/CSV aqui…".
- [ ] Arrastar (ou clicar e selecionar) um `.xlsx` exportado pelo sistema **preenche** Razão Social,
      CNPJ, Valor, Status, PA, etc.; o campo Valor mostra "R$ ..." formatado.
- [ ] Importar com o formulário já preenchido pede **confirmação** antes de sobrescrever.
- [ ] Arquivo inválido/ilegível → mensagem de erro vermelha, sem quebrar a tela.
- [ ] Após importar, o usuário ainda precisa clicar em **Efetivar** (as validações continuam valendo).

## 2.6 Segurança / reversão

Tudo isolado na etapa 1. Reverter = remover o bloco do template e as funções. Nenhum dado é gravado
pela importação.

> Próximo (opcional): `03-fase2-parceria-e-repasses.md`.
