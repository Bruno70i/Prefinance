# import_planilha.py
# Lê uma planilha (.xlsx) ou CSV e extrai campos do cadastro. SOMENTE LEITURA (não grava no banco).
# É o inverso de excel_modelo.py.
import io
import re
import csv
import datetime
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
    "N.O": "numero_emenda",
    "N.": "numero_emenda",
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


# --- DADOS DA PARCERIA ---
MAPA_PARCERIA = {
    "AJUSTE": "ajuste_termo",
    "INICIO DAS ATIVIDADES": "inicio_atividades",
    "TERMINO DAS ATIVIDADES": "termino_atividades",
    "GESTOR DA PARCERIA": "gestor_parceria",
    "PROJETO": "projeto",
    "ATENDIMENTO": "atendimento_descricao",
    "META (MES)": "meta_mes_atendimentos",
    "RESPONSAVEL PELA ENTIDADE": "responsavel_entidade",
}
CATEGORIAS = ["Saúde Mental", "Fisioterapia", "Fono", "Animal", "Outros"]
ESPECIALIDADES = [
    "Academia Clínica", "Acupuntura", "Assistente Social", "Atividade Educativa", "Educador Físico",
    "Fisio", "Fono", "Hidroginástica/\nHidroterapia", "Massoterapeuta", "Médico (Neurologista)",
    "Musicoterapia", "Neuropediatra", "Neuropsicologia", "Nutricionista", "Odonto", "Oficinas Lúdicas",
    "Oftalmologia", "Ortopedista", "Pediatria", "Pilates", "Psicologia", "Psicanalista", "Psiquiatria",
    "Psicomotricista", "Psicopedagogo", "Práticas Integrativas", "Reflexologia", "T.O.", "Veterinário",
]


def _parse_data(v):
    """'15/01/2026' ou datetime -> 'YYYY-MM-DD' (ou None)."""
    if v is None or str(v).strip() in ("", "------"):
        return None
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.strftime("%Y-%m-%d")
    s = str(v).strip()
    m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", s)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    return None


def parse_parceria_xlsx(wb) -> dict:
    ws = _achar_aba(wb, "PARCERIA")
    if not ws:
        return {}
    headers = [_norm(c.value) for c in ws[2]]
    valores = [c.value for c in ws[3]]
    por_norm = {h: v for h, v in zip(headers, valores)}

    parceria = {}
    for hnorm, campo in MAPA_PARCERIA.items():
        v = por_norm.get(hnorm)
        if v is None or str(v).strip() == "":
            continue
        if campo in ("inicio_atividades", "termino_atividades"):
            parceria[campo] = _parse_data(v)
        elif campo == "meta_mes_atendimentos":
            parceria[campo] = str(v).strip()
        else:
            parceria[campo] = str(v).strip()

    cats = {}
    esp = {}
    for c in CATEGORIAS:
        n_c = _norm(c)
        if n_c in headers:
            idx = headers.index(n_c)
            v = valores[idx]
            if v is not None and str(v).strip().upper() == "X":
                cats[c] = True
    for e in ESPECIALIDADES:
        n_e = _norm(e)
        if n_e in headers:
            idx = len(headers) - 1 - headers[::-1].index(n_e)
            v = valores[idx]
            if v is not None and str(v).strip() not in ("", "0"):
                try:
                    esp[e] = int(float(str(v).replace(",", ".")))
                except ValueError:
                    pass
    if cats:
        parceria["categorias"] = cats
    if esp:
        parceria["especialidades"] = esp
    return parceria


# --- REPASSE E PRESTAÇÃO DE CONTAS ---
LINHA_REPASSE = {
    2: "repasse_oficio", 3: "repasse_periodo", 4: "repasse_parcela", 5: "repasse_retencao",
    6: "repasse_valor_final", 7: "repasse_vencimento", 8: "repasse_pa", 9: "repasse_data_pagamento",
    10: "prestacao_oficio", 11: "prestacao_data_entrega", 12: "prestacao_pa",
    13: "prestacao_sugestao_glosa", 14: "prestacao_reconsideracao",
}
CAMPOS_DATA_REP = {"repasse_vencimento", "repasse_data_pagamento", "prestacao_data_entrega"}
CAMPOS_MOEDA_REP = {"repasse_parcela", "repasse_retencao", "repasse_valor_final",
                    "prestacao_sugestao_glosa", "prestacao_reconsideracao"}


