# Passo 08 — Ponto 5: Matriz x Filial dinâmico

> **Objetivo:** enquanto o usuário digita o CNPJ, identificar **dinamicamente** se é **Matriz** ou
> **Filial** e, no caso de filial, informar a qual **grupo (raiz)** pertence e se a matriz / outras
> filiais já estão cadastradas.
>
> Regra (diferença está só nos 4 dígitos após a barra):
> - **Matriz:** `0001` → `XX.XXX.XXX/0001-XX`
> - **Filial:** `0002`, `0003`, … (ordem sequencial de abertura)

**Depende de:** 01 (`parseCnpj`), 02 (`cnpj_raiz`/`cnpj_ordem`).
**Arquivos alterados:** `main.py` (endpoint `por-raiz`), `EntityCreateForm.vue`, `EntityForm.vue`.

---

## 8.1 Frontend — badge dinâmico (live, enquanto digita)

A UI já tem os pills "CNPJ Raiz" (~linha 154) e o card "Unidade Executora (Filial)" (~linha 175)
em `EntityCreateForm.vue`. Vamos alimentá-los.

No `<script setup>`:
```ts
import { parseCnpj } from '~/utils/validadores'

const cnpjPartes = computed(() => parseCnpj(form.cnpj))
// Ex.: { raiz, ordem, dv, tipo: 'MATRIZ'|'FILIAL'|'INDEFINIDO', numeroFilial }

const rotuloEstabelecimento = computed(() => {
  const p = cnpjPartes.value
  if (p.tipo === 'MATRIZ') return 'MATRIZ'
  if (p.tipo === 'FILIAL') return `FILIAL nº ${String(p.numeroFilial).padStart(4, '0')}`
  return '—'
})
```

No `<template>`, perto do campo CNPJ, mostre o badge:
```html
<span v-if="cnpjPartes.tipo !== 'INDEFINIDO'"
      :style="{ padding:'2px 8px', borderRadius:'12px', fontSize:'12px', fontWeight:600,
                color:'#fff', background: cnpjPartes.tipo === 'MATRIZ' ? '#0b5394' : '#0e7490' }">
  {{ rotuloEstabelecimento }}
</span>
<span v-if="cnpjPartes.raiz" style="font-size:12px; color:#64748b; margin-left:8px">
  Raiz do grupo: {{ cnpjPartes.raiz }}
</span>
```

## 8.2 Backend — listar estabelecimentos do mesmo grupo (raiz)

```python
@app.get("/api/entidades/por-raiz/{raiz}")
def entidades_por_raiz(raiz: str):
    """Lista todos os estabelecimentos (matriz + filiais) de uma mesma raiz de CNPJ."""
    if not engine:
        raise HTTPException(status_code=500, detail="Banco de dados não inicializado.")
    raiz_digitos = "".join(ch for ch in (raiz or "") if ch.isdigit())[:8]
    if len(raiz_digitos) != 8:
        return {"raiz": raiz_digitos, "estabelecimentos": []}
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT id, razao_social, cnpj, cnpj_ordem
            FROM entidades
            WHERE cnpj_raiz = :raiz
            ORDER BY cnpj_ordem
        """), {"raiz": raiz_digitos}).fetchall()
    return {
        "raiz": raiz_digitos,
        "estabelecimentos": [
            {
                "entidade_id": str(r.id),
                "razao_social": r.razao_social,
                "cnpj": r.cnpj,
                "ordem": r.cnpj_ordem,
                "tipo": "MATRIZ" if r.cnpj_ordem == "0001" else "FILIAL",
            } for r in rows
        ],
    }
```

## 8.3 Frontend — informar o grupo ao digitar uma filial

Quando `cnpjPartes.tipo === 'FILIAL'` e a raiz estiver completa (8 dígitos), consulte o grupo:
```ts
const grupoRaiz = ref<{ estabelecimentos: any[] }>({ estabelecimentos: [] })

const verificarGrupoRaiz = async () => {
  const p = cnpjPartes.value
  if (p.raiz.length !== 8) { grupoRaiz.value = { estabelecimentos: [] }; return }
  try {
    grupoRaiz.value = await $fetch(`/api/entidades/por-raiz/${p.raiz}`)
  } catch {
    grupoRaiz.value = { estabelecimentos: [] } // tolerante a falha
  }
}
```
Chame em `@blur` do CNPJ (junto com `verificarCnpj` do passo 03). Exiba, dentro do card
"Unidade Executora (Filial)":
```html
<div v-if="grupoRaiz.estabelecimentos.length" style="font-size:13px; color:#334155;">
  <p style="margin:0 0 4px; font-weight:600;">Grupo já cadastrado (raiz {{ cnpjPartes.raiz }}):</p>
  <ul style="margin:0; padding-left:18px;">
    <li v-for="est in grupoRaiz.estabelecimentos" :key="est.entidade_id">
      {{ est.tipo }} {{ est.ordem }} — {{ est.razao_social }} ({{ est.cnpj }})
    </li>
  </ul>
</div>
```

> **Comportamento 🟡 (não bloqueia):** detectar uma filial e mostrar o grupo é informativo.
> Lembre-se: cada estabelecimento tem CNPJ completo distinto, então **não** colide com a regra de
> unicidade do passo 03 (que é por 14 dígitos).
>
> **Melhoria opcional:** ao detectar que a matriz já existe, oferecer um botão "Herdar dados"
> que copia endereço/razão base da matriz para os campos atuais (apenas preenche; o usuário pode
> editar). Não implemente como obrigatório.

## 8.4 Persistência

`cnpj_raiz` e `cnpj_ordem` já são gravados pelo backend desde o passo 02 (derivados do CNPJ). Nada
extra a salvar aqui.

---

## 8.5 Critérios de aceite

- [ ] Digitar `.../0001-XX` → badge **MATRIZ** ao vivo; `.../0002-XX` → **FILIAL nº 0002**.
- [ ] Ao digitar uma filial cuja raiz já tem matriz cadastrada → lista do grupo aparece.
- [ ] Cadastrar matriz e filial da mesma raiz → ambas coexistem (sem erro de duplicidade).
- [ ] `GET /api/entidades/por-raiz/12345678` retorna os estabelecimentos ordenados por ordem.

## 8.6 Segurança / reversão

Badge é cálculo local; endpoint é leitura. Tolerante a falhas. Reverter = remover computeds, o
endpoint e os blocos de template.

> Próximo: `09-brasilapi-cnpj-nao-bloqueante.md`.
