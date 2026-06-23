# Passo 03 — (Fase 2) Importar Dados da Parceria e Repasses

> **Objetivo:** estender o parser para ler as abas **DADOS DA PARCERIA** e **REPASSE E PRESTAÇÃO DE
> CONTAS** do `.xlsx` no layout do modelo, preenchendo também as **etapas 2 e 3** do wizard. Assim a
> importação cobre o cadastro inteiro (round-trip completo da exportação).
>
> É a parte mais complexa (a aba de repasse é **transposta**). Faça **depois** que a Fase 1 (passos
> 01–02) estiver funcionando.

**Depende de:** 01, 02.
**Arquivos alterados:** `import_planilha.py`, `components/EntityCreateForm.vue`.

---

## 3.1 Backend — parser da aba DADOS DA PARCERIA

Cabeçalhos na **linha 2**, dados na **linha 3**. Veja `modelo/LAYOUT_EXPORT_EXCEL.md` §4.

Acrescente a `import_planilha.py`:

```python
import datetime

MAPA_PARCERIA = {
    "AJUSTE": "ajuste_termo",
    "INICIO DAS ATIVIDADES": "inicio_atividades",
    "TERMINO DAS ATIVIDADES": "termino_atividades",
    "GESTOR DA PARCERIA": "gestor_parceria",
    "PROJETO": "projeto",
    "ATENDIMENTO": "atendimento_descricao",
    "META (MES)": "meta_mes_atendimentos",
    "RESPONSAVEL PELA ENTIDADE": "responsavel_entidade",
}
CATEGORIAS = ["Saúde Mental", "Fisioterapia", "Fono", "Animal", "Outros"]
# Lista canônica de especialidades (mesma ordem do modelo — ver excel_modelo.py)
ESPECIALIDADES = [
    "Academia Clínica", "Acupuntura", "Assistente Social", "Atividade Educativa", "Educador Físico",
    "Fisio", "Fono", "Hidroginástica/\nHidroterapia", "Massoterapeuta", "Médico (Neurologista)",
    "Musicoterapia", "Neuropediatra", "Neuropsicologia", "Nutricionista", "Odonto", "Oficinas Lúdicas",
    "Oftalmologia", "Ortopedista", "Pediatria", "Pilates", "Psicologia", "Psicanalista", "Psiquiatria",
    "Psicomotricista", "Psicopedagogo", "Práticas Integrativas", "Reflexologia", "T.O.", "Veterinário",
]


def _parse_data(v):
    """'15/01/2026' ou datetime -> 'YYYY-MM-DD' (ou None)."""
    if v is None or str(v).strip() in ("", "------"):
        return None
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.strftime("%Y-%m-%d")
    s = str(v).strip()
    m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", s)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    return None


def parse_parceria_xlsx(wb) -> dict:
    ws = _achar_aba(wb, "PARCERIA")
    if not ws:
        return {}
    headers = [_norm(c.value) for c in ws[2]]
    valores = [c.value for c in ws[3]]
    por_norm = {h: v for h, v in zip(headers, valores)}

    parceria = {}
    for hnorm, campo in MAPA_PARCERIA.items():
        v = por_norm.get(hnorm)
        if v is None or str(v).strip() == "":
            continue
        if campo in ("inicio_atividades", "termino_atividades"):
            parceria[campo] = _parse_data(v)
        elif campo == "meta_mes_atendimentos":
            parceria[campo] = _parse_valor(v) or 0
        else:
            parceria[campo] = str(v).strip()

    # categorias (X) e especialidades (número) — casa pelo nome normalizado da coluna
    cats = {}
    esp = {}
    for c in CATEGORIAS:
        v = por_norm.get(_norm(c))
        if v is not None and str(v).strip().upper() == "X":
            cats[c] = True
    for e in ESPECIALIDADES:
        v = por_norm.get(_norm(e))
        if v is not None and str(v).strip() not in ("", "0"):
            try:
                esp[e] = int(float(str(v).replace(",", ".")))
            except ValueError:
                pass
    if cats:
        parceria["categorias"] = cats
    if esp:
        parceria["especialidades"] = esp
    return parceria
```

## 3.2 Backend — parser da aba REPASSE (transposta)

Estrutura (ver `modelo/LAYOUT_EXPORT_EXCEL.md` §5): rótulos na **coluna D** (linhas 2–15), **meses
nas colunas E+** (linha 1). Cada coluna de mês vira um repasse; células `------` significam vazio.