def parse_repasses_xlsx(wb) -> list:
    ws = _achar_aba(wb, "REPASSE")
    if not ws:
        return []
    repasses = []
    for col in range(5, ws.max_column + 1):
        rotulo_mes = ws.cell(row=1, column=col).value
        mes = str(rotulo_mes).strip() if rotulo_mes else ""
        if not re.match(r"^\d{2}\.\d{4}$", mes):
            continue
        rep = {"mes_referencia": mes}
        tem_dado = False
        for linha, campo in LINHA_REPASSE.items():
            v = ws.cell(row=linha, column=col).value
            if v is None or str(v).strip() in ("", "------"):
                continue
            if campo in CAMPOS_DATA_REP:
                rep[campo] = _parse_data(v)
            elif campo in CAMPOS_MOEDA_REP:
                rep[campo] = _parse_valor(v) or 0
            else:
                rep[campo] = str(v).strip()
            tem_dado = True
        if tem_dado:
            repasses.append(rep)
    return repasses


def parse_formalizacao_xlsx(conteudo: bytes) -> dict:
    wb = openpyxl.load_workbook(io.BytesIO(conteudo), data_only=True)
    ws = _achar_aba(wb, "FORMALIZ") or wb.worksheets[0]
    headers = _linha_valores(ws, 2)
    avisos = []

    linhas_dados = [r for r in range(3, ws.max_row + 1)
                    if any(c.value not in (None, "") for c in ws[r])]
    if not linhas_dados:
        return {"formalizacao": {}, "avisos": ["A aba de Formalização não tem linhas de dados."]}

    primeira = _mapear(headers, _linha_valores(ws, linhas_dados[0]), MAPA_FORMALIZACAO)
    if len(linhas_dados) > 1:
        nome = primeira.get("razao_social", "a primeira")
        avisos.append(f"O arquivo contém {len(linhas_dados)} entidades; importada {nome}.")

    parceria = parse_parceria_xlsx(wb)
    repasses = parse_repasses_xlsx(wb)

    ws_rep = _achar_aba(wb, "REPASSE")
    if ws_rep:
        for r_idx in range(1, 20):
            lbl = _norm(ws_rep.cell(row=r_idx, column=1).value)
            val = ws_rep.cell(row=r_idx, column=2).value
            if val is not None and str(val).strip() != "":
                s_val = str(val).strip()
                if "COD SCIM" in lbl or "COD. SCIM" in lbl:
                    primeira["cod_scim"] = s_val
                elif "PA EMPENHO" in lbl or "P.A. EMPENHO" in lbl:
                    primeira["pa_empenho"] = s_val
                elif "OBJETO" in lbl:
                    primeira["objeto_descricao"] = s_val

    return {
        "formalizacao": primeira,
        "parceria": partnership_fields_adapt(parceria),
        "repasses": repasses,
        "avisos": avisos
    }


def partnership_fields_adapt(parceria: dict) -> dict:
    # Retorna o dicionário de dados da parceria adequado para o frontend
    return parceria


def _ler_csv(conteudo: bytes) -> dict:
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

    primeira = linhas[0]
    reconhecidos = sum(1 for c in primeira if _norm(c) in MAPA_FORMALIZACAO)
    if reconhecidos <= 1 and all(len(l) >= 2 for l in linhas):
        d = {}
        for l in linhas:
            campo = MAPA_FORMALIZACAO.get(_norm(l[0]))
            if campo and str(l[1]).strip():
                d[campo] = _parse_valor(l[1]) if campo in CAMPOS_VALOR else str(l[1]).strip()
        return {"formalizacao": d, "avisos": []}

    headers = primeira
    valores = linhas[1] if len(linhas) > 1 else []
    return {"formalizacao": _mapear(headers, valores, MAPA_FORMALIZACAO), "avisos": []}


def parse_arquivo(nome_arquivo: str, conteudo: bytes) -> dict:
    nome = (nome_arquivo or "").lower()
    if nome.endswith(".csv"):
        return _ler_csv(conteudo)
    if nome.endswith((".xlsx", ".xlsm", ".xls")):
        return parse_formalizacao_xlsx(conteudo)
    raise ValueError("Formato não suportado. Envie .xlsx, .xls ou .csv.")
