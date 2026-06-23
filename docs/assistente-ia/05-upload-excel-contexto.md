# Passo 05 — (Opcional) Anexar Excel como contexto do chat

> **Objetivo:** permitir que o usuário **anexe um arquivo `.xlsx`** ao chat para a IA responder
> também sobre aquela planilha (além dos dados do banco). Atende ao pedido: "além de anexar os
> arquivos Excel para a IA ler".
>
> Recurso **opcional** e **isolado** — se não implementado, o chat do passo 04 continua funcionando
> normalmente.

**Depende de:** 03 (e 04 para a UI).
**Arquivos novos:** `ia_excel.py`.
**Arquivos alterados:** `main.py` (1 rota), `composables/useChat.ts`, `components/AssistenteIA.vue`.

---

## 5.1 Backend — leitor de Excel para texto (`ia_excel.py`)

Converte a planilha em um texto tabular compacto que cabe no contexto.

```python
# ia_excel.py
# Lê um .xlsx em memória e devolve um resumo textual compacto para o contexto do LLM.
import io
import pandas as pd

MAX_LINHAS_POR_ABA = 50  # evita estourar o contexto


def excel_para_texto(conteudo: bytes, limite_chars: int = 6000) -> str:
    try:
        xls = pd.ExcelFile(io.BytesIO(conteudo))
    except Exception as e:
        return f"[Não foi possível ler a planilha: {e}]"

    partes = []
    for nome in xls.sheet_names:
        df = xls.parse(nome)
        df = df.head(MAX_LINHAS_POR_ABA)
        partes.append(f"PLANILHA / ABA: {nome}\n{df.to_csv(index=False)}")
    texto = "\n\n".join(partes)
    if len(texto) > limite_chars:
        texto = texto[:limite_chars] + "\n[...planilha truncada...]"
    return "DADOS DA PLANILHA ANEXADA:\n" + texto
```

## 5.2 Backend — rota de upload + chat com anexo

Opção simples: uma rota que recebe o arquivo, devolve o texto extraído; o frontend guarda esse texto
e o envia junto da próxima pergunta. Acrescente ao `ChatRequest` um campo opcional e una ao contexto.

No `main.py`:
```python
from fastapi import UploadFile, File  # adicionar ao import do fastapi

@app.post("/api/chat/upload-excel")
async def chat_upload_excel(file: UploadFile = File(...)):
    import ia_excel
    conteudo = await file.read()
    return {"contexto_planilha": ia_excel.excel_para_texto(conteudo)}
```

Estenda o `ChatRequest` (passo 03) com um campo opcional:
```python
class ChatRequest(BaseModel):
    pergunta: str = Field(..., min_length=1)
    historico: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    contexto_planilha: Optional[str] = Field(default=None)  # texto vindo do upload
```

E na rota `/api/chat`, una o contexto do banco com o da planilha:
```python
contexto = ia_contexto.montar_contexto(req.pergunta)
if req.contexto_planilha:
    contexto = contexto + "\n\n" + req.contexto_planilha
```

## 5.3 Frontend — anexar no chat

No `useChat.ts`, guarde um `contextoPlanilha` e envie junto:
```ts
const contextoPlanilha = ref<string | null>(null)

const anexarExcel = async (file: File) => {
  const fd = new FormData()
  fd.append('file', file)
  const r = await fetch('/api/chat/upload-excel', { method: 'POST', body: fd })
  if (r.ok) {
    const data = await r.json()
    contextoPlanilha.value = data.contexto_planilha
  }
}
// no body do fetch de /api/chat, inclua: contexto_planilha: contextoPlanilha.value
// exponha anexarExcel e contextoPlanilha no return do composable
```

No `AssistenteIA.vue`, adicione um `<input type="file" accept=".xlsx" @change="...">` no rodapé do
painel e chame `anexarExcel(arquivo)`. Mostre um chip "📎 planilha anexada" quando houver contexto.

---

## 5.4 Critérios de aceite

- [ ] Anexar um `.xlsx` e perguntar sobre seu conteúdo → a IA responde com base na planilha.
- [ ] Sem anexo, o chat continua respondendo só com os dados do banco.
- [ ] Planilha grande é truncada (não estoura o modelo) e a IA avisa quando faltou dado.

## 5.5 Segurança / reversão

- O arquivo é lido **em memória** (não é salvo em disco).
- Reverter = remover a rota, o campo `contexto_planilha`, e os trechos do front; apagar `ia_excel.py`.

> Próximo: `06-seguranca-escala-e-aceite.md`.
