# Passo 01 — Backend: parser da Formalização + rota de import

> **Objetivo:** criar `import_planilha.py` (lê `.xlsx`/`.csv` e extrai os campos da **Formalização**)
> e a rota `POST /api/import/planilha`, que recebe o arquivo e devolve um JSON para o frontend
> preencher o formulário. **Não grava no banco.**

**Depende de:** nada.
**Arquivos novos:** `import_planilha.py`.
**Arquivos alterados:** `main.py` (1 import + 1 rota).

---

## 1.1 Parser — `import_planilha.py`

```python
# import_planilha.py
# Lê uma planilha (.xlsx) ou CSV e extrai campos do cadastro. SOMENTE LEITURA (não grava no banco).
# É o inverso de excel_modelo.py. Veja modelo/LAYOUT_EXPORT_EXCEL.md para o mapa das células.
import io
import re
import csv
import unicodedata
import openpyxl


def _norm(s) -> str:
    """Normaliza cabeçalho: maiúsculas, sem acento, sem pontuação extra, espaços colapsados."""
    if s is None:
        return ""
    t = str(s).strip()
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    t = re.sub(r"\s+", " ", t).upper().strip(" .:?")
    return t


# Cabeçalho normalizado -> campo do formulário (aceita os nomes do modelo E rótulos amigáveis)
MAPA_FORMALIZACAO = {
    "STATUS": "situacao",
    "STATUS DA ANALISE": "situacao",
    "TIPO DE INSTRUMENTO": "situacao",
    "HISTORICO": "historico",
    "HISTORICO DE MOVIMENTACOES": "historico",
    "NOME": "razao_social",
    "RAZAO SOCIAL": "razao_social",
    "RAZAO SOCIAL / NOME DA ENTIDADE": "razao_social",
    "ENTIDADE": "razao_social",
    "CNPJ": "cnpj",
    "CNPJ RAIZ": "cnpj",
    "PA EMENDA": "pa_emenda",
    "LOCALIZACAO DO PA EMENDA": "localizacao_pa_emenda",
    "EMENDA ALTERADA": "emenda_alterada",
    "PA FORMALIZACAO": "pa_formalizacao",
    "N": "numero_emenda",
    "NO": "numero_emenda",
    "NUMERO DA EMENDA": "numero_emenda",
    "NUMERO": "numero_emenda",
    "VEREADOR": "vereador",
    "VEREADOR PROPONENTE": "vereador",
    "JUSTIFICATIVA": "justificativa",
    "VALOR": "valor",
    "VALOR (R$)": "valor",
    "VALOR DESTINADO (R$)": "valor",
    "VALOR DESTINADO": "valor",
}

CAMPOS_VALOR = {"valor"}  # campos que devem virar número


def _parse_valor(v):
    """'R$ 20.000,00' / '20000.5' / 20000 -> 20000.0 (ou None)."""
    if v is None or str(v).strip() == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = re.sub(r"[^\d,.\-]", "", str(v))
    if "," in s:  # formato BR: ponto = milhar, vírgula = decimal
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _achar_aba(wb, *chaves):
    """Acha a aba cujo nome normalizado contém alguma das chaves (ex.: 'FORMALIZ')."""
    for ws in wb.worksheets:
        n = _norm(ws.title)
        if any(c in n for c in chaves):
            return ws
    return None


def _linha_valores(ws, linha):
    return [c.value for c in ws[linha]]


def _mapear(headers, valores, mapa):
    """Casa cabeçalhos -> campos. Retorna dict {campo: valor_coerido}."""
    out = {}
    for h, v in zip(headers, valores):
        campo = mapa.get(_norm(h))
        if not campo:
            continue
        if v is None or str(v).strip() == "":
            continue
        out[campo] = _parse_valor(v) if campo in CAMPOS_VALOR else str(v).strip()
    return out


def parse_formalizacao_xlsx(conteudo: bytes) -> dict:
    """Lê a aba FORMALIZAÇÃO (cabeçalho linha 2, dados linha 3+) e retorna a 1ª entidade."""
    wb = openpyxl.load_workbook(io.BytesIO(conteudo), data_only=True)
    ws = _achar_aba(wb, "FORMALIZ") or wb.worksheets[0]
    headers = _linha_valores(ws, 2)
    avisos = []

    # quantas linhas de dados existem (a partir da linha 3)
    linhas_dados = [r for r in range(3, ws.max_row + 1)
                    if any(c.value not in (None, "") for c in ws[r])]
    if not linhas_dados:
        return {"formalizacao": {}, "avisos": ["A aba de Formalização não tem linhas de dados."]}

    primeira = _mapear(headers, _linha_valores(ws, linhas_dados[0]), MAPA_FORMALIZACAO)
    if len(linhas_dados) > 1:
        nome = primeira.get("razao_social", "a primeira")
        avisos.append(f"O arquivo contém {len(linhas_dados)} entidades; importada {nome}.")
    return {"formalizacao": primeira, "avisos": avisos}


def _ler_csv(conteudo: bytes) -> dict:
    """
    CSV em 2 formatos:
    (a) horizontal: 1ª linha = cabeçalhos, 2ª linha = valores;
    (b) vertical: 2 colunas 'Campo;Valor'.
    Detecta delimitador (',' ou ';').
    """
    texto = conteudo.decode("utf-8-sig", errors="replace")
    try:
        dialeto = csv.Sniffer().sniff(texto.splitlines()[0], delimiters=",;\t")
        sep = dialeto.delimiter
    except Exception:
        sep = ";" if texto.count(";") >= texto.count(",") else ","
    linhas = list(csv.reader(io.StringIO(texto), delimiter=sep))
    linhas = [l for l in linhas if any(str(c).strip() for c in l)]
    if not linhas:
        return {"formalizacao": {}, "avisos": ["CSV vazio."]}

    # (b) vertical: muitas linhas com 2 colunas e poucos cabeçalhos reconhecidos na 1ª linha
    primeira = linhas[0]
    reconhecidos = sum(1 for c in primeira if _norm(c) in MAPA_FORMALIZACAO)
    if reconhecidos <= 1 and all(len(l) >= 2 for l in linhas):
        d = {}
        for l in linhas:
            campo = MAPA_FORMALIZACAO.get(_norm(l[0]))
            if campo and str(l[1]).strip():
                d[campo] = _parse_valor(l[1]) if campo in CAMPOS_VALOR else str(l[1]).strip()
        return {"formalizacao": d, "avisos": []}

    # (a) horizontal
    headers = primeira
    valores = linhas[1] if len(linhas) > 1 else []
    return {"formalizacao": _mapear(headers, valores, MAPA_FORMALIZACAO), "avisos": []}


def parse_arquivo(nome_arquivo: str, conteudo: bytes) -> dict:
    """Roteia por extensão. Retorna {formalizacao, parceria?, repasses?, avisos}."""
    nome = (nome_arquivo or "").lower()
    if nome.endswith(".csv"):
        return _ler_csv(conteudo)
    if nome.endswith((".xlsx", ".xlsm", ".xls")):
        return parse_formalizacao_xlsx(conteudo)
    raise ValueError("Formato não suportado. Envie .xlsx, .xls ou .csv.")
```

