# Passo 04 — Segurança, "Baixar modelo", casos de borda e aceite

> **Objetivo:** fechar a feature de importação com as proteções, a funcionalidade **"Baixar modelo
> de importação"**, o tratamento de casos de borda e o checklist final de validação fim a fim.

**Depende de:** 02 (e 03, se a Fase 2 for feita).
**Arquivos alterados:** `main.py` (1 rota nova), `components/EntityCreateForm.vue` (1 botão).

---

## 4.1 Segurança

1. **Não grava no banco.** A rota `/api/import/planilha` só **lê** o arquivo e devolve JSON. A
   persistência continua sendo o botão "Efetivar e Concluir" (com **todas** as validações já
   implementadas: CNPJ/CPF com DV, datas, soma das parcelas, duplicidade, etc.).
2. **Leitura em memória.** O arquivo nunca é salvo em disco.
3. **Limite de tamanho** (10 MB) e **extensões restritas** (`.xlsx`, `.xls`, `.csv`).
4. **Sem execução de fórmulas.** Use `openpyxl.load_workbook(..., data_only=True)` para ler o
   **valor** das células (não a fórmula).
5. **Confirmação antes de sobrescrever** dados já digitados (feito no passo 02).

## 4.2 Casos de borda (como tratar)

| Situação | Comportamento esperado |
|---|---|
| Arquivo com **várias entidades** (export geral) | Importa **a primeira** e avisa: "O arquivo contém N entidades; importada {nome}." |
| Aba **FORMALIZAÇÃO** ausente (ex.: CSV só de repasses) | Retorna o que conseguir; aviso "Aba de Formalização não encontrada". |
| Cabeçalho com nome diferente | O mapa normaliza acentos/caixa e aceita aliases. Se não casar, o campo é ignorado (não quebra). |
| Célula de valor como texto "R$ 1.234,56" | `_parse_valor` converte para `1234.56`. |
| Data em formato Excel real (datetime) | `_parse_data` aceita datetime e `dd/mm/aaaa`. |
| `------` (placeholder do modelo) | Tratado como vazio. |
| Arquivo corrompido / não-planilha | `400` com mensagem amigável; a tela não quebra. |
| CSV com `;` ou `,` | Delimitador detectado automaticamente. |
| Encoding com acento (Windows) | CSV lido como `utf-8-sig` com `errors="replace"`. |

---

## 4.3 Funcionalidade: "Baixar modelo de importação"

> Gera um arquivo **em branco** com **os cabeçalhos exatos** que o importador entende, para o
> usuário preencher offline e reimportar. Reaproveita o `excel_modelo.py`, garantindo que o modelo
> baixado seja **100% compatível** com o parser (passos 01/03) — o template é o mesmo layout da
> exportação, só que vazio.

### 4.3.1 Backend — rota `GET /api/import/modelo`

Em `main.py` (perto da rota `/api/import/planilha`). `io`, `openpyxl`, `excel_modelo` e
`StreamingResponse` já estão importados no projeto.

```python
@app.get("/api/import/modelo")
def baixar_modelo_importacao(formato: str = "xlsx"):
    """Gera um arquivo EM BRANCO com os cabeçalhos esperados pela importação."""
    # --- CSV simples: só os cabeçalhos da Formalização (formato horizontal) ---
    if formato == "csv":
        import csv as _csv
        headers = ["STATUS", "HISTÓRICO", "NOME", "CNPJ", "PA Emenda", "Localização do PA Emenda",
                   "Emenda Alterada?", "PA Formalização", "N.º", "Vereador", "Justificativa", "Valor"]
        buf = io.StringIO()
        w = _csv.writer(buf, delimiter=";")
        w.writerow(headers)
        w.writerow([""] * len(headers))  # uma linha em branco para preencher
        dados = ("﻿" + buf.getvalue()).encode("utf-8")  # BOM p/ Excel abrir com acento certo
        return StreamingResponse(
            io.BytesIO(dados),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="Modelo_Importacao_PreFinance.csv"'},
        )

    # --- XLSX: reusa o layout do modelo (3 abas) SEM dados ---
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # remove a aba padrão vazia
    # As funções abaixo definem o título da própria aba e escrevem só os cabeçalhos quando a lista é vazia
    excel_modelo.build_sheet_formalizacao(wb.create_sheet("tmp1"), [])
    excel_modelo.build_sheet_parceria(wb.create_sheet("tmp2"), [])
    excel_modelo.build_sheet_repasse(wb.create_sheet("tmp3"), {"razao_social": ""}, [])

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return StreamingResponse(
        out,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="Modelo_Importacao_PreFinance.xlsx"'},
    )
```