```python
# Linha (na aba) -> campo do repasse, conforme o layout do modelo.
LINHA_REPASSE = {
    2: "repasse_oficio", 3: "repasse_periodo", 4: "repasse_parcela", 5: "repasse_retencao",
    6: "repasse_valor_final", 7: "repasse_vencimento", 8: "repasse_pa", 9: "repasse_data_pagamento",
    10: "prestacao_oficio", 11: "prestacao_data_entrega", 12: "prestacao_pa",
    13: "prestacao_sugestao_glosa", 14: "prestacao_reconsideracao",
}
CAMPOS_DATA_REP = {"repasse_vencimento", "repasse_data_pagamento", "prestacao_data_entrega"}
CAMPOS_MOEDA_REP = {"repasse_parcela", "repasse_retencao", "repasse_valor_final",
                    "prestacao_sugestao_glosa", "prestacao_reconsideracao"}


def parse_repasses_xlsx(wb) -> list:
    ws = _achar_aba(wb, "REPASSE")
    if not ws:
        return []
    repasses = []
    # colunas de mês começam na coluna 5 (E). O cabeçalho do mês está na linha 1.
    for col in range(5, ws.max_column + 1):
        rotulo_mes = ws.cell(row=1, column=col).value
        mes = str(rotulo_mes).strip() if rotulo_mes else ""
        if not re.match(r"^\d{2}\.\d{4}$", mes):  # ignora a coluna do ano anterior (ex.: '2025')
            continue
        rep = {"mes_referencia": mes}
        tem_dado = False
        for linha, campo in LINHA_REPASSE.items():
            v = ws.cell(row=linha, column=col).value
            if v is None or str(v).strip() in ("", "------"):
                continue
            if campo in CAMPOS_DATA_REP:
                rep[campo] = _parse_data(v)
            elif campo in CAMPOS_MOEDA_REP:
                rep[campo] = _parse_valor(v) or 0
            else:
                rep[campo] = str(v).strip()
            tem_dado = True
        if tem_dado:
            repasses.append(rep)
    return repasses
```

## 3.3 Backend — incluir Fase 2 no retorno

Em `parse_formalizacao_xlsx`, antes do `return`, abra o mesmo workbook e agregue:
```python
def parse_formalizacao_xlsx(conteudo: bytes) -> dict:
    wb = openpyxl.load_workbook(io.BytesIO(conteudo), data_only=True)
    # ... (lê FORMALIZAÇÃO como no passo 01) ...
    parceria = parse_parceria_xlsx(wb)
    repasses = parse_repasses_xlsx(wb)
    return {"formalizacao": primeira, "parceria": parceria or None,
            "repasses": repasses, "avisos": avisos}
```
(Reaproveite o `wb` já aberto; não abra duas vezes.)

## 3.4 Frontend — aplicar parceria e repasses

Adicione ao `EntityCreateForm.vue` (usadas pelo `aplicarImportacao` do passo 02):

```ts
function aplicarParceria(p: any): number {
  let n = 0
  const campos = ['ajuste_termo', 'gestor_parceria', 'projeto', 'inicio_atividades',
    'termino_atividades', 'meta_mes_atendimentos', 'atendimento_descricao', 'responsavel_entidade']
  for (const k of campos) {
    if (p[k] !== undefined && p[k] !== null && p[k] !== '') { (form.parceria as any)[k] = p[k]; n++ }
  }
  if (p.categorias && typeof p.categorias === 'object') { form.parceria.categorias = { ...p.categorias }; n++ }
  if (p.especialidades && typeof p.especialidades === 'object') { form.parceria.especialidades = { ...p.especialidades }; n++ }
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
  return form.repasses.length
}
```

> Como o passo 02 já chama `aplicarParceria?.(...)` e `aplicarRepasses?.(...)` de forma opcional, ao
> definir essas funções a Fase 2 passa a funcionar automaticamente.

---

## 3.5 Critérios de aceite

- [ ] Reimportar um `.xlsx` completo preenche também a etapa 2 (ajuste, gestor, datas, categorias com
      "X", especialidades) e a etapa 3 (cronograma de repasses com os meses corretos).
- [ ] Datas viram `YYYY-MM-DD`; valores viram número; `mes_referencia` fica `MM.AAAA`.
- [ ] A coluna do ano anterior ("2025") e colunas só com `------` são ignoradas.
- [ ] A soma das parcelas importadas confere com o total (a validação da etapa 3 valida na hora de
      efetivar).

## 3.6 Segurança / reversão

Aditivo ao parser. Reverter = remover as funções novas e voltar o `return` da Fase 1.

> Próximo: `04-seguranca-edge-cases-e-aceite.md`.
