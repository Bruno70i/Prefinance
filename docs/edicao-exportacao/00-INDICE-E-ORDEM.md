# Plano — Unificar Edição com o Cadastro + Exportação por Entidade

> **Para quem vai implementar (IA ou dev):** leia este índice inteiro antes de tocar em qualquer
> arquivo. Os passos são **incrementais e reversíveis** — na ordem abaixo, o site **nunca quebra**
> entre um passo e outro.

---

## 0. O problema (diagnóstico preciso)

Existem **dois formulários diferentes** com **fontes de dados diferentes**:

| | Criação ("Nova Parceria") | Edição ("Editar") |
|---|---|---|
| Componente | `components/EntityCreateForm.vue` (wizard 3 passos) | `components/EntityForm.vue` (modal com abas) |
| Grava em | **colunas reais** (`situacao`, `historico`, `pa_emenda`, …) + tabelas `dados_parceria` e `repasses_mensais` | **JSONB legado** `configuracoes_extras.formalizacao / .parceria / .financeiro_detalhes` |
| Passos/labels | Cadastro de Formalização · Dados da Parceria · Controle Financeiro | Processo de Formalização · Dados da Parceria · Fluxo de Repasses |
| Cronograma de repasses | ✅ mostra e edita | ❌ não mostra |

**Consequência:** os campos do "Editar" **não batem** com o cadastro real. Editar parceria/financeiro
no modal grava no JSONB legado, não nas tabelas — e o que é exportado (que lê as tabelas reais) não
corresponde ao que o modal mostra.

**Boa notícia:** o backend **já está pronto** para o modelo certo:
- `PUT /api/entidades/{id}` (`update_entidade`, ~linha 824 de `main.py`) já faz DELETE+INSERT de
  `dados_parceria` e `repasses_mensais` a partir do schema `EntidadeCreate` (com `parceria` e
  `repasses` aninhados) — exatamente o mesmo payload que o wizard de criação envia.
- Só falta um `GET /api/entidades/{id}` que devolva os dados **aninhados** para popular o wizard.

---

## 1. A decisão central de arquitetura

**Reutilizar o `EntityCreateForm.vue` (wizard) para CRIAR e EDITAR.** Assim os campos e labels são
**os mesmos por construção** (uma única fonte da verdade). O `EntityForm.vue` é **aposentado**.

> Alternativa rejeitada: reescrever o `EntityForm.vue` para imitar o wizard. Isso recria duas
> fontes da verdade e o problema volta no futuro. Não faça.

---

## 2. O que muda na exportação (requisitos do cliente)

- ❌ **Remover** o botão "Exportar Geral (Excel)" do topo do dashboard (`pages/index.vue`).
- ✅ **Adicionar** um botão "Exportar" **por empresa**, na coluna "Ações" do dashboard, ao lado de
  "Editar" e "Excluir" (`components/EntitySelector.vue`) → gera a planilha **só daquela** entidade.
- ✅ **Exportar por etapa** (Cadastro de Formalização · Dados da Parceria · Controle Financeiro)
  disponível **durante o preenchimento** (criação) **e** **na edição**.

Endpoints de exportação já existentes e reaproveitados (não precisam ser criados):
- `POST /api/export/dados?etapa=` → exporta o **rascunho** (corpo do formulário). Usado na **criação**.
- `GET /api/export/entidade/{id}?etapa=` → exporta dados **persistidos**. Usado na **edição** e no
  botão por linha do dashboard (`etapa=todos` para a planilha completa).

> `etapa` aceita: `formalizacao`, `parceria`, `financeiro`, `todos`.

---

## 3. Ordem de execução (obrigatória)

| # | Arquivo | Entrega | Depende de |
|---|---|---|---|
| 01 | `01-backend-get-entidade-completa.md` | `GET /api/entidades/{id}` com dados aninhados (formalização + parceria + repasses). **Aditivo**, não muda UI. | — |
| 02 | `02-edicao-reusa-wizard.md` | `EntityCreateForm.vue` ganha **modo de edição** (props `modo`/`entidadeId`, carregar, PUT). Ainda **não religa** o dashboard. Criação continua igual. | 01 |
| 03 | `03-dashboard-exportar-por-entidade.md` | Dashboard: "Editar" abre o wizard em edição; **remover** "Exportar Geral"; **adicionar** "Exportar" por linha. | 02 |
| 04 | `04-limpeza-e-criterios-de-aceite.md` | Remover `EntityForm.vue` + modal; limpezas opcionais; checklist final de aceite. | 03 |

**Garantia de não quebrar:** após o passo 01, nada muda na tela. Após o 02, criar continua
funcionando e o modo edição existe mas ainda não é usado. Após o 03, "Editar" usa o wizard. Após o
04, o código morto é removido.

---

## 4. Convenções

- **Não** criar campos novos: a edição deve usar **exatamente** os campos/labels do wizard de
  criação (Cadastro de Formalização · Dados da Parceria · Controle Financeiro).
- Datas trafegam como `YYYY-MM-DD` (string) entre front e back; valores como número.
- `mes_referencia` no formato `MM.AAAA` (já padronizado no projeto).
- Em **modo edição**, todas as checagens de validação (`check-cnpj`, `check-cpf`, `check-razao`)
  devem passar `ignorar_id` = id da entidade editada, para não acusar a si mesma.
- Testar após **cada** passo (seção "Critérios de aceite" de cada arquivo).

Prossiga para `01-backend-get-entidade-completa.md`.
