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
