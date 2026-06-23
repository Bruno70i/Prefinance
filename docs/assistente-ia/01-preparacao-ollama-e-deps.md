# Passo 01 — Preparação: Ollama, modelo e dependências

> **Objetivo:** deixar o ambiente pronto (LLM local rodando + dependências Python) **sem alterar
> nada do site**. Ao fim deste passo, `ollama` responde no terminal e o projeto tem um
> `requirements.txt`.

**Depende de:** nada.
**Arquivos novos:** `requirements.txt`.
**Arquivos alterados:** `.env` (acrescentar 3 variáveis).

---

## 1.1 Instalar o Ollama e baixar o modelo

1. Instalar o Ollama (Windows): baixar em https://ollama.com/download e instalar. Ele sobe um
   serviço local em `http://localhost:11434`.
2. Baixar um modelo Llama 3 (recomendado o 3.1 8B, melhor em seguir instruções):

```bash
ollama pull llama3.1:8b
```

> Alternativas: `llama3:8b` (mais leve) ou `llama3.1:8b-instruct-q4_K_M` (quantizado, menos RAM).
> Em máquina modesta, `llama3.2:3b` funciona com qualidade menor. O modelo é **configurável** por
> `.env` (abaixo), então não fixe no código.

3. Testar:
```bash
ollama run llama3.1:8b "responda apenas: ok"
```

## 1.2 Dependências Python

Não há `requirements.txt` no projeto. Crie um na raiz consolidando o que já é usado + o cliente do
Ollama:

```txt
# requirements.txt
fastapi
uvicorn[standard]
pandas
openpyxl
sqlalchemy
psycopg2-binary
python-dotenv
ollama
```

Instale no venv do projeto:
```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

> Usaremos o **pacote oficial `ollama`** (API simples `ollama.chat(...)`, com suporte a streaming).
> Já confirmado que `fastapi`, `pandas`, `openpyxl`, `sqlalchemy`, `psycopg2` estão instalados; só
> `ollama` falta.

## 1.3 Variáveis de ambiente (`.env`)

Acrescente ao `.env` (não remova as variáveis de banco existentes):

```env
# --- Assistente de IA ---
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
IA_MAX_CONTEXT_CHARS=12000
```

- `OLLAMA_HOST`: onde o Ollama escuta.
- `OLLAMA_MODEL`: modelo usado (troque sem mexer no código).
- `IA_MAX_CONTEXT_CHARS`: orçamento de tamanho do contexto injetado (proteção contra prompts gigantes).

## 1.4 Verificação rápida do cliente Python

```bash
.venv/Scripts/python.exe -c "import ollama; print(ollama.chat(model='llama3.1:8b', messages=[{'role':'user','content':'diga ok'}])['message']['content'])"
```
Deve imprimir algo como `ok`.

---

## 1.5 Critérios de aceite

- [ ] `ollama run llama3.1:8b "ok"` responde no terminal.
- [ ] `requirements.txt` existe e `pip install -r requirements.txt` roda sem erro no venv.
- [ ] O snippet do item 1.4 retorna texto do modelo.
- [ ] O site (backend + frontend) continua subindo normalmente — nada do app foi tocado.

## 1.6 Segurança / reversão

Apenas ambiente. Reverter = desinstalar o pacote `ollama` e remover as 3 variáveis do `.env`.

> Próximo: `02-backend-motor-de-contexto.md`.
