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
  const contextoPlanilha = ref<string | null>(null)
  const nomePlanilhaAnexada = ref<string | null>(null)

  const anexarExcel = async (file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    carregando.value = true
    erro.value = null
    try {
      const r = await fetch('/api/chat/upload-excel', { method: 'POST', body: fd })
      if (!r.ok) throw new Error('Falha ao processar arquivo no servidor')
      const data = await r.json()
      contextoPlanilha.value = data.contexto_planilha
      nomePlanilhaAnexada.value = file.name
    } catch (e: any) {
      erro.value = e?.message || 'Erro ao anexar planilha'
      contextoPlanilha.value = null
      nomePlanilhaAnexada.value = null
    } finally {
      carregando.value = false
    }
  }

  const removerPlanilha = () => {
    contextoPlanilha.value = null
    nomePlanilhaAnexada.value = null
  }

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
        body: JSON.stringify({
          pergunta: texto,
          historico,
          contexto_planilha: contextoPlanilha.value
        }),
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

  const limpar = () => {
    mensagens.value = []
    erro.value = null
    contextoPlanilha.value = null
    nomePlanilhaAnexada.value = null
  }

  return { mensagens, carregando, erro, enviar, limpar, contextoPlanilha, nomePlanilhaAnexada, anexarExcel, removerPlanilha }
}
