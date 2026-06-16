# Plano de Implementação — Exportar Excel no layout da pasta `modelo`

> Objetivo: substituir o Excel "genérico" gerado hoje pelo backend por uma cópia fiel
> das 3 planilhas-modelo em `modelo/Planilhas_Consolidadas.xlsx` (equivalentes às 3 imagens
> `1 - FORMALIZAÇÂO.jpeg`, `2 - DADOS DA PARCERIA.jpeg`, `3 - REPASSE e PRESTAÇÃO DE CONTAS.jpeg`).

---

## 1. Diagnóstico — por que o Excel atual sai "genérico"

O site é **Nuxt 3** (frontend) + **FastAPI / `main.py`** (backend Python na porta 8000,
com proxy em `nuxt.config.ts`). O Excel é gerado em 3 endpoints no backend:

| Endpoint | Origem dos dados | Disparado por |
|---|---|---|
| `GET /api/export/geral` | banco (todas entidades) | `pages/index.vue:131` — botão "Exportar Geral" |
| `GET /api/export/entidade/{id}` | banco (1 entidade) | `components/EntityForm.vue:275` |
| `POST /api/export/dados` | dados do formulário (rascunho) | `components/EntityCreateForm.vue:1058` |

Os três usam o **mesmo padrão**: montam um `pandas.DataFrame` e chamam `df.to_excel(...)`,
depois aplicam `apply_excel_styles()` (`main.py:858`).

**Causa raiz:** `df.to_excel` só produz uma **tabela plana** (1 linha de cabeçalho + N linhas
de dados). O `apply_excel_styles` apenas pinta a linha 1 de azul-escuro (`#003366`), adiciona
bordas e auto-ajusta a largura. Isso nunca reproduz o modelo, porque o modelo **não é uma
tabela plana**: tem cabeçalhos agrupados em 2 níveis com merge, banners de título, texto
rotacionado 90°, e uma das abas é uma **tabela transposta (pivô)**. A paleta de cores também
está errada (o modelo usa `0B5394` / `9FC5E8` / `CFE2F3`, não `003366`).

---

## 2. Estrutura exata do modelo (3 abas = 3 imagens)

Inspeção de `modelo/Planilhas_Consolidadas.xlsx` via `openpyxl`.

### Aba 1 — `FORMALIZAÇÃO` (tabela em lista, 1 linha por entidade)
- **Linha 1**: 3 banners agrupados com merge → `SITUAÇÃO` (A1:B1), `ENTIDADE` (C1:D1),
  `EMENDA` (E1:L1). Fundo `0B5394`, texto branco, negrito, centralizado.
- **Linha 2**: subcabeçalhos — STATUS, HISTÓRICO, NOME, CNPJ, PA Emenda,
  Localização do PA Emenda, Emenda Alterada?, PA Formalização, N.º, Vereador,
  Justificativa, Valor. Fundo `9FC5E8`, negrito.
- **Linhas 3+**: dados, fundo listrado `CFE2F3`; HISTÓRICO é texto **multilinha numa célula só**
  (`wrap_text`).
- **Larguras**: A=15, B=55, C=45, D=20, E=15, F=15, G=15, H=15, I=8, J=20, K=35, L=15.

### Aba 2 — `DADOS DA PARCERIA` (tabela larga, ~44 colunas, 1 linha por entidade)
- **Linha 1**: banner único mesclado A1:AN1 — "RELAÇÃO DE AJUSTES VIGENTES COM TERCEIRO
  SETOR - SAÚDE". Fundo `0B5394`, texto branco.
- **Linha 2** (altura ≈ 130): cabeçalhos. Fundo `9FC5E8`. Inclui:
  - Campos fixos: ENTIDADE, AJUSTE, INÍCIO DAS ATIVIDADES, TÉRMINO DAS ATIVIDADES,
    GESTOR DA PARCERIA, PROJETO.
  - **5 colunas-categoria** (Saúde Mental, Fisioterapia, Fono, Animal, Outros) — texto
    rotacionado 90°, preenchidas com **"X"** quando a categoria está presente.
  - ATENDIMENTO, META (Mês).
  - **Matriz de 29 especialidades** (texto rotacionado 90°), preenchidas com a **meta
    numérica** de cada especialidade.
  - RESPONSÁVEL PELA ENTIDADE (última coluna).

### Aba 3 — `REPASSE E PRESTAÇÃO DE CONTAS` (tabela transposta / pivô, 1 bloco por entidade)
- **Bloco vertical esquerdo** (A2:B7): ENTIDADE / CNPJ / CÓD. SCIM / AJUSTE / P.A. EMPENHO /
  OBJETO. (A7:A21 e B7:B21 mesclados para o OBJETO ocupar a altura toda.)
- **Coluna C**: 3 seções mescladas verticalmente → REPASSE (C2:C9),
  PRESTAÇÃO DE CONTAS (C10:C15), MTS (C16:C21). Fundo `9FC5E8`.
