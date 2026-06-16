# Passo 03 — Dashboard: editar via wizard, exportar por entidade

> **Objetivo:** religar o botão "Editar" para abrir o **wizard em modo edição** (passo 02);
> **remover** o botão "Exportar Geral"; e **adicionar** um botão "Exportar" **por linha** (por
> empresa) na tabela.

**Depende de:** 02.
**Arquivos alterados:** `pages/index.vue`, `components/EntitySelector.vue`.

---

## 3.1 `pages/index.vue` — religar Editar e remover Exportar Geral

### a) Estado de edição
No `<script setup>`, adicione um id de edição e ajuste a navegação:
```ts
const editId = ref<string | null>(null)

function novaParceria() {
  editId.value = null            // modo criar
  activeScreen.value = 'formalizacao'
}

function openEntity(id: string) {
  editId.value = id              // modo editar
  activeScreen.value = 'formalizacao'
}

function onSalvo() {
  editId.value = null
  activeScreen.value = 'dashboard'  // EntitySelector remonta e recarrega a lista (onMounted → fetchEntities)
}
```
> Pode remover `isEditModalOpen`, `selectEntity`, `selectedEntity` e o `watch` do modal — não serão
> mais usados (ver passo 04 para a limpeza completa).

### b) Render do wizard (criar **e** editar)
Onde hoje está:
```html
<EntityCreateForm :active-screen="activeScreen" @update-screen="setScreen" />
```
Troque por:
```html
<EntityCreateForm
  :active-screen="activeScreen"
  :modo="editId ? 'editar' : 'criar'"
  :entidade-id="editId"
  @update-screen="setScreen"
  @salvo="onSalvo"
/>
```

### c) Remover o botão "Exportar Geral"
No `top-bar`, **apague** este bloco (≈ linhas 46-48):
```html
<button class="btn btn-ghost btn-sm" @click="exportGeral()"> ... Exportar Geral (Excel) </button>
```
E remova a função `exportGeral()` (≈ linhas 131-138). (O endpoint `/api/export/geral` pode
permanecer no backend, inofensivo, ou ser removido no passo 04.)

### d) Remover o modal de edição
Apague o bloco do modal no `<template>` (≈ linhas 69-74) e o import/uso de `EntityForm`:
```html
<!-- Modal de Edição -->
<div v-if="isEditModalOpen" ...> <EntityForm /> </div>
```
(Detalhes e remoção do arquivo no passo 04.)

## 3.2 `components/EntitySelector.vue` — botão "Exportar" por linha

A coluna "Ações" hoje (≈ linhas 111-120) tem **Editar** e **Excluir**. Adicione **Exportar**:

```html
<td>
  <div style="display:flex; gap:8px">
    <button class="btn btn-ghost btn-sm" @click="$emit('edit-entity', entity.id)">
      Editar
    </button>
    <button class="btn btn-ghost btn-sm" @click="exportarEntidade(entity)">
      Exportar
    </button>
    <button class="btn btn-ghost btn-sm" style="color:#ef4444"
            @click="confirmDelete(entity.id, entity.razao_social)"
            :disabled="isDeletingId === entity.id">
      {{ isDeletingId === entity.id ? 'Excluindo...' : 'Excluir' }}
    </button>
  </div>
</td>
```

No `<script setup>`, adicione a função (exporta a planilha **completa** daquela entidade):
```ts
function exportarEntidade(entity: Entity) {
  const nome = (entity.razao_social || 'Entidade').replace(/ /g, '_')
  const link = document.createElement('a')
  link.href = `/api/export/entidade/${entity.id}?etapa=todos`
  link.download = `Prefinance_${nome}.xlsx`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
```

> O endpoint `GET /api/export/entidade/{id}?etapa=todos` já existe e gera as 3 abas no layout do
> modelo (ver `modelo/LAYOUT_EXPORT_EXCEL.md`). Cada empresa gera **sua própria** planilha — que é o
> objetivo (nada de exportação generalizada).

## 3.3 Exportação por etapa na edição (já vem do passo 02)

Como a edição agora usa o wizard, os botões "Exportar Etapa" de cada passo já existem. Garanta que,
**em modo edição**, eles exportem os dados **persistidos** (e não o rascunho). No `exportEtapa` do
`EntityCreateForm.vue`, ramifique por modo:

```ts
const exportEtapa = async (etapa: string) => {
  // Em edição: exporta o que está salvo no banco (GET por entidade)
  if (ehEdicao.value && props.entidadeId) {
    const link = document.createElement('a')
    link.href = `/api/export/entidade/${props.entidadeId}?etapa=${etapa}`
    link.download = `Prefinance_${(form.razao_social || 'Entidade').replace(/ /g, '_')}_${etapa}.xlsx`
    document.body.appendChild(link); link.click(); document.body.removeChild(link)
    return
  }
  // Em criação: exporta o rascunho atual (POST /api/export/dados) — comportamento já existente
  /* ...mantém o corpo atual da função... */
}
```

> Assim cobre os dois cenários pedidos: exportar **durante o preenchimento** (criação → rascunho) e
> **depois, na edição** (dados persistidos), ambos **por etapa**.

---

## 3.4 Critérios de aceite

- [ ] No dashboard, **não** existe mais o botão "Exportar Geral".
- [ ] Cada linha da tabela tem **Editar · Exportar · Excluir**.
- [ ] Clicar em **Exportar** numa linha baixa a planilha **só daquela** empresa (3 abas, layout
      modelo).
- [ ] Clicar em **Editar** abre o **wizard** com os campos reais preenchidos (mesmos labels do
      cadastro). Salvar persiste e volta ao dashboard com a lista atualizada.
- [ ] Dentro da edição, "Exportar Etapa" baixa a etapa correspondente com dados persistidos.
- [ ] Durante a criação, "Exportar Etapa" continua baixando o rascunho.

## 3.5 Segurança / reversão

Mudanças localizadas em 2 componentes. Reverter = restaurar o botão/funcão de Exportar Geral e o
modal. Recomenda-se fazer o passo 04 (limpeza) só após validar este.

> Próximo: `04-limpeza-e-criterios-de-aceite.md`.
