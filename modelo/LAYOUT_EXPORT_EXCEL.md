# Especificação de Layout — Exportação Excel (PreFinance)

> **Backup explicativo.** Este documento descreve, em detalhe, **como o site exporta as
> planilhas Excel** — layout e formatação — para que o resultado seja idêntico às planilhas
> desta pasta `modelo/` (`Planilhas_Consolidadas.xlsx` e as 3 imagens de referência).
>
> Serve como referência para reconstruir ou auditar a exportação caso o código se perca.
> A implementação de referência está em `excel_modelo.py` (raiz do projeto), consumida pelos
> endpoints de exportação do backend (`main.py`).

---

## 1. Visão geral

A exportação gera um arquivo `.xlsx` com **3 abas**, cada uma espelhando uma das planilhas-modelo:

| Aba | Tipo de layout | Imagem de referência |
|---|---|---|
| `FORMALIZAÇÃO` | Tabela em lista (1 linha por entidade) | `1 - FORMALIZAÇÂO.jpeg` |
| `DADOS DA PARCERIA` | Tabela larga, 43 colunas (1 linha por entidade) | `2 - DADOS DA PARCERIA.jpeg` |
| `REPASSE E PRESTAÇÃO DE CONTAS` | Tabela transposta/pivô (1 aba por entidade) | `3 - REPASSE e PRESTAÇÃO DE CONTAS.jpeg` |

**Importante:** o layout **não é uma tabela plana**. Usa cabeçalhos com merge, banners de título,
texto rotacionado 90°, faixas alternadas e, na aba de repasse, uma estrutura transposta com os
meses como colunas. Por isso, a exportação é construída **célula a célula com `openpyxl`** — não
com `pandas.to_excel` (que só produz tabelas planas e foi o que gerava o layout "genérico"
antigo).

---

## 2. Padrões visuais globais

### 2.1 Paleta de cores (ARGB hex)

| Constante | Hex | Uso |
|---|---|---|
| Azul escuro | `0B5394` | Fundo dos banners de título (linha 1) |
| Azul médio | `9FC5E8` | Fundo dos cabeçalhos (linha 2) e rótulos da aba de repasse |
| Azul muito claro | `CFE2F3` | Faixa de fundo alternada nas linhas de dados |
| Branco | `FFFFFF` | Texto sobre fundo azul escuro |

### 2.2 Fontes (todas **Arial**)

| Papel | Tamanho | Estilo |
|---|---|---|
| Título / banner | 11 | Negrito, branco |
| Cabeçalho | 10 | Negrito |
| Dado | 10 | Normal |
| Dado em destaque (rótulos do bloco esquerdo da aba de repasse) | 10 | Negrito |

### 2.3 Bordas

Borda **fina (`thin`) cinza `C0C0C0`** em todos os 4 lados de **todas as células com conteúdo**
(títulos, cabeçalhos e dados).

### 2.4 Formato de moeda

Aplicado a todos os valores monetários:

```
"R$ "#,##0.00;"R$ "(#,##0.00);"R$ "-";@
```

(Positivo → `R$ 1.234,56`; negativo → `R$ (1.234,56)`; zero → `R$ -`; texto → como está.)

### 2.5 Formato de data

Sempre `dd/mm/aaaa`. Datas recebidas como `YYYY-MM-DD` (string) ou objeto `date`/`datetime`
são convertidas para esse formato.

---

## 3. Aba `FORMALIZAÇÃO`

Tabela em lista: **1 linha por entidade**.

### Linha 1 — banners de título (merge, fundo `0B5394`, fonte branca, centralizado, altura 25)

| Merge | Texto |
|---|---|
| `A1:B1` | SITUAÇÃO |
| `C1:D1` | ENTIDADE |
| `E1:L1` | EMENDA |

### Linha 2 — subcabeçalhos (fundo `9FC5E8`, negrito, centralizado, `wrap`, altura 25)

| Col | Cabeçalho |
|---|---|
| A | STATUS |
| B | HISTÓRICO |
| C | NOME |
| D | CNPJ |
| E | PA Emenda |
| F | Localização do PA Emenda |
| G | Emenda Alterada? |
| H | PA Formalização |
| I | N.º |
| J | Vereador |
| K | Justificativa |
| L | Valor |

### Linhas 3+ — dados

- **Faixa alternada:** linhas ímpares recebem fundo `CFE2F3`; pares ficam sem preenchimento.
- **Alinhamento por coluna:**
  - B (Histórico): esquerda + `wrap` (texto multilinha em uma célula só).
  - L (Valor): direita, formato de moeda.
  - A, D, E, G, H, I (Status, CNPJ, PAs, N.º, Alterada?): centralizado.
  - Demais: esquerda.

### Larguras de coluna (fixas)

| A | B | C | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15 | 55 | 45 | 20 | 15 | 15 | 15 | 15 | 8 | 20 | 35 | 15 |

### Origem dos dados (campos da entidade)

`situacao`, `historico`, `razao_social`, `cnpj`, `pa_emenda`, `localizacao_pa_emenda`,
`emenda_alterada`, `pa_formalizacao`, `numero_emenda`, `vereador`, `justificativa`, `valor`.

