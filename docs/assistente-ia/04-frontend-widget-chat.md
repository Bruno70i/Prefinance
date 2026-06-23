# Passo 04 — Frontend: widget de chat do assistente

> **Objetivo:** adicionar um **botão flutuante** que abre um **painel de chat**, consumindo
> `POST /api/chat` com streaming. Isolado, montado no dashboard, sem afetar o resto da UI.

**Depende de:** 03.
**Arquivos novos:** `composables/useChat.ts`, `components/AssistenteIA.vue`.
**Arquivos alterados:** `pages/index.vue` (montar o componente).

---

## 4.1 Composable — `composables/useChat.ts`

Lê o stream da rota e vai concatenando os tokens na última mensagem.

```ts
// composables/useChat.ts
import { ref } from 'vue'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export const useChat = () => {
  const mensagens = ref<ChatMessage[]>([])
  const carregando = ref(false)
  const erro = ref<string | null>(null)

  const enviar = async (pergunta: string) => {
    const texto = pergunta.trim()
    if (!texto || carregando.value) return
    erro.value = null
    mensagens.value.push({ role: 'user', content: texto })

    // histórico (sem a pergunta atual) para dar memória curta ao modelo
    const historico = mensagens.value.slice(0, -1).slice(-6)

    // placeholder da resposta que será preenchido em streaming
    const idx = mensagens.value.push({ role: 'assistant', content: '' }) - 1
    carregando.value = true

    try {
      const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pergunta: texto, historico }),
      })
      if (resp.status === 503) {
        mensagens.value[idx].content = '⚠️ Assistente indisponível. Verifique se o Ollama está em execução.'
        return
      }
      if (!resp.ok || !resp.body) throw new Error('Falha na resposta do servidor')

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        mensagens.value[idx].content += decoder.decode(value, { stream: true })
      }
    } catch (e: any) {
      erro.value = e?.message || 'Erro ao falar com o assistente'
      mensagens.value[idx].content = '⚠️ Não foi possível obter a resposta.'
    } finally {
      carregando.value = false
    }
  }

  const limpar = () => { mensagens.value = []; erro.value = null }

  return { mensagens, carregando, erro, enviar, limpar }
}
```

## 4.2 Componente — `components/AssistenteIA.vue`

Botão flutuante (canto inferior direito) que abre o painel de chat.

```vue
<template>
  <div>
    <!-- Botão flutuante -->
    <button v-if="!aberto" class="ia-fab" @click="aberto = true" title="Assistente PreFinance">
      💬 Assistente
    </button>

    <!-- Painel -->
    <div v-if="aberto" class="ia-panel">
      <div class="ia-header">
        <strong>Assistente PreFinance</strong>
        <div>
          <button class="ia-link" @click="limpar">Limpar</button>
          <button class="ia-link" @click="aberto = false">✕</button>
        </div>
      </div>

      <div class="ia-body" ref="corpo">
        <p v-if="mensagens.length === 0" class="ia-hint">
          Pergunte qualquer coisa sobre os cadastros. Ex.: "Quanto já foi repassado à Casa de Luz?"
        </p>
        <div v-for="(m, i) in mensagens" :key="i" :class="['ia-msg', m.role]">
          <span class="ia-bubble" style="white-space: pre-wrap">{{ m.content }}</span>
        </div>
        <p v-if="carregando" class="ia-hint">Pensando…</p>
      </div>

      <form class="ia-input" @submit.prevent="onEnviar">
        <input v-model="texto" type="text" placeholder="Digite sua pergunta…" :disabled="carregando" />
        <button type="submit" :disabled="carregando || !texto.trim()">Enviar</button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChat } from '~/composables/useChat'

const aberto = ref(false)
const texto = ref('')
const corpo = ref<HTMLElement | null>(null)
const { mensagens, carregando, enviar, limpar } = useChat()

const onEnviar = async () => {
  const q = texto.value
  texto.value = ''
  await enviar(q)
}

// auto-scroll para a última mensagem
watch(mensagens, async () => {
  await nextTick()
  if (corpo.value) corpo.value.scrollTop = corpo.value.scrollHeight
}, { deep: true })
</script>

<style scoped>
.ia-fab { position: fixed; right: 24px; bottom: 24px; z-index: 1000;
  background: #0b5394; color: #fff; border: none; border-radius: 999px;
  padding: 12px 18px; font-weight: 600; cursor: pointer; box-shadow: 0 8px 20px rgba(0,0,0,.2); }
.ia-panel { position: fixed; right: 24px; bottom: 24px; z-index: 1000; width: 380px; max-width: 92vw;
  height: 560px; max-height: 80vh; background: #fff; border-radius: 14px; display: flex;
  flex-direction: column; box-shadow: 0 20px 40px rgba(0,0,0,.25); overflow: hidden; }
.ia-header { display: flex; justify-content: space-between; align-items: center;
  padding: 12px 14px; background: #0b5394; color: #fff; }
.ia-link { background: none; border: none; color: #cfe2f3; cursor: pointer; margin-left: 10px; }
.ia-body { flex: 1; overflow-y: auto; padding: 14px; background: #f8fafc; }
.ia-hint { color: #64748b; font-size: 13px; }
.ia-msg { display: flex; margin-bottom: 10px; }
.ia-msg.user { justify-content: flex-end; }
.ia-bubble { max-width: 85%; padding: 8px 12px; border-radius: 10px; font-size: 14px; line-height: 1.4; }
.ia-msg.user .ia-bubble { background: #0b5394; color: #fff; }
.ia-msg.assistant .ia-bubble { background: #e2e8f0; color: #1e293b; }
.ia-input { display: flex; gap: 8px; padding: 10px; border-top: 1px solid #e2e8f0; background: #fff; }
.ia-input input { flex: 1; padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 8px; }
.ia-input button { background: #0b5394; color: #fff; border: none; border-radius: 8px; padding: 8px 14px; cursor: pointer; }
.ia-input button:disabled { opacity: .5; cursor: not-allowed; }
</style>
```

## 4.3 Montar no dashboard — `pages/index.vue`

Importe e renderize o componente uma vez (fica flutuando em todas as telas). No `<template>`, antes
do fechamento do `<div>` raiz:
```html
<AssistenteIA />
```
Como o Nuxt 3 auto-importa componentes de `components/`, normalmente **não** é preciso importar
manualmente. Se o projeto usa imports explícitos, adicione:
```ts
import AssistenteIA from '~/components/AssistenteIA.vue'
```

---

## 4.4 Critérios de aceite

- [ ] Aparece o botão flutuante "💬 Assistente" no dashboard.
- [ ] Ao perguntar, a resposta **aparece em streaming** (token a token).
- [ ] Perguntar sobre uma entidade real traz dados corretos; perguntar algo inexistente traz "Não
      encontrei esse dado nos cadastros."
- [ ] Com o Ollama desligado, o painel mostra o aviso de indisponível e o resto do site funciona.
- [ ] Abrir/fechar/limpar o chat funciona; o auto-scroll acompanha as mensagens.

## 4.5 Segurança / reversão

Componente isolado. Reverter = remover `<AssistenteIA />` do `index.vue` e apagar os 2 arquivos novos.

> Próximo: `05-upload-excel-contexto.md` (opcional) ou `06-seguranca-escala-e-aceite.md`.
