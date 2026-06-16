# Passo 04 — Limpeza final e critérios de aceite

> **Objetivo:** remover o código que ficou órfão depois que a edição passou a usar o wizard, e
> validar o conjunto. Faça **só depois** que os passos 01–03 estiverem funcionando.

**Depende de:** 03.
**Arquivos alterados/removidos:** `components/EntityForm.vue` (remover), `pages/index.vue` (limpeza),
opcionalmente `main.py`.

---

## 4.1 Remover o formulário de edição antigo

O `components/EntityForm.vue` **não é mais usado** (a edição agora é o wizard). 

1. Em `pages/index.vue`, confirme que **não há** mais:
   - `import EntityForm from '~/components/EntityForm.vue'`
   - o `<EntityForm />` no template (modal já removido no passo 03)
   - referências a `isEditModalOpen`, `closeEditModal`, `selectEntity`/`selectedEntity` ligadas ao modal.
2. **Apague** o arquivo `components/EntityForm.vue`.

> Se preferir conservar como histórico, mova para `components/_legacy/EntityForm.vue.bak` em vez de
> apagar — mas garanta que **não** é mais importado.

## 4.2 Ajustar o composable (se necessário)

`composables/useEntity.ts` continua útil para `fetchEntities` e `deleteEntity`. As funções
`selectEntity`/`saveEntity`/`clearSelection`/`selectedEntity` eram usadas pelo `EntityForm` antigo:
- `EntitySelector.vue` ainda usa `entitiesList`, `fetchEntities`, `deleteEntity` → **manter**.
- Se `selectEntity`/`saveEntity`/`selectedEntity` ficarem sem nenhum uso, podem ser removidos. Faça
  uma busca por usos antes de remover; em caso de dúvida, **mantenha** (não atrapalha).

## 4.3 (Opcional) Limpezas no backend

- **Rota duplicada:** remover a segunda definição de `@app.get("/api/entidades")` (≈ linha 704),
  que é inalcançável.
- **Export geral:** se o botão foi removido (passo 03) e ninguém mais chama `/api/export/geral`,
  o endpoint pode ser removido. Não é obrigatório — deixá-lo não causa dano.

> Mudanças de backend aqui são **opcionais** e de higiene. Se houver qualquer incerteza, pule.

---

## 4.4 Checklist de aceite (fim a fim)

**Edição fiel ao cadastro**
- [ ] "Editar" abre o wizard com os **mesmos passos e labels** do cadastro: *Cadastro de
      Formalização · Dados da Parceria · Controle Financeiro*.
- [ ] Todos os campos vêm preenchidos: formalização (status, PA emenda, PA formalização, nº emenda,
      vereador, valor, justificativa, histórico…), parceria (ajuste, gestor, datas, categorias,
      especialidades, meta), financeiro (cód. SCIM, PA empenho, objeto e **cronograma de repasses**).
- [ ] Salvar grava nas tabelas reais (`entidades`, `dados_parceria`, `repasses_mensais`) e volta ao
      dashboard com a lista atualizada.
- [ ] O CNPJ da própria entidade não é acusado como duplicado em edição.

**Exportação por entidade**
- [ ] O botão "Exportar Geral" **não existe** mais no topo.
- [ ] Cada linha tem **Exportar**, que baixa a planilha **só daquela** empresa (3 abas no layout do
      `modelo/`).
- [ ] Exportar por etapa funciona **na criação** (rascunho) e **na edição** (persistido).

**Não-regressão**
- [ ] Criar nova parceria continua funcionando (bloqueio da soma de parcelas, datas, validações de
      CNPJ/CPF, BrasilAPI etc. intactos).
- [ ] Excluir continua funcionando.
- [ ] `GET /api/entidades/check-cnpj`, `check-cpf`, `por-raiz`, `check-razao` continuam respondendo
      (não foram capturados pela rota `/api/entidades/{id}`).

## 4.5 Teste manual sugerido

1. `uvicorn main:app --reload` + `npm run dev`.
2. Criar uma parceria nova com 1–2 repasses → conferir no dashboard.
3. Exportar pela linha → abrir o `.xlsx` e conferir as 3 abas no layout do modelo.
4. Editar a mesma entidade → conferir que todos os campos vêm preenchidos; alterar um valor de
   parcela e salvar; reabrir para confirmar a persistência.
5. Exportar etapa "Controle Financeiro" dentro da edição → conferir o cronograma.

---

## 4.6 Resumo do que mudou

| Antes | Depois |
|---|---|
| Editar abria `EntityForm.vue` (campos legados do JSONB) | Editar abre o **wizard** (campos reais, iguais ao cadastro) |
| "Exportar Geral" no topo | **Exportar por empresa** na linha da tabela |
| Edição não mostrava repasses | Edição mostra e edita o **cronograma** completo |
| Export só do rascunho ou geral | Export **por etapa** na criação e na edição + planilha completa por entidade |

> Fim do plano. Volte ao `00-INDICE-E-ORDEM.md` para a visão geral.
