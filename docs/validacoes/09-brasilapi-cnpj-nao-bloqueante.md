# Passo 09 — Dica complementar #2: auto-preenchimento via BrasilAPI (NÃO bloqueante)

> **Objetivo:** ao digitar um CNPJ válido, **opcionalmente** buscar dados públicos (razão social,
> endereço, situação cadastral, matriz/filial) para **pré-preencher** o formulário e reduzir erro
> de digitação.
>
> 🔵 **Requisito crítico do cliente (#2):** isto é **100% opcional**. Se a API estiver fora do ar,
> lenta, ou retornar erro, **o usuário cadastra normalmente**. A consulta **nunca** pode bloquear,
> travar ou impedir o cadastro.

**Depende de:** 01 (validar CNPJ), 08 (recomendado, para o conceito matriz/filial).
**Arquivos alterados:** `EntityCreateForm.vue` (e opcionalmente `EntityForm.vue`).
**Decisão de arquitetura:** chamar a BrasilAPI **direto do frontend** (ela suporta CORS). Assim, a
indisponibilidade dela nunca afeta o backend nem o fluxo de gravação.

---

## 9.1 Princípios de não-bloqueio (obrigatórios)

1. A consulta roda em `@blur` do CNPJ, **depois** que o usuário já pode seguir digitando.
2. Usa **timeout** curto (`AbortController`, ~4s). Estourou → aborta silenciosamente.
3. **Nunca** seta `errors.*` por falha de API. **Nunca** entra em `podeConcluir`/`nextStep`.
4. O pré-preenchimento é uma **sugestão**: idealmente o usuário confirma; campos preenchidos
   continuam editáveis.
5. Mostra apenas um status discreto (sucesso/indisponível), nunca um erro vermelho.

## 9.2 Frontend — função de consulta tolerante a falha

```ts
const statusBrasilApi = ref<'idle' | 'buscando' | 'ok' | 'indisponivel'>('idle')

const consultarBrasilApi = async () => {
  const d = apenasDigitos(form.cnpj)
  if (d.length !== 14 || !validarCNPJ(d)) return // só consulta CNPJ formalmente válido
  statusBrasilApi.value = 'buscando'

  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), 4000) // timeout de 4s

  try {
    const resp = await fetch(`https://brasilapi.com.br/api/cnpj/v1/${d}`, { signal: ctrl.signal })
    clearTimeout(timer)
    if (!resp.ok) { statusBrasilApi.value = 'indisponivel'; return } // 404/429/5xx → segue manual
    const dados = await resp.json()

    // Pré-preenche SOMENTE campos vazios (não sobrescreve o que o usuário já digitou).
    if (!form.razao_social && dados.razao_social) form.razao_social = dados.razao_social
    if (!form.configuracoes_extras.endereco && dados.logradouro) {
      form.configuracoes_extras.endereco =
        [dados.logradouro, dados.numero, dados.bairro, dados.municipio, dados.uf]
          .filter(Boolean).join(', ')
    }
    if (!form.configuracoes_extras.telefone && dados.ddd_telefone_1) {
      form.configuracoes_extras.telefone = String(dados.ddd_telefone_1)
    }
    // dados.descricao_identificador_matriz_filial: "1 - MATRIZ" / "2 - FILIAL" (apenas confirma o passo 08)
    statusBrasilApi.value = 'ok'
  } catch {
    clearTimeout(timer)
    statusBrasilApi.value = 'indisponivel' // abort/offline/erro → NUNCA bloqueia
  }
}
```

Dispare em `@blur` do CNPJ, **somada** às checagens já existentes:
```html
<input type="text" v-model="form.cnpj"
       @input="handleCnpjInput"
       @blur="verificarCnpj(); verificarGrupoRaiz(); consultarBrasilApi()" />
```

## 9.3 Frontend — status discreto (template)

```html
<span v-if="statusBrasilApi === 'buscando'" style="font-size:12px;color:#64748b">
  Consultando dados públicos…
</span>
<span v-else-if="statusBrasilApi === 'ok'" style="font-size:12px;color:#16a34a">
  ✓ Dados sugeridos automaticamente (confira e ajuste se necessário).
</span>
<span v-else-if="statusBrasilApi === 'indisponivel'" style="font-size:12px;color:#94a3b8">
  Consulta automática indisponível — preencha manualmente.
</span>
```

> Observe: o estado `'indisponivel'` usa cor neutra (cinza), **não** vermelho — não é erro do
> usuário, é só ausência de conveniência.

## 9.4 (Opcional) Confirmação antes de sobrescrever

Se quiser evitar surpreender o usuário, em vez de preencher direto, guarde `dados` em um `ref` e
mostre um botão "Usar dados encontrados" que aplica os valores. Mantém o controle com o usuário.

## 9.5 O que NÃO fazer

- ❌ Não criar dependência no backend que chame a BrasilAPI de forma síncrona no caminho de
  gravação.
- ❌ Não colocar `statusBrasilApi` em nenhuma condição de `:disabled`, `nextStep` ou `submitForm`.
- ❌ Não transformar timeout/erro em `apiError`/`errors.cnpj`.

---

## 9.6 Critérios de aceite

- [ ] CNPJ válido conhecido → razão social/endereço sugeridos; status verde.
- [ ] Desligar a internet / simular timeout → status cinza "indisponível" e **o cadastro conclui
      normalmente**.
- [ ] Campos já preenchidos pelo usuário **não** são sobrescritos.
- [ ] Nenhuma falha de API impede avançar de passo ou concluir.

## 9.7 Segurança / reversão

Isolado no front e tolerante a falhas. Reverter = remover `consultarBrasilApi`, o status e a
chamada no `@blur`.

> Próximo: `10-dicas-extras.md`.