> **Por que funciona:** `build_sheet_formalizacao(ws, [])` e `build_sheet_parceria(ws, [])` escrevem
> o banner + a linha de cabeçalhos e, como a lista de entidades é vazia, **não geram linhas de
> dados** — exatamente um template em branco. `build_sheet_repasse(ws, {"razao_social": ""}, [])`
> monta a grade transposta (rótulos + colunas de meses) com placeholders `------` para o usuário
> preencher. Os títulos das abas são definidos pelas próprias funções ("FORMALIZAÇÃO", "DADOS DA
> PARCERIA", "REPASSE"), então os nomes temporários `tmp1/2/3` são sobrescritos.

### 4.3.2 Frontend — botão ao lado do drag & drop (etapa 1)

No `EntityCreateForm.vue`, logo abaixo (ou dentro) da área de import criada no passo 02:

```html
<div style="display:flex; gap:10px; align-items:center; margin-top:6px">
  <button type="button" class="btn btn-secondary btn-sm" @click.stop="baixarModeloImportacao('xlsx')">
    ⬇️ Baixar modelo (Excel)
  </button>
  <button type="button" class="btn btn-secondary btn-sm" @click.stop="baixarModeloImportacao('csv')">
    ⬇️ Baixar modelo (CSV)
  </button>
</div>
```
> `@click.stop` evita que o clique no botão também dispare o seletor de arquivo do drag & drop (que
> tem `@click` na div pai).

```ts
function baixarModeloImportacao(formato: 'xlsx' | 'csv' = 'xlsx') {
  const link = document.createElement('a')
  link.href = `/api/import/modelo?formato=${formato}`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
```

### 4.3.3 Critérios de aceite (modelo)

- [ ] `GET /api/import/modelo` baixa um `.xlsx` com 3 abas (FORMALIZAÇÃO, DADOS DA PARCERIA, REPASSE)
      **sem linhas de dados**.
- [ ] `GET /api/import/modelo?formato=csv` baixa um CSV com os cabeçalhos da Formalização + 1 linha
      em branco; abre no Excel com acentos corretos.
- [ ] Preencher o modelo baixado e reimportá-lo pelo drag & drop **preenche o formulário** (round-trip
      perfeito, pois o template é o mesmo layout que o parser lê).

---

## 4.4 Recomendações de UX (opcionais)

- **Pré-visualização antes de aplicar:** em vez de preencher direto, mostrar um resumo ("Vamos
  preencher: Razão Social, CNPJ, Valor…") com botão "Aplicar". Reduz surpresa.
- **Seleção de entidade** quando o arquivo tem várias: listar as entidades e deixar o usuário
  escolher qual importar (evolução do "importa a primeira").

## 4.5 Checklist de aceite (fim a fim)

**Fase 1 (Formalização)**
- [ ] Drag & drop visível na etapa 1; aceita `.xlsx`/`.xls`/`.csv`.
- [ ] Reimportar um `.xlsx` exportado pelo sistema preenche Razão Social, CNPJ, Valor (formatado),
      Status, PA Emenda, PA Formalização, Nº Emenda, Vereador, Justificativa, Histórico.
- [ ] CSV (horizontal e vertical) funciona.
- [ ] Confirmação ao sobrescrever; erro amigável em arquivo inválido.

**Modelo de importação**
- [ ] Botões "Baixar modelo (Excel)" e "Baixar modelo (CSV)" presentes na etapa 1.
- [ ] O modelo baixado, preenchido e reimportado, preenche o formulário corretamente.

**Fase 2 (Parceria + Repasses) — se implementada**
- [ ] Etapa 2 preenchida: ajuste, gestor, vigência, categorias ("X"), especialidades, meta.
- [ ] Etapa 3 preenchida: cronograma de repasses com meses (`MM.AAAA`) e valores corretos.
- [ ] Soma das parcelas confere com o total ao efetivar.

**Robustez / não-regressão**
- [ ] A importação **não grava** nada sozinha — só preenche o formulário.
- [ ] Efetivar após importar passa pelas validações normais.
- [ ] Nenhuma rota/funcionalidade existente foi quebrada (exportação, edição, chat, dashboard).

## 4.6 Teste manual sugerido

1. Na etapa 1, clique em **"Baixar modelo (Excel)"** → abra o arquivo e confira as 3 abas em branco.
2. Preencha a aba FORMALIZAÇÃO (e, se Fase 2, as demais) e salve.
3. Arraste esse arquivo na área de import → confira os campos preenchidos.
4. Alternativamente, exporte uma entidade existente e reimporte-a para validar o round-trip.
5. Ajuste o que quiser e clique em **Efetivar** → confirme que salvou corretamente.
6. Teste um CSV simples e um arquivo inválido (ex.: um `.pdf` renomeado) para ver o erro amigável.

---

## 4.7 Resumo dos artefatos

| Arquivo | Papel |
|---|---|
| `import_planilha.py` | Parser de `.xlsx`/CSV → campos do formulário (inverso de `excel_modelo.py`) |
| `main.py` (alterado) | +rota `POST /api/import/planilha` (lê) e +rota `GET /api/import/modelo` (baixa template) |
| `components/EntityCreateForm.vue` (alterado) | Drag & drop na etapa 1 + funções de preenchimento + botões "Baixar modelo" |

> Fim do plano. Volte ao `00-INDICE-E-ORDEM.md` para a visão geral.
