# Plano de Implementação — Robustez de Validações (PreFinance)

> **Para quem vai implementar (IA ou dev):** leia este índice inteiro antes de tocar em qualquer
> arquivo. Cada passo é **incremental, aditivo e reversível** — feito na ordem abaixo, o site
> **nunca quebra** entre um passo e outro. Não pule etapas: vários passos dependem da fundação
> criada nos primeiros.

---

## 0. Contexto do projeto (mapa rápido)

- **Backend:** FastAPI em `main.py` (raiz). Porta 8000. SQLAlchemy + PostgreSQL via `text()`.
  - Criação de entidade: função `create_entidade` (`@app.post("/api/entidades")`, ~linha 220).
  - Atualização: `update_entidade` (`@app.put("/api/entidades/{entidade_id}")`, ~linha 499).
  - Modelos Pydantic: `EntidadeCreate` (~92), `ParceriaCreate` (~61), `RepasseCreate` (~74).
- **Frontend:** Nuxt 3 + Vue 3 (Composition API, `<script setup lang="ts">`).
  - Form de **criação** (wizard 3 passos): `components/EntityCreateForm.vue`.
  - Form de **edição**: `components/EntityForm.vue`.
  - Proxy `/api/**` → `http://localhost:8000` (ver `nuxt.config.ts`).
- **Banco:** tabelas `entidades`, `dados_parceria` (1:1), `repasses_mensais` (1:N).
  - CPF do representante hoje vive **dentro do JSONB** `configuracoes_extras.cpf_representante`
    (não é coluna, não é indexável). O passo 02 corrige isso.

> ⚠️ **Regra de ouro:** o **frontend valida para UX**, mas o **backend é a autoridade**. Toda
> regra de bloqueio precisa existir **também** no servidor. Nunca confie só no cliente.

---

## 1. Ordem de execução (obrigatória)

| # | Arquivo | O que entrega | Depende de |
|---|---|---|---|
| 01 | `01-fundacao-validadores.md` | Funções puras de validação de CNPJ/CPF (com dígito verificador) e parsing matriz/filial. Front (`utils/validadores.ts`) + back (`validadores.py`). **Não liga nada ainda** — 100% aditivo. | — |
| 02 | `02-migracao-schema.md` | Migração de banco: colunas `cpf_representante`, `telefone`, `cnpj_raiz`, `cnpj_ordem`, índices e backfill. Persistir CPF na coluna no create/update. | — |
| 03 | `03-cnpj-duplicado.md` | Ponto 1: aviso "CNPJ já existe (de qual entidade)". Endpoint `check-cnpj` + bloqueio no submit + mensagem inline. | 01, 02 |
| 04 | `04-datas-vigencia.md` | Ponto 2: início ≤ término, com aviso na seção "Dados da Parceria". Front + validação Pydantic. | — |
| 05 | `05-bloqueio-soma-parcelas.md` | Ponto 3: soma das parcelas tem de bater com o total para "efetivar". Bloqueio front + back. | — |
| 06 | `06-cpf-vinculo-aviso-inline.md` | Ponto 4: ao digitar CPF, avisar (não bloqueia) que já é representante de outro CNPJ. Endpoint `check-cpf`. | 01, 02 |
| 07 | `07-resumo-representante-conclusao.md` | **Requisito novo #1:** no passo final, painel informativo com nº de empresas dessa pessoa e total já repassado entre todas. Não bloqueia. | 02, 06 |
| 08 | `08-matriz-filial.md` | Ponto 5: badge dinâmico MATRIZ/FILIAL e agrupamento por raiz. Endpoint `por-raiz`. | 01, 02 |
| 09 | `09-brasilapi-cnpj-nao-bloqueante.md` | Dica complementar #2: auto-preenchimento via BrasilAPI **totalmente opcional e não-bloqueante** (se a API cair, cadastra normal). | 01, 08 (recomendado) |
| 10 | `10-dicas-extras.md` | Demais melhorias: padronizar `mes_referencia`, normalização, CHECKs de banco, quase-duplicatas, modal de confirmação. | vários |

**Recomendação de priorização (valor/esforço):** 01 → 05 → 04 → 03 → 02 → 06 → 07 → 08 → 09 → 10.
(01 destrava tudo; 05 e 04 são bloqueios baratos e de alto impacto; 02 é pré-requisito de 06/07/08.)

---

## 2. Taxonomia de severidade (decisão de produto)

Toda validação se encaixa em uma destas categorias. Use a cor/comportamento correspondente.

| Severidade | Comportamento | Casos |
|---|---|---|
| 🔴 **Bloqueia** | Impede avançar/concluir. Mensagem vermelha. | CNPJ inválido (DV), CNPJ duplicado exato, soma das parcelas ≠ total, início > término |
| 🟡 **Avisa** | Informa, **não impede**. Banner amarelo. | CPF já é representante de outro CNPJ; filial detectada; nome muito parecido com existente; total já repassado pela pessoa |
| 🔵 **Auxilia** | Conveniência opcional. | Auto-preenchimento BrasilAPI; sugestão de parcelas |

> **Requisitos novos do cliente são SEMPRE 🟡 ou 🔵 — nunca bloqueiam:**
> 1. Resumo de empresas/total repassado da pessoa (arquivo 07) → 🟡 informativo.
> 2. Consulta BrasilAPI (arquivo 09) → 🔵 opcional; **se falhar, o cadastro continua normalmente.**

---

## 3. Convenções para o implementador

- **Não remova** código existente sem necessidade; prefira adicionar guard clauses e computeds.
- **Normalização:** CNPJ e CPF são sempre comparados/armazenados como **apenas dígitos**
  (`replace(/\D/g, '')` no front; `re.sub(r'\D', '', x)` no back).
- **Datas:** no payload do front vão como `YYYY-MM-DD` (string do `<input type="date">`); no
  backend são `date` do Pydantic. Mantenha esse contrato.
- **Aplicar nos DOIS forms:** toda regra de UX precisa ser replicada em `EntityCreateForm.vue`
  **e** `EntityForm.vue`. Por isso o passo 01 centraliza as funções num único `utils/`.
- **Testar após cada passo:** cada arquivo tem uma seção **"Critérios de aceite"**. Rode o app
  (`uvicorn main:app --reload` + `npm run dev`) e valide antes de seguir.
- **Rollback:** cada passo tem seção **"Segurança / reversão"**. Mudanças de schema usam
  `IF NOT EXISTS` e são idempotentes.

---

## 4. Resumo dos artefatos novos (visão geral)

**Arquivos novos:**
- `utils/validadores.ts` (front) e `validadores.py` (back) — passo 01.
- `migrations/2026_validacoes.sql` + `run_migration.py` — passo 02.
- `composables/useValidacaoEntidade.ts` (front, opcional) — centraliza chamadas de checagem.

**Endpoints novos (todos GET, somente leitura, não afetam fluxos atuais):**
- `GET /api/entidades/check-cnpj?cnpj=` — passo 03.
- `GET /api/representantes/check-cpf?cpf=` — passos 06 e 07.
- `GET /api/entidades/por-raiz/{raiz}` — passo 08.

**Endpoints alterados (apenas ganham validações de bloqueio, retrocompatíveis):**
- `create_entidade` e `update_entidade` — passos 03, 04, 05 (e persistência de CPF no 02).

Prossiga para `01-fundacao-validadores.md`.
