# Passo 02 — Wizard ganha modo de edição (fonte única de campos)

> **Objetivo:** fazer o `EntityCreateForm.vue` (o wizard de "Nova Parceria") funcionar também para
> **editar** uma entidade existente. Assim, edição e criação têm **exatamente os mesmos campos e
> labels** (Cadastro de Formalização · Dados da Parceria · Controle Financeiro).
>
> Este passo **não religa** o dashboard ainda — a criação continua 100% igual. O modo edição passa a
> existir, pronto para o passo 03 usar.

**Depende de:** 01 (`GET /api/entidades/{id}`).
**Arquivos alterados:** `components/EntityCreateForm.vue`.

---

## 2.1 Novas props

Hoje (≈ linha 551):
```ts
const props = defineProps<{
  activeScreen?: string
}>()
const emit = defineEmits(['update-screen'])
```
Altere para:
```ts
const props = defineProps<{
  activeScreen?: string
  modo?: 'criar' | 'editar'      // default 'criar'
  entidadeId?: string | null     // preenchido apenas em edição
}>()
const emit = defineEmits(['update-screen', 'salvo']) // 'salvo' avisa o dashboard p/ atualizar a lista
const ehEdicao = computed(() => props.modo === 'editar' && !!props.entidadeId)
```

## 2.2 Carregar a entidade no modo edição

Crie a função que busca o endpoint do passo 01 e popula o `form` (o objeto reativo já existente).
Mapeie campo a campo, formatando o que o template espera (ex.: `repasse_parcela_texto`).

```ts
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

    // configuracoes_extras (mantém chaves que o form usa)
    const ex = e.configuracoes_extras || {}
    form.configuracoes_extras.email_contato = ex.email_contato || ''
    form.configuracoes_extras.telefone = ex.telefone || ''
    form.configuracoes_extras.endereco = ex.endereco || ''
    form.configuracoes_extras.cpf_representante = ex.cpf_representante || ''
    // ... demais chaves de configuracoes_extras que o form já usa, se houver

    // Parceria
    const p = e.parceria || {}
    form.parceria.ajuste_termo = p.ajuste_termo || ''
    form.parceria.gestor_parceria = p.gestor_parceria || ''
    form.parceria.projeto = p.projeto || ''
    form.parceria.inicio_atividades = p.inicio_atividades || ''   // 'YYYY-MM-DD'
    form.parceria.termino_atividades = p.termino_atividades || ''
    form.parceria.meta_mes_atendimentos = p.meta_mes_atendimentos || 0
    form.parceria.atendimento_descricao = p.atendimento_descricao || ''
    form.parceria.responsavel_entidade = p.responsavel_entidade || ''
    form.parceria.categorias = p.categorias || {}
    form.parceria.especialidades = p.especialidades || {}

    // Repasses → recria o cronograma do wizard, com o texto de moeda BR
    form.repasses = (e.repasses || []).map((r: any) => ({
      ...r,
      repasse_parcela_texto: (r.repasse_parcela ?? 0)
        .toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
      repasse_vencimento: r.repasse_vencimento || '',
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
```

> Ajuste a lista de chaves de `form.configuracoes_extras` para casar com o que o `form` já declara
> (veja o `reactive(form ...)` no componente). Não invente chaves novas; apenas preencha as
> existentes.

## 2.3 Submeter: POST (criar) ou PUT (editar)

No `submitForm`, o POST está fixo (≈ linha 1445):
```ts
const response = await $fetch('/api/entidades', { method: 'POST', headers, body: payload })
```
Troque por um branch:
```ts
const url = ehEdicao.value ? `/api/entidades/${props.entidadeId}` : '/api/entidades'
const metodo = ehEdicao.value ? 'PUT' : 'POST'
const response = await $fetch<any>(url, { method: metodo, headers: { 'Content-Type': 'application/json' }, body: payload })
```
O `payload` é o **mesmo** (o `EntidadeCreate` com `parceria` + `repasses`) — o `update_entidade`
já aceita esse formato.

Na ramificação de sucesso:
```ts
if (ehEdicao.value) {
  apiSuccess.value = 'Alterações salvas com sucesso!'
  emit('salvo')                       // o dashboard recarrega a lista
  emit('update-screen', 'dashboard')  // volta para a tela de consulta
} else {
  apiSuccess.value = `Parceria cadastrada com sucesso! ID: ${response.id}`
  resetForm()
}
```

## 2.4 Validações em modo edição (passar `ignorar_id`)

As checagens hoje chamam os endpoints **sem** `ignorar_id` (assumem criação). Em edição, isso
acusaria a própria entidade como "CNPJ duplicado". Ajuste para incluir o id quando `ehEdicao`:

```ts
const idParaIgnorar = computed(() => (ehEdicao.value ? props.entidadeId : undefined))

// Exemplos (aplicar nas 3 verificações):
// check-cnpj:
{ params: { cnpj: digitos, ignorar_id: idParaIgnorar.value } }
// check-cpf:
{ params: { cpf: d, ignorar_id: idParaIgnorar.value } }
// check-razao:
{ params: { nome, ignorar_id: idParaIgnorar.value } }
```
(O backend já aceita `ignorar_id` opcional nesses endpoints.)

## 2.5 Rótulo do botão e título (cosmético)

- Botão final (≈ linha 463): label dinâmico
  `{{ ehEdicao ? 'Salvar Alterações' : 'Efetivar e Concluir Cadastro' }}`.
- (Opcional) Cabeçalho do wizard pode mostrar a razão social quando em edição.

> **Importante:** mantenha o `podeConcluir` (bloqueio da soma de parcelas) e a validação de datas
> também na edição — são as mesmas regras já implementadas.

---

## 2.6 Critérios de aceite

- [ ] Renderizar `<EntityCreateForm modo="editar" :entidade-id="ID" />` (teste temporário) carrega
      todos os campos da entidade nos 3 passos, incluindo o **cronograma de repasses**.
- [ ] Salvar em edição faz `PUT /api/entidades/{id}` e persiste em `dados_parceria` e
      `repasses_mensais` (confirme no banco).
- [ ] Em edição, o CNPJ da própria entidade **não** é acusado como duplicado.
- [ ] Criar uma nova parceria **continua funcionando** exatamente como antes (modo `criar`).

## 2.7 Segurança / reversão

As mudanças são guardadas por `ehEdicao` (default `criar`). Sem `modo="editar"`, o comportamento é
idêntico ao atual. Reverter = remover as props e os branches.

> Próximo: `03-dashboard-exportar-por-entidade.md`.