- **Coluna D**: rótulos das linhas:
  - REPASSE: OFÍCIO, PERÍODO, PARCELA ($), RETENÇÃO ($), VALOR FINAL, VENCIMENTO, P.A.,
    DATA - PAGAMENTO.
  - PRESTAÇÃO DE CONTAS: OFÍCIO, DATA - ENTREGA, P.A., SUGESTÃO DE GLOSA ($),
    RECONSIDERAÇÃO ($), SUGESTÃO DE GLOSA (P.A.).
  - MTS: Cadastro (Termo), Atualização / Aditamento, Lançado Valores? (TSS),
    Prestado Contas? (ENTIDADE), Análise da PC? (COMISSÃO), Parecer Final?.
- **Colunas E→P**: os **meses como colunas** (2025, 01.2026 … 11.2026). Cada repasse mensal
  vira uma coluna. Células sem dado recebem `------`.

### Paleta canônica do modelo
| Elemento | Cor (ARGB) |
|---|---|
| Banner de título (linha 1) | `0B5394` (fundo) + `FFFFFF` (fonte), negrito |
| Cabeçalho (linha 2 / coluna C) | `9FC5E8` (fundo), negrito |
| Faixa de dados / labels | `CFE2F3` (fundo) |
| Bordas | `thin` em todas as células com conteúdo |

---

## 3. Mapeamento dados → modelo

O modelo de banco encaixa quase perfeitamente nas planilhas-modelo.

| Coluna do modelo | Origem no banco |
|---|---|
| FORMALIZAÇÃO (todas as colunas) | `entidades`: `situacao`, `historico`, `razao_social`, `cnpj`, `pa_emenda`, `localizacao_pa_emenda`, `emenda_alterada`, `pa_formalizacao`, `numero_emenda`, `vereador`, `justificativa`, `valor` |
| PARCERIA — campos fixos | `dados_parceria`: `ajuste_termo`, `inicio_atividades`, `termino_atividades`, `gestor_parceria`, `projeto`, `atendimento_descricao`, `meta_mes_atendimentos`, `responsavel_entidade` |
| PARCERIA — 5 categorias "X" | `dados_parceria.categorias` (JSONB) ↔ `areas_projeto` |
| PARCERIA — 29 especialidades | `dados_parceria.especialidades` (JSONB) ↔ `metas_detalhadas` `{nome: meta}` |
| REPASSE — bloco esquerdo | `entidades`: `cod_scim`, `pa_empenho`, `objeto_descricao` + `ajuste_termo` |
| REPASSE — seções/meses | `repasses_mensais` (1 linha = 1 mês), pivotado por `mes_referencia` |

As chaves do JSONB `especialidades` batem exatamente com os cabeçalhos do modelo
(incluindo `"Hidroginástica/\nHidroterapia"` com quebra de linha), confirmado em
`entidades_mapeadas.json`.

### Listas canônicas (extraídas da linha 2 do modelo)

**Categorias (colunas G–K, marcação "X"):**
```
Saúde Mental, Fisioterapia, Fono, Animal, Outros
```

**Especialidades (colunas N–AP, meta numérica), nesta ordem:**
```
Academia Clínica, Acupuntura, Assistente Social, Atividade Educativa, Educador Físico,
Fisio, Fono, Hidroginástica/\nHidroterapia, Massoterapeuta, Médico (Neurologista),
Musicoterapia, Neuropediatra, Neuropsicologia, Nutricionista, Odonto, Oficinas Lúdicas,
Oftalmologia, Ortopedista, Pediatria, Pilates, Psicologia, Psicanalista, Psiquiatria,
Psicomotricista, Psicopedagogo, Práticas Integrativas, Reflexologia, T.O., Veterinário
```

---

## 4. Decisões adotadas (defaults)

> Estes pontos foram fechados com os defaults recomendados. Onde o modelo pede mais do que o
> banco oferece hoje, o comportamento adotado está descrito abaixo.

1. **REPASSE com várias entidades (export "geral")** → **uma aba REPASSE por entidade**
   (nome da aba derivado da razão social, truncado ao limite do Excel de 31 caracteres e
   higienizado). Para export individual, a aba é idêntica ao modelo.
2. **Colunas de meses** → **derivadas dinamicamente**: 1 coluna do ano anterior (rótulo do ano,
   ex. `2025`) + 12 meses (`01.AAAA` … `12.AAAA`), onde `AAAA` é o ano de `inicio_atividades`
   (fallback: ano corrente se a data estiver ausente). Meses sem repasse recebem `------`.
3. **Seção MTS** (Cadastro, Atualização, Lançado Valores?, Prestado Contas?, Análise da PC?,
   Parecer Final?) → **renderizada com os rótulos, células de dados em branco** (o schema só
   tem `prestacao_mts`). Marcado como melhoria futura de schema.
