# Passo 06 — Segurança, escala (Fase 2) e critérios de aceite finais

> **Objetivo:** consolidar as proteções, descrever a evolução para muitos cadastros (busca
> semântica) e dar o checklist final de validação fim a fim.

**Depende de:** 04 (e 05, se feito).

---

## 6.1 Segurança e guardrails

1. **Somente leitura, sempre.** Todo acesso a banco passa por `ia_contexto.py`, que só faz `SELECT`.
   **Nunca** dê ao LLM a capacidade de gerar/rodar SQL, nem rotas de escrita.
2. **Sem injeção de SQL.** As consultas usam parâmetros bind (`:id`, `:cpf`...). A pergunta do
   usuário **nunca** é concatenada em SQL — ela só entra no texto do prompt e nos filtros Python.
3. **Anti-alucinação reforçada.** O system prompt (passo 03) exige resposta só pelo contexto. Reforce
   periodicamente revisando respostas; se o modelo "viajar", reduza `temperature` (adicione
   `options={"temperature": 0.1}` na chamada `_client.chat`).
4. **Privacidade.** O LLM é **local** (Ollama); nenhum dado sai da máquina. Mantenha assim se os
   dados forem sensíveis (CPF, CNPJ, valores).
5. **Limite de tamanho.** `IA_MAX_CONTEXT_CHARS` evita prompts gigantes. O histórico é limitado às
   últimas 6 trocas (passo 03).
6. **(Opcional) Controle de acesso.** Se o site tiver login no futuro, restrinja `/api/chat` a
   usuários autenticados. Hoje o sistema é interno (gestora de contratos).
7. **Tolerância a falha.** Ollama offline → 503 com mensagem clara; o site segue funcionando.

## 6.2 Escala — Fase 2: busca semântica (opcional, para muitos cadastros)

O passo 02 injeta o **roster de todas as entidades** (1 linha cada) + detalhe das citadas. Isso
funciona muito bem para dezenas/centenas de registros. Quando passar de ~alguns milhares, o roster
fica grande demais. Aí evolua a seleção de contexto:

1. **Gerar embeddings** de cada entidade (texto = razão social + objeto + parceria) com um modelo de
   embedding do Ollama:
   ```python
   # exemplo: ollama.embeddings(model="nomic-embed-text", prompt=texto)["embedding"]
   ```
   (Baixar com `ollama pull nomic-embed-text`.)
2. **Armazenar os vetores**:
   - Opção A: extensão **pgvector** no PostgreSQL (coluna `vetor vector(768)` + índice ivfflat).
   - Opção B (mais simples): cache em arquivo (`.pkl`/JSON) recalculado quando os dados mudam.
3. **Na pergunta**: gerar o embedding da pergunta, buscar as N entidades mais similares (cosine) e
   injetar **somente o detalhe delas** no contexto, em vez do roster inteiro.
4. **Invalidação**: recalcular o embedding de uma entidade quando ela for criada/editada (gancho no
   `create_entidade`/`update_entidade`).

> Mantenha a Fase 2 **opcional**: só implemente quando o volume justificar. Para o estado atual
> (poucas dezenas de parcerias), o passo 02 basta e é mais simples/robusto.

## 6.3 Ajustes finos recomendados

- **`temperature` baixa** (0.1–0.2) para respostas mais factuais.
- **Modelo**: se as respostas estiverem fracas, teste `llama3.1:8b` → bom equilíbrio. Para hardware
  forte, `llama3.1:70b` melhora bastante (mais lento). Tudo via `OLLAMA_MODEL` no `.env`.
- **Formatação**: se quiser respostas em Markdown renderizado no chat, troque o `white-space:
  pre-wrap` por um render de Markdown (ex.: lib leve) — opcional/cosmético.

---

## 6.4 Checklist de aceite (fim a fim)

**Funcional**
- [ ] Botão flutuante abre o chat no dashboard.
- [ ] "Quantas parcerias existem e qual o volume total?" → números corretos do banco.
- [ ] "Quanto já foi repassado à {entidade}?" → valor correto, citando a entidade.
- [ ] "Qual o gestor e a vigência da {entidade}?" → dados corretos da parceria.
- [ ] Pergunta sobre algo inexistente → "Não encontrei esse dado nos cadastros." (não inventa).
- [ ] (Se passo 05) Anexar `.xlsx` e perguntar sobre ele → responde pela planilha.

**Robustez / não-regressão**
- [ ] Respostas em **streaming** (token a token).
- [ ] Ollama desligado → 503 amigável; **todo o resto do site funciona** (dashboard, cadastro,
      edição, exportação).
- [ ] Nenhuma rota antiga foi alterada/quebrada.
- [ ] O assistente **nunca** escreve no banco (auditável: só há `SELECT` em `ia_contexto.py`).

**Confiabilidade dos dados**
- [ ] Conferir 3 respostas contra o banco (psql) — valores idênticos.
- [ ] Forçar uma pergunta capciosa (dado que não existe) e confirmar que o modelo recusa em vez de
      inventar.

---

## 6.5 Resumo dos artefatos criados

| Arquivo | Papel |
|---|---|
| `requirements.txt` | Dependências do backend (inclui `ollama`) |
| `ia_contexto.py` | Lê o PostgreSQL e monta o contexto ancorado (somente leitura) |
| `ollama_service.py` | Conversa com o LLM local (streaming, system prompt anti-alucinação) |
| `ia_excel.py` (opcional) | Converte planilha anexada em texto de contexto |
| `composables/useChat.ts` | Estado do chat + leitura do streaming |
| `components/AssistenteIA.vue` | Botão flutuante + painel de chat |
| `main.py` (alterado) | +2 imports, +`ChatRequest`, +rota `/api/chat` (e upload opcional) |
| `pages/index.vue` (alterado) | Monta `<AssistenteIA />` |

> Fim do plano. Volte ao `00-INDICE-E-ORDEM.md` para a visão geral.
