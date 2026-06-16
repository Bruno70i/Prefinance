# Passo 06 — Ponto 4: CPF já vinculado a outro CNPJ (aviso, não bloqueia)

> **Objetivo:** ao digitar o **CPF do representante**, se ele já for representante de outra(s)
> entidade(s), mostrar um **aviso informativo** com o(s) CNPJ(s) — **sem impedir** o cadastro.
> 🟡 Avisa. (Mesma pessoa pode legitimamente representar vários CNPJs.)

**Depende de:** 01 (validar CPF), 02 (coluna `cpf_representante` + índice).
**Arquivos alterados:** `main.py` (endpoint), `EntityCreateForm.vue`, `EntityForm.vue`.

---

## 6.1 Backend — endpoint `check-cpf` (somente leitura)

Este endpoint é reaproveitado pelo passo 07 (que adiciona os totais). Já o crie completo aqui.

Importe no topo: `from validadores import validar_cpf, apenas_digitos`.

```python
@app.get("/api/representantes/check-cpf")
def check_cpf(cpf: str, ignorar_id: str | None = None):
    """
    Lista as entidades em que o CPF já é representante e agrega totais.
    NÃO bloqueia nada — é informativo. `ignorar_id` exclui a própria entidade (modo edição).
    """
    if not engine:
        raise HTTPException(status_code=500, detail="Banco de dados não inicializado.")
    digitos = apenas_digitos(cpf)
    resp = {
        "valido": validar_cpf(digitos),
        "total_empresas": 0,
        "total_repassado": 0.0,
        "empresas": [],
    }
    if len(digitos) != 11:
        return resp

    with engine.connect() as conn:
        params = {"cpf": digitos}
        filtro_id = ""
        if ignorar_id:
            filtro_id = "AND e.id <> :ignorar_id"
            params["ignorar_id"] = ignorar_id

        # Empresas dessa pessoa + total já repassado (valor final efetivamente pago) por empresa.
        rows = conn.execute(text(f"""
            SELECT e.id, e.razao_social, e.cnpj,
                   COALESCE(SUM(r.repasse_valor_final) FILTER (WHERE r.repasse_data_pagamento IS NOT NULL), 0) AS total_pago
            FROM entidades e
            LEFT JOIN repasses_mensais r ON r.entidade_id = e.id
            WHERE e.cpf_representante = :cpf {filtro_id}
            GROUP BY e.id, e.razao_social, e.cnpj
            ORDER BY e.razao_social
        """), params).fetchall()

        empresas = []
        total_geral = 0.0
        for row in rows:
            total_geral += float(row.total_pago or 0)
            empresas.append({
                "entidade_id": str(row.id),
                "razao_social": row.razao_social,
                "cnpj": row.cnpj,
                "total_repassado": float(row.total_pago or 0),
            })
        resp["empresas"] = empresas
        resp["total_empresas"] = len(empresas)
        resp["total_repassado"] = total_geral
    return resp
```

> **Definição de "total já repassado":** soma de `repasse_valor_final` apenas das parcelas com
> `repasse_data_pagamento` preenchida (ou seja, **efetivamente pagas**). Se o produto preferir
> "tudo que está programado", remova o `FILTER (WHERE ... IS NOT NULL)`. Documente a escolha.

## 6.2 Frontend — aviso inline ao digitar o CPF

Campo: `form.configuracoes_extras.cpf_representante` (~linha 114 em `EntityCreateForm.vue`). Já
existe `<p v-if="errors.cpf_representante">`; adicione **um segundo elemento** para o aviso (cor
amarela), separado do erro de formato:

No `<script setup>`:
```ts
import { validarCPF, apenasDigitos } from '~/utils/validadores'

const avisoCpf = ref<string>('')

const verificarCpf = async () => {
  avisoCpf.value = ''
  const d = apenasDigitos(form.configuracoes_extras.cpf_representante)
  if (d.length !== 11) return
  if (!validarCPF(d)) { errors.cpf_representante = 'CPF inválido (dígito verificador).'; return }
  errors.cpf_representante = ''
  try {
    const r = await $fetch<{ total_empresas: number; empresas: any[] }>(
      '/api/representantes/check-cpf', { params: { cpf: d } }
    )
    if (r.total_empresas > 0) {
      const lista = r.empresas.map(e => e.cnpj || e.razao_social).join(', ')
      avisoCpf.value = `Este CPF já é representante de ${r.total_empresas} empresa(s): ${lista}.`
    }
  } catch {
    avisoCpf.value = '' // sem conexão = sem aviso; nunca bloqueia
  }
}
```

No `<template>`, adicione `@blur="verificarCpf"` no input do CPF e:
```html
<p v-if="avisoCpf" style="color:#b45309; font-size:13px; margin-top:4px">⚠️ {{ avisoCpf }}</p>
```

> **Não** adicione `avisoCpf` a nenhuma condição de bloqueio (`nextStep`, `podeConcluir`,
> `submitForm`). É puramente informativo.

## 6.3 Frontend — replicar em `EntityForm.vue` (edição)

Igual, mas passando `ignorar_id` para não contar a própria entidade:
```ts
{ params: { cpf: d, ignorar_id: formState.value.id } }
```

---

## 6.4 Critérios de aceite

- [ ] Digitar um CPF já usado em outra entidade → aviso amarelo com o(s) CNPJ(s); **cadastro segue
      permitido**.
- [ ] CPF com DV errado → erro de formato (vermelho), separado do aviso.
- [ ] Sem backend/itinerância → nenhum aviso, sem travar a digitação.
- [ ] `GET /api/representantes/check-cpf?cpf=...` retorna `total_empresas`, `total_repassado` e a
      lista `empresas`.

## 6.5 Segurança / reversão

Endpoint só leitura; front só exibe texto. Nada bloqueia. Reverter = remover `verificarCpf`, o
`<p>` e o endpoint.

> Próximo: `07-resumo-representante-conclusao.md`.
