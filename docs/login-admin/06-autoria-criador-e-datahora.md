# Passo 06 — Autoria: quem criou + data/hora na lista

> **Objetivo:** ao criar uma parceria, gravar **quem a criou**; na lista "Parcerias Cadastradas",
> mostrar o **nome do criador** e, ao **clicar nele**, exibir a **data e hora** da criação.

**Depende de:** 02 (usuário injetado) e 01 (coluna `criado_por`).
**Arquivos alterados:** `main.py` (INSERT + SELECT da listagem), `components/EntitySelector.vue`,
`composables/useEntity.ts`.

---

## 6.1 Backend — gravar o criador

No `create_entidade` (que no passo 02 passou a receber `usuario: dict = Depends(auth.get_current_user)`):

1. Acrescente a coluna no `INSERT INTO entidades (...)` e no `VALUES (...)`:
   ```
   ..., criado_por
   ..., :criado_por
   ```
2. No dicionário de binds:
   ```python
   "criado_por": usuario.get("nome") or usuario.get("sub"),
   ```

> (Opcional) Em `update_entidade`, grave `atualizado_por = :atualizado_por` com
> `usuario.get("nome")` para também rastrear a última edição.

## 6.2 Backend — devolver criador e data na listagem

No `get_entidades` (`GET /api/entidades`), inclua `created_at` e `criado_por` no SELECT e na resposta:

```python
query = text("""
    SELECT id, razao_social, cnpj, responsavel_nome, situacao, numero_emenda, valor,
           configuracoes_extras, created_at, criado_por
    FROM entidades ORDER BY razao_social ASC
""")
...
entidades.append({
    # ...campos atuais...
    "created_at": row.created_at.isoformat() if row.created_at else None,
    "criado_por": row.criado_por,
})
```

## 6.3 Frontend — interface `Entity`

Em `composables/useEntity.ts`, adicione ao `interface Entity`:
```ts
created_at?: string | null
criado_por?: string | null
```

## 6.4 Frontend — coluna "Criado por" com clique → data/hora

Em `components/EntitySelector.vue`:

**Cabeçalho** (adicione antes de "Ações"):
```html
<th>Criado por</th>
```

**Célula** (adicione na mesma posição, dentro do `<tr v-for=...>`):
```html
<td>
  <button v-if="entity.criado_por" class="btn btn-ghost btn-sm" style="padding:2px 8px"
          @click="alternarData(entity.id)">
    {{ entity.criado_por }}
  </button>
  <span v-else style="color:#94a3b8">—</span>
  <div v-if="mostrarDataId === entity.id" style="font-size:12px; color:#475569; margin-top:4px">
    🕒 Criado em {{ formatarDataHora(entity.created_at) }}
  </div>
</td>
```
> ⚠️ Lembre de ajustar o `colspan` da linha "Nenhum registro encontrado" (de 6 para 7).

**Script** (adicione):
```ts
const mostrarDataId = ref<string | null>(null)
function alternarData(id: string) {
  mostrarDataId.value = mostrarDataId.value === id ? null : id
}
function formatarDataHora(iso?: string | null) {
  if (!iso) return 'data não registrada'
  return new Date(iso).toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}
```

> Parcerias criadas **antes** deste recurso têm `criado_por = NULL` e mostram "—" (esperado).

---

## 6.5 Critérios de aceite

- [ ] Criar uma parceria logado como "Bruno" → a linha mostra "Bruno" na coluna "Criado por".
- [ ] Clicar no nome exibe "🕒 Criado em dd/mm/aaaa HH:MM"; clicar de novo oculta.
- [ ] Criar logado como outro usuário registra o nome correto.
- [ ] Parcerias antigas (sem autoria) mostram "—" sem quebrar a tabela.

## 6.6 Segurança / reversão

`criado_por` é um snapshot (sobrevive à exclusão do usuário). Reverter = remover a coluna na UI e os
campos do SELECT/INSERT.

> Próximo: `07-seguranca-sugestoes-e-aceite.md`.
