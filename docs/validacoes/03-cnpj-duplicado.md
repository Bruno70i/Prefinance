# Passo 03 — Ponto 1: "Esse CNPJ já existe"

> **Objetivo:** impedir cadastro de CNPJ duplicado e, principalmente, **dizer de qual entidade**
> o CNPJ já é. Inclui validação de **dígito verificador** (rejeita CNPJ falso). 🔴 Bloqueia.
>
> Regra: a unicidade é pelo **CNPJ completo de 14 dígitos**. Filiais têm CNPJ diferente (ordem
> `0002`+) → são entidades distintas e **podem** coexistir. CPF, telefone e gestor **não** são
> únicos.

**Depende de:** 01 (validadores), 02 (CNPJ normalizado/índice único).
**Arquivos alterados:** `main.py` (novo endpoint + guard no create/update), `EntityCreateForm.vue`,
`EntityForm.vue`.

---

## 3.1 Backend — endpoint de checagem (somente leitura)

Adicione em `main.py` (perto dos outros GET de entidades). Importe os validadores no topo:
`from validadores import validar_cnpj, apenas_digitos`.

```python
@app.get("/api/entidades/check-cnpj")
def check_cnpj(cnpj: str):
    """Retorna se o CNPJ já existe e, em caso afirmativo, qual entidade o possui."""
    if not engine:
        raise HTTPException(status_code=500, detail="Banco de dados não inicializado.")
    digitos = apenas_digitos(cnpj)
    resposta = {"existe": False, "valido": validar_cnpj(digitos), "entidade_id": None, "razao_social": None}
    if len(digitos) != 14:
        return resposta
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT id, razao_social FROM entidades
            WHERE regexp_replace(cnpj, '\\D', '', 'g') = :d
            LIMIT 1
        """), {"d": digitos}).fetchone()
        if row:
            resposta["existe"] = True
            resposta["entidade_id"] = str(row.id)
            resposta["razao_social"] = row.razao_social
    return resposta
```

## 3.2 Backend — bloqueio no create/update (autoridade)

Em `create_entidade`, **antes do INSERT**:

```python
from validadores import validar_cnpj, apenas_digitos  # garanta o import no topo

_cnpj_digitos = apenas_digitos(entidade.cnpj or "")
if _cnpj_digitos:
    if not validar_cnpj(_cnpj_digitos):
        raise HTTPException(status_code=400, detail="CNPJ inválido (dígito verificador não confere).")
    dup = conn.execute(text("""
        SELECT razao_social FROM entidades
        WHERE regexp_replace(cnpj, '\\D', '', 'g') = :d LIMIT 1
    """), {"d": _cnpj_digitos}).fetchone()
    if dup:
        raise HTTPException(status_code=409, detail=f"CNPJ já cadastrado para: {dup.razao_social}")
```

Em `update_entidade`, faça igual mas **excluindo a própria entidade**:
`AND id <> :id` no WHERE, com bind `{"d": _cnpj_digitos, "id": entidade_id}`.

> Coloque esse trecho **dentro** do `with engine.begin() as conn:` para reusar a conexão.

## 3.3 Frontend — checagem inline (UX)

Em `EntityCreateForm.vue`, o campo CNPJ já dispara `handleCnpjInput`. Adicione uma checagem no
`blur` e o uso do validador do passo 01.

No `<template>`, no input de CNPJ (~linha 88), acrescente `@blur="verificarCnpj"`. Já existe
`<p v-if="errors.cnpj">{{ errors.cnpj }}</p>` para exibir a mensagem.

No `<script setup>`:
```ts
import { validarCNPJ, apenasDigitos } from '~/utils/validadores'

const verificarCnpj = async () => {
  const digitos = apenasDigitos(form.cnpj)
  if (!digitos) { errors.cnpj = ''; return }
  if (digitos.length !== 14) { errors.cnpj = 'O CNPJ deve conter 14 dígitos.'; return }
  if (!validarCNPJ(digitos)) { errors.cnpj = 'CNPJ inválido (dígito verificador).'; return }
  try {
    const r = await $fetch<{ existe: boolean; razao_social: string | null }>(
      '/api/entidades/check-cnpj', { params: { cnpj: digitos } }
    )
    errors.cnpj = r.existe ? `CNPJ já cadastrado para: ${r.razao_social}` : ''
  } catch {
    errors.cnpj = '' // se a checagem online falhar, não bloqueia a digitação; o backend valida no submit
  }
}
```

Reforce o `nextStep()` (~linha 685) para também checar o **DV** (hoje só checa comprimento):
```ts
if (form.cnpj) {
  const d = apenasDigitos(form.cnpj)
  if (d.length !== 14 || !validarCNPJ(d)) {
    errors.cnpj = 'CNPJ inválido (verifique os 14 dígitos e o dígito verificador).'
    hasErrors = true
  }
}
```

No `submitForm` (~linha 968), trate o **409** vindo do backend e exiba em `apiError` (a UI já
mostra `apiError`). O `$fetch`/`fetch` deve capturar `response.status === 409` e usar o `detail`.

## 3.4 Frontend — replicar em `EntityForm.vue` (edição)

Mesma função `verificarCnpj`, mas na edição **ignore o próprio registro**: como o backend já faz
`AND id <> :id`, basta que o `check-cnpj` inline não trave a própria entidade. Opcional: passar o
`id` atual e ignorar no front se `entidade_id === idAtual`.

---

## 3.5 Critérios de aceite

- [ ] Tentar cadastrar um CNPJ que já existe → mensagem **"CNPJ já cadastrado para: {Razão}"**,
      bloqueia o submit (backend retorna 409).
- [ ] Digitar CNPJ com DV errado → "CNPJ inválido (dígito verificador)" e não avança de passo.
- [ ] Editar uma entidade **sem mudar** o CNPJ → salva normalmente (não acusa duplicata de si mesma).
- [ ] `GET /api/entidades/check-cnpj?cnpj=00000000000191` responde `{existe, valido, razao_social}`.

## 3.6 Segurança / reversão

- O endpoint novo é só leitura. Os guards no create/update só **rejeitam dados realmente
  inválidos/duplicados** — não afetam cadastros válidos. Para reverter, remova os blocos
  adicionados.

> Próximo: `04-datas-vigencia.md`.
