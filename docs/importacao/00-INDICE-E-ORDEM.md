# Plano — Importar planilha (Excel/CSV) e preencher o cadastro automaticamente

> **Objetivo:** na tela **1 — Cadastro de Formalização**, adicionar uma **área de arrastar e soltar**
> (drag & drop) que aceite **`.xlsx` / `.xls` / `.csv`**. Ao anexar, o sistema **lê o arquivo e
> preenche os campos do formulário automaticamente** — o **processo inverso da exportação**.
>
> **Para quem vai implementar (IA/dev):** leia este índice antes de começar. Os passos são
> **incrementais e isolados**; na ordem abaixo, o site atual **continua funcionando**. Toda a lógica
> nova vai em **arquivos novos**; o `main.py` só ganha **uma rota nova** e o `EntityCreateForm.vue`
> ganha **um componente filho** e uma função de preenchimento.

---

## 0. Princípios (para não quebrar nem alucinar)

1. **Importar = PRÉ-PREENCHER, nunca salvar direto.** A rota de import **não grava no banco**. Ela
   lê o arquivo e devolve um JSON; o frontend usa esse JSON para **preencher o formulário**. O
   usuário revisa e clica em **"Efetivar e Concluir"** (fluxo existente) — assim **todas as
   validações já implementadas continuam valendo**.
2. **Espelho da exportação.** O parser é o **inverso** de `excel_modelo.py`. Use o documento
   `modelo/LAYOUT_EXPORT_EXCEL.md` como mapa exato de onde cada dado está em cada aba/célula.
3. **Tolerante a falha.** Arquivo inválido/ilegível → erro amigável; o cadastro continua funcionando
   normalmente (o import é um atalho, não um pré-requisito).
4. **Mapeamento determinístico em Python** (cabeçalhos → campos), com normalização de acentos/caixa.
   Nada de "adivinhar" via IA.

---

## 1. Como o arquivo é lido (resumo técnico)

A exportação gera 3 abas no layout do modelo:
- **FORMALIZAÇÃO** — cabeçalhos na **linha 2**, dados a partir da **linha 3** (a linha 1 é o banner
  mesclado).
- **DADOS DA PARCERIA** — cabeçalhos na linha 2, dados na linha 3 (inclui categorias com "X" e
  especialidades numéricas).
- **REPASSE E PRESTAÇÃO DE CONTAS** — **transposta**: rótulos na coluna D, **meses nas colunas E+**.

O parser detecta o layout pelas **abas** (`.xlsx`) ou trata o **CSV** como tabela plana (formatos
aceitos descritos no passo 01). Para `.xlsx` usamos **openpyxl** (lê célula a célula, lidando com os
cabeçalhos em 2 níveis); para `.csv`, `pandas`/`csv`.

> **Importante (campo valor):** no `EntityCreateForm.vue`, `form.valor` é `number | null` e um
> `watch` atualiza o display (`valorExibicao`) sozinho — então o preenchimento só precisa setar
> `form.valor = <número>`. Repasses usam `mes_referencia` no formato `MM.AAAA` + `repasse_parcela`
> (número) + `repasse_parcela_texto` (string BR).

---

## 2. Ordem de execução

| # | Arquivo | Entrega | Depende de |
|---|---|---|---|
| 01 | `01-backend-parser-e-rota.md` | `import_planilha.py` (parser da aba **FORMALIZAÇÃO** + CSV) e rota `POST /api/import/planilha`. Não grava nada. | — |
| 02 | `02-frontend-dropzone-e-preenchimento.md` | Componente de drag & drop na **etapa 1** + função que preenche o `form`. | 01 |
| 03 | `03-fase2-parceria-e-repasses.md` | (Fase 2) estender o parser para **DADOS DA PARCERIA** e **REPASSE**, preenchendo as etapas 2 e 3. | 01, 02 |
| 04 | `04-seguranca-edge-cases-e-aceite.md` | Casos de borda, segurança e checklist de aceite. | 02 (e 03) |

**Garantia de não quebrar:** após 01, existe uma rota nova sem uso na UI. Após 02, a importação da
**formalização** funciona ponta a ponta (entrega o pedido principal da tela 1). 03 e 04 são
incrementos.

---

## 3. Convenções

- Formatos aceitos: `.xlsx`, `.xls`, `.csv`. Tamanho máx. sugerido: 10 MB.
- O arquivo é lido **em memória** (não é salvo em disco).
- **Não sobrescrever sem avisar:** se o formulário já tiver dados, o frontend pede confirmação antes
  de preencher.
- Se a planilha tiver **várias entidades** (export geral), a tela de criação importa **a primeira** e
  avisa o usuário (ver passo 04).
- Novos módulos Python na raiz (ao lado de `excel_modelo.py`).

Prossiga para `01-backend-parser-e-rota.md`.