---

## 4. Aba `DADOS DA PARCERIA`

Tabela larga de **43 colunas (A–AQ)**, **1 linha por entidade**.

### Linha 1 — banner único (merge `A1:AQ1`, fundo `0B5394`, branco, centralizado, altura 25)

Texto: **RELAÇÃO DE AJUSTES VIGENTES COM TERCEIRO SETOR - SAÚDE**

### Linha 2 — cabeçalhos (fundo `9FC5E8`, negrito, **altura ≈ 130**)

Ordem das colunas (1→43):

1. **Campos fixos (1–6):** ENTIDADE, AJUSTE, INÍCIO DAS ATIVIDADES, TÉRMINO DAS ATIVIDADES,
   GESTOR DA PARCERIA, PROJETO.
2. **Categorias (7–11) — texto rotacionado 90°:** Saúde Mental, Fisioterapia, Fono, Animal,
   Outros.
3. **Campos (12–13):** ATENDIMENTO, META (Mês).
4. **Especialidades (14–42) — texto rotacionado 90°:** ver lista canônica abaixo.
5. **Coluna 43:** RESPONSÁVEL PELA ENTIDADE.

> **Rotação 90°** aplica-se às colunas 7–11 (categorias) e 14–42 (especialidades). É o que faz a
> altura da linha 2 ser ≈ 130.

#### Lista canônica das 29 especialidades (ordem exata, colunas 14–42)

```
Academia Clínica, Acupuntura, Assistente Social, Atividade Educativa, Educador Físico,
Fisio, Fono, Hidroginástica/⏎Hidroterapia, Massoterapeuta, Médico (Neurologista),
Musicoterapia, Neuropediatra, Neuropsicologia, Nutricionista, Odonto, Oficinas Lúdicas,
Oftalmologia, Ortopedista, Pediatria, Pilates, Psicologia, Psicanalista, Psiquiatria,
Psicomotricista, Psicopedagogo, Práticas Integrativas, Reflexologia, T.O., Veterinário
```

> `Hidroginástica/⏎Hidroterapia` contém uma **quebra de linha** entre as duas palavras (`\n`).

### Linhas 3+ — dados

- **Faixa alternada:** ímpares com fundo `CFE2F3`.
- **Categorias (7–11):** marca **"X"** quando a categoria está presente na lista `categorias`
  da entidade; caso contrário, vazio.
- **Especialidades (14–42):** preenche a **meta numérica** vinda do dicionário `especialidades`
  (`{nome: meta}`). O nome é casado de forma tolerante a quebras de linha/espaços; chave que não
  exista na lista canônica é ignorada.
- **Alinhamento:** colunas 3–4 (datas), 7–11 (categorias) e 14–42 (especialidades) centralizadas;
  demais à esquerda com `wrap`.

### Larguras de coluna

| Colunas | Largura |
|---|---|
| 1, 5, 6, 12 (Entidade, Gestor, Projeto, Atendimento) | 30 |
| 2, 13, 43 (Ajuste, Meta, Responsável) | 20 |
| 3, 4 (datas) | 15 |
| 7–11 e 14–42 (categorias e especialidades) | 6 |

### Origem dos dados (campos da parceria)

`razao_social`, `ajuste_termo`, `inicio_atividades`, `termino_atividades`, `gestor_parceria`,
`projeto`, `categorias` (lista), `atendimento_descricao`, `meta_mes_atendimentos`,
`especialidades` (dicionário nome→meta), `responsavel_entidade`.

---

## 5. Aba `REPASSE E PRESTAÇÃO DE CONTAS`

Tabela **transposta (pivô)**: o nome da aba é a **razão social da entidade** (higienizada de
`\ / ? * [ ]` e truncada a 31 caracteres). No export geral, gera-se **uma aba por entidade**.

### 5.1 Colunas de meses (dinâmicas)

As colunas E em diante são os meses. São derivadas do **ano de `inicio_atividades`** (`ano_base`;
fallback: ano atual):

```
[ <ano_base − 1> , 01.<ano_base> , 02.<ano_base> , … , 12.<ano_base> ]
```

Exemplo com início em 2026 → colunas: `2025`, `01.2026`, `02.2026`, …, `12.2026`
(1 coluna do ano anterior + 12 meses = 13 colunas, E a Q).

### 5.2 Linha 1 — cabeçalho (fundo `0B5394`, branco, centralizado, altura 25)

- `A1:D1` mesclado = **ENTIDADE**.
- Colunas E+ = os rótulos de mês (ver 5.1).

### 5.3 Bloco esquerdo (colunas A–B, rótulos em negrito à direita, valores à esquerda)

| Linha | A (rótulo) | B (valor) |
|---|---|---|
| 2 | ENTIDADE: | razão social |
| 3 | CNPJ | cnpj |
| 4 | CÓD. SCIM: | cod_scim |
| 5 | AJUSTE: | ajuste_termo |
| 6 | P.A. EMPENHO: | pa_empenho |
| 7 | OBJETO: | objeto_descricao |

