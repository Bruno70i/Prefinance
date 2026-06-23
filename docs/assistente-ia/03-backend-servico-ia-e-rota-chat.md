# Passo 03 — Backend: serviço de IA + rota `POST /api/chat`

> **Objetivo:** conectar o motor de contexto (passo 02) ao Ollama e expor `POST /api/chat` com
> **streaming** e **system prompt anti-alucinação**.
>
> No `main.py`, a única mudança é **registrar uma rota nova** (e um import). Nenhuma rota existente é
> alterada.

**Depende de:** 02.
**Arquivos novos:** `ollama_service.py`.
**Arquivos alterados:** `main.py` (1 import + 1 rota + 1 modelo Pydantic).

---

## 3.1 Serviço de IA — `ollama_service.py`

```python
# ollama_service.py
# Conversa com o Ollama (LLM local). Streaming de tokens. Tolerante a falha.
import os
from dotenv import load_dotenv
import ollama

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

_client = ollama.Client(host=OLLAMA_HOST)

SYSTEM_PROMPT = (
    "Você é o assistente virtual do PreFinance, um sistema de gestão de parcerias com o terceiro "
    "setor (OSC/ONG) da Secretaria de Saúde. Responda SEMPRE em português, de forma objetiva.\n\n"
    "REGRAS OBRIGATÓRIAS:\n"
    "1. Responda SOMENTE com base no CONTEXTO fornecido pelo sistema, que contém os dados reais "
    "cadastrados. \n"
    "2. Se a informação pedida NÃO estiver no contexto, diga claramente: 'Não encontrei esse dado "
    "nos cadastros.' Nunca invente.\n"
    "3. NUNCA invente valores, CNPJs, datas, nomes de pessoas ou de entidades.\n"
    "4. Ao citar um dado, mencione a entidade de origem (razão social e/ou CNPJ).\n"
    "5. Para perguntas de soma/contagem, use apenas os números do contexto (resumo geral).\n"
    "6. Seja conciso; use listas quando ajudar na clareza."
)


def montar_mensagens(pergunta: str, contexto: str, historico: list | None = None) -> list:
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    # histórico opcional (limitado às últimas trocas pelo chamador)
    for h in (historico or []):
        if h.get("role") in ("user", "assistant") and h.get("content"):
            msgs.append({"role": h["role"], "content": h["content"]})
    msgs.append({
        "role": "user",
        "content": f"CONTEXTO (dados reais do sistema):\n{contexto}\n\n---\nPERGUNTA: {pergunta}",
    })
    return msgs


def stream_resposta(pergunta: str, contexto: str, historico: list | None = None):
    """Gera tokens de texto (str) à medida que o modelo responde."""
    mensagens = montar_mensagens(pergunta, contexto, historico)
    for parte in _client.chat(model=OLLAMA_MODEL, messages=mensagens, stream=True):
        token = parte.get("message", {}).get("content", "")
        if token:
            yield token


def disponivel() -> bool:
    """Checa se o Ollama responde (para health-check tolerante)."""
    try:
        _client.list()
        return True
    except Exception:
        return False
```

## 3.2 Rota no `main.py`

No topo de `main.py`, junto dos outros imports de módulos locais (`import excel_modelo`,
`from validadores import ...`):
```python
import ia_contexto
import ollama_service
```

Adicione um modelo Pydantic (perto dos outros, ex.: após `EntidadeCreate`):
```python
class ChatRequest(BaseModel):
    pergunta: str = Field(..., min_length=1, description="Pergunta do usuário")
    historico: Optional[List[Dict[str, str]]] = Field(default_factory=list,
        description="Mensagens anteriores [{role:'user'|'assistant', content:'...'}]")
```

Adicione a rota (pode ficar perto das rotas de export):
```python
@app.post("/api/chat")
def chat(req: ChatRequest):
    """Responde perguntas sobre os cadastros, com contexto ancorado no banco. Streaming."""
    if not ollama_service.disponivel():
        raise HTTPException(
            status_code=503,
            detail="Assistente de IA indisponível: verifique se o Ollama está em execução."
        )
    # Limita o histórico às últimas 6 trocas para não inflar o prompt
    historico = (req.historico or [])[-6:]
    contexto = ia_contexto.montar_contexto(req.pergunta)

    def gerar():
        try:
            for token in ollama_service.stream_resposta(req.pergunta, contexto, historico):
                yield token
        except Exception as e:
            yield f"\n[Erro ao gerar resposta: {e}]"

    return StreamingResponse(gerar(), media_type="text/plain; charset=utf-8")
```

> `StreamingResponse` já é importado em `main.py` (usado nos exports). `Optional`, `List`, `Dict`,
> `Field`, `BaseModel`, `HTTPException` também já estão importados.

## 3.3 Teste da rota (sem frontend)

```bash
curl -N -X POST http://localhost:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"pergunta\":\"Quantas parcerias existem e qual o volume total?\"}"
```
(No PowerShell, use aspas adequadas.) A resposta deve **fluir** token a token e citar números do
banco.

---

## 3.4 Critérios de aceite

- [ ] Com o Ollama ligado, `POST /api/chat` responde em streaming.
- [ ] Pergunta sobre uma entidade específica retorna dados corretos (confira no banco).
- [ ] Pergunta sobre algo inexistente → o assistente responde "Não encontrei esse dado nos cadastros."
- [ ] Com o Ollama **desligado**, a rota retorna **503** com mensagem clara (e o resto do site segue
      funcionando).
- [ ] Nenhuma rota antiga deixou de funcionar.

## 3.5 Segurança / reversão

- A rota é **somente leitura** (via `ia_contexto`, que só faz SELECT).
- Reverter = remover a rota, o modelo `ChatRequest`, os 2 imports e apagar `ollama_service.py`.

> Próximo: `04-frontend-widget-chat.md`.
