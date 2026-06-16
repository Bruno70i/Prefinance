# Passo 04 — Ponto 2: Início da vigência ≤ Término

> **Objetivo:** impedir que a data de **início das atividades** seja posterior à de **término**,
> com aviso na seção **"Dados da Parceria"** (onde estão os campos de calendário). 🔴 Bloqueia.

**Depende de:** nada.
**Arquivos alterados:** `main.py` (validação Pydantic), `EntityCreateForm.vue`, `EntityForm.vue`.

---

## 4.1 Backend — validação no modelo `ParceriaCreate`

Em `main.py`, no modelo `ParceriaCreate` (~linha 61), adicione um validador de modelo. Importe
`model_validator` do pydantic no topo: `from pydantic import BaseModel, Field, ConfigDict, model_validator`.

```python
class ParceriaCreate(BaseModel):
    # ... campos existentes ...

    @model_validator(mode="after")
    def _validar_vigencia(self):
        if self.inicio_atividades and self.termino_atividades:
            if self.inicio_atividades > self.termino_atividades:
                raise ValueError("A data de início não pode ser posterior à data de término.")
        return self
```

> O FastAPI converte `ValueError` de validação em **422** automaticamente. Se preferir 400 com
> mensagem amigável, faça a checagem dentro de `create_entidade`/`update_entidade` e levante
> `HTTPException(400, "A data de início não pode ser posterior à data de término.")`.

## 4.2 Frontend — aviso inline na seção "Dados da Parceria"

Os campos são `form.parceria.inicio_atividades` e `form.parceria.termino_atividades`
(`<input type="date">`, ~linhas 218 e 222 em `EntityCreateForm.vue`).

No `<script setup>`:
```ts
const datasVigenciaInvalidas = computed(() => {
  const ini = form.parceria.inicio_atividades
  const fim = form.parceria.termino_atividades
  return !!(ini && fim && ini > fim) // strings YYYY-MM-DD comparam corretamente lexicograficamente
})
```

No `<template>`, logo abaixo do par de campos de data, adicione:
```html
<p v-if="datasVigenciaInvalidas" style="color:#ef4444; font-size:13px; margin-top:4px">
  A data de início não pode ser posterior à data de término.
</p>
```

**Bloquear avanço/conclusão:**
- No `nextStep()`, quando estiver saindo do passo de parceria, adicione
  `if (datasVigenciaInvalidas.value) { /* foca e */ return }`.
- No `submitForm`, no início: `if (datasVigenciaInvalidas.value) { apiError.value = 'Corrija as datas de vigência.'; return }`.
- (Opcional) desabilitar o botão de concluir: `:disabled="isSubmitting || datasVigenciaInvalidas"`.

> Comparação de strings `YYYY-MM-DD` funciona porque o formato é ordenável. Se algum campo usar
> outro formato, converta para `Date` antes de comparar.

## 4.3 Frontend — replicar em `EntityForm.vue`

Mesma `computed` e mesmo bloqueio no submit do form de edição.

---

## 4.4 Critérios de aceite

- [ ] Início `10/10/2026` e término `01/01/2026` → aparece o aviso vermelho e o submit é bloqueado.
- [ ] Backend rejeita o mesmo caso mesmo se o front for burlado (teste via `curl`/Swagger).
- [ ] Datas válidas (início ≤ término) ou um dos campos vazio → sem erro.

## 4.5 Segurança / reversão

Aditivo. A regra só rejeita o caso logicamente impossível. Reverter = remover a `computed`, o
`<p>` e o `model_validator`.

> Próximo: `05-bloqueio-soma-parcelas.md`.
