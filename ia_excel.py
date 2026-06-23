# ia_excel.py
# Lê um .xlsx em memória e devolve um resumo textual compacto para o contexto do LLM.
import io
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

MAX_LINHAS_POR_ABA = int(os.getenv("MAX_LINHAS_CONTEXTO", "50"))


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
