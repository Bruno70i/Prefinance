# Passo 05 — Ponto 3: Soma das parcelas deve bater com o valor total

> **Objetivo:** o usuário **não pode** clicar em "Efetivar e concluir cadastro" enquanto a soma do
> cronograma de parcelas for diferente do **valor total** do repasse. 🔴 Bloqueia.
>
> Boa notícia: já existe o computed `somaCoincide` em `EntityCreateForm.vue` (~linha 655) que hoje
> só mostra um **aviso visual**. Este passo o transforma em **bloqueio** e adiciona a checagem no
> backend.

**Depende de:** nada.
**Arquivos alterados:** `EntityCreateForm.vue`, `EntityForm.vue`, `main.py`.

---

## 5.1 Frontend — transformar aviso em bloqueio

Estado atual relevante em `EntityCreateForm.vue`:
```ts
const somaParcelas = computed(() =>
  form.repasses.reduce((acc, r) => acc + (Number(r.repasse_parcela) || 0), 0)
)
const somaCoincide = computed(() => {
  if (!form.valor) return somaParcelas.value === 0
  return Math.abs(somaParcelas.value - form.valor) < 0.01
})
```

### a) Endurecer a condição de conclusão
Crie um computed específico que exige **valor definido**, **ao menos uma parcela** e soma batendo:
```ts
const podeConcluir = computed(() => {
  if (isSubmitting.value) return false
  if (!form.valor || form.valor <= 0) return false
  if (!form.repasses || form.repasses.length === 0) return false
  return somaCoincide.value && !datasVigenciaInvalidas.value // datas vêm do passo 04
})
```

### b) Desabilitar o botão concluir (~linha 378)
```html
<button type="submit" class="btn btn-success" :disabled="!podeConcluir">
  Efetivar e concluir cadastro
</button>
```

### c) Guard no `submitForm` (defesa redundante de UX)
No início de `submitForm`:
```ts
if (!form.valor || form.valor <= 0) {
  apiError.value = 'Informe o valor total do repasse antes de concluir.'
  return
}
if (!somaCoincide.value) {
  const dif = Math.abs(somaParcelas.value - (form.valor || 0))
  apiError.value = `A soma das parcelas (R$ ${somaParcelas.value.toFixed(2)}) difere do total ` +
    `(R$ ${(form.valor || 0).toFixed(2)}). Diferença de R$ ${dif.toFixed(2)}.`
  return
}
```

### d) Mensagem clara de bloqueio (template)
O aviso já existe (~linha 355). Garanta que ele apareça quando `!somaCoincide` e oriente:
```html
<p v-if="!somaCoincide" class="val-warn">
  A soma das parcelas precisa ser igual ao valor total para concluir o cadastro.
</p>
```

> **Tolerância:** mantenha `< 0.01` (1 centavo) para evitar falso negativo por arredondamento de
> ponto flutuante.

## 5.2 Backend — validação autoritária

Em `create_entidade` e `update_entidade`, depois de carregar `entidade.repasses` e antes de
persistir:

```python
if entidade.repasses:
    soma = sum(float(r.repasse_parcela or 0) for r in entidade.repasses)
    total = float(entidade.valor or 0)
    if total > 0 and abs(soma - total) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"A soma das parcelas ({soma:.2f}) difere do valor total ({total:.2f})."
        )
```

> **Decisão:** só valida quando `total > 0`. Rascunhos sem total definido não são bloqueados pelo
> backend (o bloqueio "tem que ter total" fica no front, no fluxo de conclusão). Se o produto
> exigir total sempre, troque a condição para `if total <= 0: raise ...`.

## 5.3 Frontend — replicar em `EntityForm.vue`

Reaproveite `somaParcelas`, `somaCoincide`, `podeConcluir` e o guard no submit da edição.

---

## 5.4 Critérios de aceite

- [ ] Total = R$ 1.200,00 com parcelas somando R$ 1.000,00 → botão "Efetivar" **desabilitado** e
      aviso visível.
- [ ] Ajustar as parcelas para somar exatamente R$ 1.200,00 → botão habilita e salva.
- [ ] Tentar burlar via API com soma divergente → backend retorna 400.
- [ ] Diferença de 1 centavo por arredondamento não bloqueia indevidamente.

## 5.5 Segurança / reversão

Aditivo/comportamental. Reverter = voltar o `:disabled` para `isSubmitting`, remover o guard e a
checagem do backend. Nenhum dado é alterado.

> Próximo: `06-cpf-vinculo-aviso-inline.md`.