- `A7:A21` e `B7:B21` são **mesclados** (o rótulo OBJETO e seu texto ocupam a altura do bloco
  inteiro, com `wrap`).

### 5.4 Coluna C — seções (merge vertical, fundo `9FC5E8`, negrito, centralizado)

| Merge | Seção |
|---|---|
| `C2:C9` | REPASSE |
| `C10:C15` | PRESTAÇÃO DE CONTAS |
| `C16:C21` | MTS |

### 5.5 Coluna D — rótulos das linhas (fundo `9FC5E8`, negrito)

| Linha | Rótulo | Seção |
|---|---|---|
| 2 | OFÍCIO | REPASSE |
| 3 | PERÍODO | REPASSE |
| 4 | PARCELA ($) | REPASSE |
| 5 | RETENÇÃO ($) | REPASSE |
| 6 | VALOR FINAL | REPASSE |
| 7 | VENCIMENTO | REPASSE |
| 8 | P.A. | REPASSE |
| 9 | DATA - PAGAMENTO | REPASSE |
| 10 | OFÍCIO | PRESTAÇÃO DE CONTAS |
| 11 | DATA - ENTREGA | PRESTAÇÃO DE CONTAS |
| 12 | P.A. | PRESTAÇÃO DE CONTAS |
| 13 | SUGESTÃO DE GLOSA ($) | PRESTAÇÃO DE CONTAS |
| 14 | RECONSIDERAÇÃO ($) | PRESTAÇÃO DE CONTAS |
| 15 | SUGESTÃO DE GLOSA (P.A.) | PRESTAÇÃO DE CONTAS |
| 16 | Cadastro (Termo) | MTS |
| 17 | Atualização / Aditamento | MTS |
| 18 | Lançado Valores? (TSS) | MTS |
| 19 | Prestado Contas? (ENTIDADE) | MTS |
| 20 | Análise da PC? (COMISSÃO) | MTS |
| 21 | Parecer Final? | MTS |

### 5.6 Células de dados (colunas de mês × linhas 2–21)

Cada coluna de mês é preenchida a partir do repasse daquele mês (`mes_referencia` no formato
`MM.AAAA`). Mapeamento linha → campo:

| Linha | Campo | Tipo |
|---|---|---|
| 2 | repasse_oficio | texto |
| 3 | repasse_periodo | texto |
| 4 | repasse_parcela | moeda |
| 5 | repasse_retencao | moeda |
| 6 | repasse_valor_final | moeda |
| 7 | repasse_vencimento | data |
| 8 | repasse_pa | texto |
| 9 | repasse_data_pagamento | data |
| 10 | prestacao_oficio | texto |
| 11 | prestacao_data_entrega | data |
| 12 | prestacao_pa | texto |
| 13 | prestacao_sugestao_glosa | moeda |
| 14 | prestacao_reconsideracao | moeda |
| 15 | SUGESTÃO DE GLOSA (P.A.) | **sempre vazio** (sem campo no banco) |
| 16–21 | MTS | **sempre vazio** (sem campo no banco) |

**Regras de preenchimento:**
- Se **não há repasse** para o mês → a célula recebe o marcador **`------`**.
- Linha 15 (Glosa P.A.) e linhas 16–21 (MTS): em branco quando há repasse; `------` quando não há.
- Valores monetários ausentes (mas com repasse presente) → `R$ -` (zero formatado).
- Todas as células de dados são centralizadas.

### 5.7 Larguras de coluna

| A | B | C | D | E+ (meses) |
|---|---|---|---|---|
| 15 | 50 | 25 | 25 | 15 cada |

### Origem dos dados

- Bloco esquerdo: `razao_social`, `cnpj`, `cod_scim`, `ajuste_termo`, `pa_empenho`,
  `objeto_descricao` (da entidade).
- Colunas de mês: lista de `repasses_mensais` da entidade, pivotada por `mes_referencia`.

---

## 6. Decisões de projeto (defaults adotados)

1. **Uma aba REPASSE por entidade** no export geral (nome = razão social truncada a 31 chars).
2. **Colunas de meses dinâmicas**: ano anterior + 12 meses do ano de `inicio_atividades`.
3. **Seção MTS**: rótulos exibidos, dados **em branco** (o banco só possui `prestacao_mts`).
4. **"SUGESTÃO DE GLOSA (P.A.)"**: rótulo exibido, dado **em branco** (sem campo no banco).
5. **PAs azuis sublinhados** das imagens: são **apenas estilo visual**, não hyperlinks reais.
6. **Meses sem repasse**: preenchidos com o marcador `------`.

---

## 7. Resumo técnico

- **Biblioteca:** `openpyxl` (construção célula a célula — **não** `pandas.to_excel`).
- **Arquivo de referência da implementação:** `excel_modelo.py`
  (`build_sheet_formalizacao`, `build_sheet_parceria`, `build_sheet_repasse`).
- **Consumido por:** endpoints de exportação em `main.py`
  (`/api/export/geral`, `/api/export/entidade/{id}`, `/api/export/dados`).
- **Sem dependências novas** além do que o projeto já usa.
