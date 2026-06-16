# Passo 07 — Requisito novo #1: resumo do representante na conclusão

> **Objetivo:** no **passo final** (tela de "Efetivar e concluir cadastro"), se o CPF informado já
> estiver vinculado a outros CNPJs, exibir um **painel informativo** com:
> 1. **quantas empresas** essa pessoa já tem cadastradas;
> 2. **o total já repassado** (somado) entre **todas** essas empresas.
>
> 🟡 **Apenas informação extra. NÃO impede nada** (não desabilita o botão, não bloqueia o submit).

**Depende de:** 02 (coluna CPF), 06 (endpoint `check-cpf`, que já devolve `total_empresas`,
`total_repassado` e `empresas`).
**Arquivos alterados:** `EntityCreateForm.vue` (e `EntityForm.vue` se quiser o mesmo painel na
edição).

---

## 7.1 Onde aparece

No **Passo 3** do wizard (financeiro/conclusão), acima do botão "Efetivar e concluir cadastro".
O painel é renderizado só quando houver dados (`resumoRepresentante.total_empresas > 0`).

## 7.2 Frontend — buscar o resumo ao entrar no passo final

Reutiliza o endpoint do passo 06. Buscar quando o usuário **chega ao passo 3** (e/ou quando o CPF
muda), com cache simples.

No `<script setup>`:
```ts
interface ResumoRepresentante {
  total_empresas: number
  total_repassado: number
  empresas: { entidade_id: string; razao_social: string; cnpj: string; total_repassado: number }[]
}

const resumoRepresentante = ref<ResumoRepresentante>({
  total_empresas: 0, total_repassado: 0, empresas: []
})

const carregarResumoRepresentante = async () => {
  const d = apenasDigitos(form.configuracoes_extras.cpf_representante)
  if (d.length !== 11) {
    resumoRepresentante.value = { total_empresas: 0, total_repassado: 0, empresas: [] }
    return
  }
  try {
    resumoRepresentante.value = await $fetch<ResumoRepresentante>(
      '/api/representantes/check-cpf', { params: { cpf: d /*, ignorar_id: id na edição */ } }
    )
  } catch {
    // Falha de rede não pode atrapalhar a conclusão: zera o resumo e segue.
    resumoRepresentante.value = { total_empresas: 0, total_repassado: 0, empresas: [] }
  }
}
```

Dispare quando o passo muda para 3. Já existe um `watch`/`nextStep` controlando `currentStep`.
Acrescente:
```ts
watch(currentStep, (novo) => {
  if (novo === 3) carregarResumoRepresentante()
})
```

Helper de moeda (se ainda não houver um reutilizável no componente):
```ts
const fmtBRL = (v: number) =>
  (v || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
```

## 7.3 Frontend — o painel (template), antes do botão concluir

```html
<div v-if="resumoRepresentante.total_empresas > 0"
     style="margin:12px 0; padding:12px 14px; border:1px solid #fde68a; background:#fffbeb; border-radius:8px;">
  <p style="font-weight:600; color:#92400e; margin:0 0 6px;">
    ℹ️ Informação sobre o representante
  </p>
  <p style="margin:0 0 4px; color:#78350f;">
    Esta pessoa (CPF {{ form.configuracoes_extras.cpf_representante }}) já é representante de
    <strong>{{ resumoRepresentante.total_empresas }}</strong> empresa(s).
  </p>
  <p style="margin:0 0 8px; color:#78350f;">
    Total já repassado entre todas:
    <strong>{{ fmtBRL(resumoRepresentante.total_repassado) }}</strong>.
  </p>
  <ul style="margin:0; padding-left:18px; color:#92400e; font-size:13px;">
    <li v-for="emp in resumoRepresentante.empresas" :key="emp.entidade_id">
      {{ emp.razao_social }} ({{ emp.cnpj || 's/ CNPJ' }}) — {{ fmtBRL(emp.total_repassado) }}
    </li>
  </ul>
  <p style="margin:8px 0 0; font-size:12px; color:#a16207;">
    Esta é apenas uma informação. Não impede a conclusão do cadastro.
  </p>
</div>
```

> **Decisão de cálculo:** o `total_repassado` vem do endpoint `check-cpf` (passo 06), definido como
> soma de `repasse_valor_final` das parcelas **efetivamente pagas** (com `repasse_data_pagamento`).
> Mantenha a mesma definição aqui para consistência entre o aviso inline e o painel final.

## 7.4 (Opcional) Mesmo painel na edição

Em `EntityForm.vue`, se houver passo de conclusão, replique chamando `check-cpf` com
`ignorar_id: formState.value.id` para não contar a própria entidade no total.

---

## 7.5 Critérios de aceite

- [ ] Cadastrar pessoa cujo CPF já representa 2 empresas → no passo final aparece "já é
      representante de **2** empresa(s)" e o **total somado** já repassado, com a lista por empresa.
- [ ] O botão "Efetivar e concluir" **permanece habilitado** (sujeito apenas às regras de bloqueio
      dos passos 03/04/05).
- [ ] Se o backend estiver fora do ar, o passo final abre normalmente, **sem** painel e **sem**
      travar a conclusão.
- [ ] CPF novo (sem vínculos) → painel não aparece.

## 7.6 Segurança / reversão

Puramente informativo e tolerante a falhas. Reverter = remover o `ref`, o `watch`, a função e o
bloco de template.

> Próximo: `08-matriz-filial.md`.
