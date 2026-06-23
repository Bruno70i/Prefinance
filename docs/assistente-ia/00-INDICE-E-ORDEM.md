# Plano — Assistente de IA com acesso a todos os cadastros do PreFinance

> **Objetivo:** adicionar um **assistente de IA (chat)** ao PreFinance que tenha **contexto de todos
> os dados cadastrados** (entidades, parcerias e repasses no PostgreSQL) e, opcionalmente, de
> planilhas Excel anexadas — de modo que o usuário possa **perguntar qualquer coisa sobre qualquer
> cadastro salvo**.
>
> **Para quem vai implementar (IA/dev):** leia este índice inteiro antes de começar. Os passos são
> **incrementais e isolados** — na ordem abaixo, o site atual **continua funcionando** o tempo todo.
> Todo o código de IA é **adicionado em arquivos novos**; o `main.py` só ganha o registro de **uma
> rota nova**.

---

## 0. Princípio anti-alucinação (a regra mais importante)

O LLM **não** deve "saber" os dados de cor nem inventar SQL. Em vez disso:

1. **O Python busca os fatos no PostgreSQL** (determinístico) e monta um **CONTEXTO** textual com os
   registros reais.
2. **O LLM recebe pergunta + CONTEXTO** e responde **somente com base no contexto**.
3. **System prompt rígido:** "se não estiver no contexto, diga que não encontrou; nunca invente
   valores, CNPJs, datas ou nomes; cite a entidade de origem de cada dado."

Assim, os números vêm sempre do banco, não da imaginação do modelo. Isso é o que torna o sistema
**robusto e confiável**.

---

## 1. Arquitetura escolhida (adaptada ao projeto REAL)

> ⚠️ Os documentos de referência (`docs/Sistema de IA/*.md`) descrevem o "PlanIA" com pastas
> `backend/app/services/` e `frontend/`. **O PreFinance NÃO tem essa estrutura.** Ele é **flat**:
> `main.py`, `validadores.py`, `excel_modelo.py` na raiz; `components/`, `composables/`, `pages/`.
> **Siga a estrutura real abaixo**, não a do PlanIA.

- **LLM local via Ollama (Llama 3)** — roda na máquina, **privacidade total**, sem API externa
  (alinhado aos documentos de referência). Modelo e host configuráveis por `.env`.
- **Motor de contexto** (`ia_contexto.py`): lê PostgreSQL e monta o contexto ancorado.
- **Serviço de IA** (`ollama_service.py`): conversa com o Ollama, com streaming.
- **Rota** `POST /api/chat` em `main.py`: recebe pergunta + histórico, chama o motor de contexto e o
  serviço de IA, devolve a resposta (streaming).
- **Frontend**: `composables/useChat.ts` + `components/AssistenteIA.vue` (botão flutuante + painel de
  chat), montado em `pages/index.vue`.
- **(Opcional) Excel como contexto**: upload de `.xlsx` que vira texto e entra no contexto.
- **(Opcional, Fase 2) Busca semântica**: embeddings para escalar a milhares de cadastros.

### Tabelas que o assistente vai ler (somente leitura)
- `entidades` (formalização + dados cadastrais)
- `dados_parceria` (1:1 — ajuste, vigência, gestor, metas, especialidades)
- `repasses_mensais` (1:N — parcelas, vencimentos, prestação de contas)

---

## 2. Ordem de execução (obrigatória)

| # | Arquivo | Entrega | Depende de |
|---|---|---|---|
| 01 | `01-preparacao-ollama-e-deps.md` | Instalar Ollama, baixar o modelo, criar `requirements.txt`, configurar `.env`. **Nada no app muda.** | — |
| 02 | `02-backend-motor-de-contexto.md` | `ia_contexto.py`: lê o banco e monta o CONTEXTO ancorado (roster + agregados + detalhe das entidades citadas). Testável isolado. | 01 |
| 03 | `03-backend-servico-ia-e-rota-chat.md` | `ollama_service.py` + `POST /api/chat` (streaming) com system prompt anti-alucinação. | 02 |
| 04 | `04-frontend-widget-chat.md` | `useChat.ts` + `AssistenteIA.vue` (botão flutuante + painel) montado no dashboard. | 03 |
| 05 | `05-upload-excel-contexto.md` | (Opcional) Anexar `.xlsx` ao chat como contexto extra. | 03 |
| 06 | `06-seguranca-escala-e-aceite.md` | Guardrails, Fase 2 (busca semântica para escala) e checklist de aceite fim a fim. | 04 |

**Garantia de não quebrar:** após 01, só o ambiente muda. Após 02, existe um módulo novo sem uso na
UI. Após 03, a rota `/api/chat` responde mas a UI ainda não a usa. Após 04, o chat aparece. 05 e 06
são incrementos opcionais/finais.

---

## 3. Convenções

- **Somente leitura:** o assistente **nunca** escreve/edita/exclui dados. Sem `INSERT/UPDATE/DELETE`,
  sem SQL gerado por LLM.
- **Novos módulos Python na raiz** (ao lado de `main.py`), seguindo o padrão de `validadores.py` e
  `excel_modelo.py`.
- **Conexão ao banco:** cada serviço cria seu próprio `engine` a partir das variáveis de ambiente
  (mesmo padrão de `clear_db.py`), para **evitar import circular** com `main.py`.
- **Idioma:** todas as respostas do assistente em **português**.
- **Tolerância a falha:** se o Ollama estiver offline, a rota responde um erro claro e o site
  continua funcionando normalmente (o chat é um recurso adicional, não bloqueia nada).

Prossiga para `01-preparacao-ollama-e-deps.md`.