4. **"SUGESTÃO DE GLOSA (P.A.)"** → renderizada com o rótulo, dados **em branco** (sem campo
   correspondente no banco).
5. **Números de PA azuis sublinhados** → **apenas estilo visual**, sem hyperlink real (o
   arquivo-modelo também não usa hyperlinks de fato).

---

## 5. Plano de implementação

**Estratégia:** abandonar `df.to_excel` + `apply_excel_styles` para estas 3 abas e
**construir as células diretamente com `openpyxl`**, espelhando o modelo. Toda a lógica fica
num módulo novo e reutilizável pelos 3 endpoints. Nenhuma dependência nova (`openpyxl` já está
no projeto).

### Passo 1 — Novo módulo `excel_modelo.py`
- Constantes de estilo: paleta (`0B5394` / `9FC5E8` / `CFE2F3`), fontes, bordas `thin`,
  alinhamentos (centralizado + `wrap_text`).
- Listas canônicas ordenadas das 5 categorias e 29 especialidades (seção 3).
- Helpers: `_merge_e_estiliza(ws, range, fill, font, ...)`, formatação de moeda
  `R$ #,##0.00`, formatação de datas `dd/mm/aaaa`.

### Passo 2 — `build_sheet_formalizacao(ws, entidades)`
- Escreve os 3 banners da linha 1 (merges A1:B1 / C1:D1 / E1:L1) + subcabeçalhos da linha 2.
- 1 linha por entidade; `Histórico` com `wrap_text`; `Valor` como número (`R$ #,##0.00`).
- Aplica as larguras fixas do modelo e a faixa `CFE2F3` nas linhas de dados.

### Passo 3 — `build_sheet_parceria(ws, entidades)`
- Banner A1:AN1; cabeçalho na linha 2 com altura ≈ 130 e especialidades/categorias em
  `textRotation=90`.
- Por entidade: campos fixos + **"X"** nas categorias presentes em `categorias` + meta
  numérica nas colunas de `especialidades` (lookup por nome canônico; chave inexistente na
  lista é ignorada).

### Passo 4 — `build_sheet_repasse(ws, entidade, repasses)`
- Monta o bloco esquerdo (labels verticais A2:B7, OBJETO mesclado), a coluna C com as 3 seções
  mescladas e a coluna D com os rótulos.
- Gera as colunas de meses (Passo decisão 4.2), pivota `repasses_mensais` por `mes_referencia`,
  preenche `------` onde não há dado. Datas e valores formatados. MTS / Glosa (P.A.) em branco.

### Passo 5 — Refatorar os 3 endpoints
Arquivos/linhas atuais: `main.py:919` (geral), `main.py:1048` (entidade), `main.py:1189` (dados).
- Substituir os blocos `pd.DataFrame(...).to_excel(...)` e o loop `apply_excel_styles` por:
  criar `Workbook()`, chamar os builders apropriados conforme o filtro `etapa`
  (`todos` / `formalizacao` / `parceria` / `financeiro`).
- No `geral`: uma aba `FORMALIZAÇÃO`, uma `DADOS DA PARCERIA`, e N abas REPASSE (uma por
  entidade) — conforme decisão 4.1.
- Manter `StreamingResponse`, `media_type` e os nomes de arquivo atuais.
- `apply_excel_styles` pode ser mantido apenas para abas legadas ou removido.

### Passo 6 — Validação
- Gerar export com os dados de exemplo (`entidades_mapeadas.json`) e comparar célula a célula
  com as 3 imagens / o `.xlsx` modelo: merges, cores, rotação, larguras, faixas, formatos de
  moeda e data.

**Frontend:** nenhuma mudança — botões e endpoints permanecem iguais; muda apenas o conteúdo
gerado pelo backend.

---

## 6. Riscos / pontos de atenção
- **Encoding**: garantir UTF-8 ao escrever strings com acentos (o `main.py` já trata isso).
- **Especialidades fora da lista canônica**: ignorar (ou logar) chaves do JSONB que não existam
  nos cabeçalhos do modelo.
- **Performance no "geral"**: uma aba REPASSE por entidade pode gerar muitas abas — validar com
  volume real de dados.
- **Schema MTS**: as 6 linhas da seção MTS ficam vazias até o schema ganhar campos próprios
  (melhoria futura, fora do escopo deste plano).
- **Dependências**: nenhuma nova lib necessária (`openpyxl` já presente).

---

## 7. Resumo do escopo
- ✅ Backend: novo módulo `excel_modelo.py` + refatoração dos 3 endpoints de export.
- ✅ Saída idêntica ao layout das 3 planilhas-modelo.
- ⛔ Sem mudanças de frontend.
- ⛔ Sem mudanças de schema nesta etapa (MTS / Glosa P.A. ficam em branco).