> **Fase 2 (passo 03)** acrescenta `parse_parceria_xlsx` e `parse_repasses_xlsx` e os inclui no
> retorno de `parse_formalizacao_xlsx`/`parse_arquivo`. Por ora, `parceria`/`repasses` ficam ausentes
> e o frontend só preenche a etapa 1.

## 1.2 Rota — `main.py`

No topo, junto dos imports locais:
```python
import import_planilha
```
Garanta o import do FastAPI para upload (pode já existir):
```python
from fastapi import UploadFile, File
```
Adicione a rota (perto das rotas de export):
```python
@app.post("/api/import/planilha")
async def importar_planilha(file: UploadFile = File(...)):
    """Lê uma planilha/CSV e devolve os campos para PRÉ-PREENCHER o formulário. NÃO grava no banco."""
    conteudo = await file.read()
    if len(conteudo) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo muito grande (máx. 10 MB).")
    try:
        resultado = import_planilha.parse_arquivo(file.filename, conteudo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Não foi possível ler o arquivo: {e}")

    form = resultado.get("formalizacao") or {}
    return {
        "formalizacao": form,
        "parceria": resultado.get("parceria"),
        "repasses": resultado.get("repasses", []),
        "avisos": resultado.get("avisos", []),
        "campos_preenchidos": len(form),
    }
```

## 1.3 Teste rápido (sem frontend)

1. Exporte uma entidade pelo dashboard (gera o `.xlsx` no layout modelo).
2. Reenvie esse arquivo para a rota:
```bash
curl -X POST http://localhost:8000/api/import/planilha -F "file=@Prefinance_Casa_de_Luz.xlsx"
```
Deve retornar `formalizacao` com `razao_social`, `cnpj`, `valor` (número), `situacao`, etc.

---

## 1.4 Critérios de aceite

- [ ] Reenviar um `.xlsx` exportado pelo sistema retorna os campos de formalização corretos.
- [ ] `valor` volta como **número** (ex.: `20000.0`), não string.
- [ ] Um CSV horizontal (cabeçalhos + 1 linha) e um CSV vertical (`Campo;Valor`) funcionam.
- [ ] Arquivo de formato inválido → `400` com mensagem clara.
- [ ] Nenhuma rota existente foi alterada; nada é gravado no banco.

## 1.5 Segurança / reversão

Somente leitura, em memória. Reverter = remover a rota e apagar `import_planilha.py`.

> Próximo: `02-frontend-dropzone-e-preenchimento.md`.
