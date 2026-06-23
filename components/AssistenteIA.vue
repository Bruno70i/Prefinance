<template>
  <div>
    <!-- Botão flutuante -->
    <button v-if="!aberto" class="ia-fab" @click="aberto = true" title="Assistente PreFinance">
      💬 Assistente IA
    </button>

    <!-- Painel de Chat -->
    <div v-if="aberto" class="ia-panel">
      <div class="ia-header">
        <div class="ia-header-title">
          <span class="ia-header-icon">🤖</span>
          <strong>Assistente PreFinance</strong>
        </div>
        <div class="ia-header-actions">
          <button class="ia-btn-icon" @click="limpar" title="Limpar conversa">🧹</button>
          <button class="ia-btn-icon" @click="aberto = false" title="Fechar">✕</button>
        </div>
      </div>

      <!-- Corpo das mensagens -->
      <div class="ia-body" ref="corpo">
        <p v-if="mensagens.length === 0" class="ia-hint">
          Olá! Sou o assistente local do PreFinance. Você pode me perguntar sobre os cadastros salvos, como:
          <br /><br />
          <em>"Quantas parcerias existem?"</em><br />
          <em>"Qual o valor total das parcerias?"</em><br />
          <em>"Qual a vigência e gestor da entidade X?"</em>
          <br /><br />
          Ou anexe uma planilha abaixo para fazermos análises conjuntas.
        </p>
        
        <div v-for="(m, i) in mensagens" :key="i" :class="['ia-msg', m.role]">
          <div class="ia-bubble">
            <span style="white-space: pre-wrap">{{ m.content }}</span>
          </div>
        </div>

        <p v-if="carregando" class="ia-hint loading-pulse">Pensando e consultando a base de dados…</p>
        <p v-if="erro" class="ia-error">⚠️ {{ erro }}</p>
      </div>

      <!-- Rodapé com chips de anexos e entrada -->
      <div class="ia-footer">
        <!-- Chip de planilha anexada -->
        <div v-if="nomePlanilhaAnexada" class="ia-attachment-chip">
          <span class="ia-attachment-text" :title="nomePlanilhaAnexada">📎 {{ nomePlanilhaAnexada }}</span>
          <button type="button" class="ia-attachment-remove" @click="removerPlanilha">×</button>
        </div>

        <!-- Form de envio -->
        <form class="ia-input-area" @submit.prevent="onEnviar">
          <!-- Botão de anexo de arquivo oculto -->
          <label class="ia-btn-attach" title="Anexar planilha Excel (.xlsx)">
            📎
            <input type="file" accept=".xlsx" @change="onFileChange" style="display: none" :disabled="carregando" />
          </label>

          <input 
            v-model="texto" 
            type="text" 
            placeholder="Digite sua pergunta…" 
            :disabled="carregando"
            class="ia-input-field"
          />
          <button type="submit" class="ia-btn-send" :disabled="carregando || (!texto.trim() && !nomePlanilhaAnexada)">
            Enviar
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChat } from '~/composables/useChat'

const aberto = ref(false)
const texto = ref('')
const corpo = ref<HTMLElement | null>(null)

const { 
  mensagens, 
  carregando, 
  erro, 
  enviar, 
  limpar, 
  nomePlanilhaAnexada, 
  anexarExcel, 
  removerPlanilha 
} = useChat()

const onEnviar = async () => {
  const q = texto.value
  texto.value = ''
  await enviar(q)
}

const onFileChange = async (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    await anexarExcel(target.files[0])
    // limpa o input para permitir selecionar o mesmo arquivo novamente
    target.value = ''
  }
}

// auto-scroll para acompanhar o streaming
watch(mensagens, async () => {
  await nextTick()
  if (corpo.value) {
    corpo.value.scrollTop = corpo.value.scrollHeight
  }
}, { deep: true })
</script>

<style scoped>
.ia-fab {
  position: fixed;
  right: 24px;
  bottom: 85px;
  z-index: 1000;
  background: linear-gradient(135deg, #0b5394, #073763);
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 14px 22px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 8px 25px rgba(11, 83, 148, 0.4);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.ia-fab:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(11, 83, 148, 0.5);
  background: linear-gradient(135deg, #0d6efd, #0b5394);
}

.ia-panel {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 1000;
  width: 400px;
  max-width: 92vw;
  height: 580px;
  max-height: 82vh;
  background: #ffffff;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.08);
  font-family: system-ui, -apple-system, sans-serif;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.ia-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: linear-gradient(135deg, #0b5394, #073763);
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.ia-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ia-header-icon {
  font-size: 18px;
}

.ia-header-actions {
  display: flex;
  gap: 12px;
}

.ia-btn-icon {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.85);
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.ia-btn-icon:hover {
  background-color: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.ia-body {
  flex: 1;
  overflow-y: auto;
  padding: 18px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ia-hint {
  color: #64748b;
  font-size: 13.5px;
  line-height: 1.5;
  background: #f1f5f9;
  padding: 12px 14px;
  border-radius: 10px;
  margin: 0;
  border-left: 3px solid #cbd5e1;
}

.ia-error {
  color: #ef4444;
  font-size: 13px;
  background: #fef2f2;
  padding: 10px;
  border-radius: 8px;
  margin: 0;
}

.loading-pulse {
  animation: pulse 1.5s infinite ease-in-out;
  background: #f0f7ff;
  border-left-color: #3b82f6;
  color: #1d4ed8;
}

@keyframes pulse {
  0%, 100% { opacity: 0.8; }
  50% { opacity: 0.5; }
}

.ia-msg {
  display: flex;
  width: 100%;
}

.ia-msg.user {
  justify-content: flex-end;
}

.ia-msg.assistant {
  justify-content: flex-start;
}

.ia-bubble {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.45;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.ia-msg.user .ia-bubble {
  background: #0b5394;
  color: #ffffff;
  border-bottom-right-radius: 2px;
}

.ia-msg.assistant .ia-bubble {
  background: #ffffff;
  color: #1e293b;
  border-bottom-left-radius: 2px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.ia-footer {
  border-top: 1px solid #e2e8f0;
  background: #ffffff;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ia-attachment-chip {
  align-self: flex-start;
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f1f5f9;
  color: #475569;
  padding: 4px 10px;
  border-radius: 99px;
  font-size: 12px;
  border: 1px solid #e2e8f0;
  max-width: 100%;
}

.ia-attachment-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ia-attachment-remove {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  padding: 0 2px;
}

.ia-attachment-remove:hover {
  color: #ef4444;
}

.ia-input-area {
  display: flex;
  gap: 10px;
  align-items: center;
}

.ia-btn-attach {
  font-size: 18px;
  cursor: pointer;
  color: #64748b;
  padding: 6px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  width: 38px;
  height: 38px;
}

.ia-btn-attach:hover {
  background: #f1f5f9;
  color: #0b5394;
  border-color: #cbd5e1;
}

.ia-input-field {
  flex: 1;
  padding: 8px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  height: 38px;
  box-sizing: border-box;
}

.ia-input-field:focus {
  border-color: #0b5394;
}

.ia-btn-send {
  background: #0b5394;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  height: 38px;
}

.ia-btn-send:hover {
  background: #073763;
}

.ia-btn-send:disabled {
  background: #cbd5e1;
  color: #94a3b8;
  cursor: not-allowed;
}
</style>
