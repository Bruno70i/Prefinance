# ia_contexto.py
# Motor de contexto: lê o PostgreSQL e monta um bloco textual ancorado para o LLM.
# SOMENTE LEITURA. Nenhuma escrita no banco.
import os
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

_DB_HOST = os.getenv("DB_HOST", "localhost")
_DB_PORT = os.getenv("DB_PORT", "5432")
_DB_USER = os.getenv("DB_USER", "postgres")
_DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
_DB_NAME = os.getenv("DB_NAME", "prefinance")
_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{_DB_USER}:{_DB_PASSWORD}@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}",
)
MAX_CHARS = int(os.getenv("IA_MAX_CONTEXT_CHARS", "12000"))

# Engine próprio (evita import circular com main.py)
_engine = create_engine(_DATABASE_URL, pool_pre_ping=True)


def _brl(v) -> str:
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def _d(v) -> str:
    return v.strftime("%d/%m/%Y") if v is not None and hasattr(v, "strftime") else "—"


def agregados(conn) -> str:
    total_ent = conn.execute(text("SELECT COUNT(*) FROM entidades")).scalar() or 0
    volume = conn.execute(text("SELECT COALESCE(SUM(valor),0) FROM entidades")).scalar() or 0
    repassado = conn.execute(text(
        "SELECT COALESCE(SUM(repasse_valor_final),0) FROM repasses_mensais "
        "WHERE repasse_data_pagamento IS NOT NULL"
    )).scalar() or 0
    por_status = conn.execute(text(
        "SELECT COALESCE(situacao,'(sem status)') AS s, COUNT(*) AS n "
        "FROM entidades GROUP BY 1 ORDER BY 2 DESC"
    )).fetchall()
    linhas = "; ".join(f"{r.s}: {r.n}" for r in por_status)
    return (
        "RESUMO GERAL:\n"
        f"- Total de entidades/parcerias: {total_ent}\n"
        f"- Volume total dos contratos (soma de 'valor'): {_brl(volume)}\n"
        f"- Total já repassado (parcelas com pagamento confirmado): {_brl(repassado)}\n"
        f"- Distribuição por status: {linhas}\n"
    )


def roster(conn) -> str:
    rows = conn.execute(text("""
        SELECT razao_social, cnpj, COALESCE(situacao,'—') AS situacao,
               COALESCE(numero_emenda, pa_emenda, '—') AS pa, valor,
               COALESCE(responsavel_nome, '—') AS responsavel_nome,
               COALESCE(cpf_representante, '—') AS cpf_representante,
               COALESCE(vereador, '—') AS vereador
        FROM entidades ORDER BY razao_social
    """)).fetchall()
    out = ["LISTA DE ENTIDADES CADASTRADAS (uma por linha):"]
    for r in rows:
        out.append(f"- {r.razao_social} | CNPJ: {r.cnpj or '—'} | Status: {r.situacao} "
                   f"| PA: {r.pa} | Valor: {_brl(r.valor)} | Resp. Legal: {r.responsavel_nome} (CPF: {r.cpf_representante}) | Vereador: {r.vereador}")
    return "\n".join(out)


def _ids_relevantes(conn, pergunta: str) -> list:
    """Seleciona entidades citadas na pergunta por nome, CNPJ, PA, vereador, gestor ou responsável."""
    p = (pergunta or "").lower()
    digitos = re.sub(r"\D", "", pergunta or "")
    
    # Palavras-chave da pergunta com 4 ou mais caracteres (evita pronomes curtos)
    p_words = [w for w in re.split(r'\W+', p) if len(w) >= 4]

    rows = conn.execute(text("""
        SELECT e.id, e.razao_social, e.cnpj, e.numero_emenda, e.pa_emenda, e.vereador,
               e.responsavel_nome, e.cpf_representante, p.gestor_parceria
        FROM entidades e LEFT JOIN dados_parceria p ON p.entidade_id = e.id
    """)).fetchall()
    ids = []
    for r in rows:
        campos = [r.razao_social, r.cnpj, r.numero_emenda, r.pa_emenda, r.vereador, r.responsavel_nome, r.cpf_representante, r.gestor_parceria]
        achou = False
        for c in campos:
            if not c:
                continue
            cl = str(c).lower()
            
            # match se a palavra chave estiver contida no campo
            if any(w in cl for w in p_words):
                achou = True
                break
            # match completo
            if cl in p:
                achou = True
                break
            # ... ou por dígitos de CNPJ presentes na pergunta
            cd = re.sub(r"\D", "", str(c))
            if cd and len(cd) >= 6 and digitos and cd in digitos:
                achou = True
                break
        if achou:
            ids.append(str(r.id))
    return ids


def detalhe_entidade(conn, entidade_id: str) -> str:
    m = conn.execute(text("""
        SELECT e.*, p.ajuste_termo, p.inicio_atividades, p.termino_atividades, p.gestor_parceria,
               p.projeto, p.meta_mes_atendimentos, p.atendimento_descricao, p.especialidades,
               p.responsavel_entidade
        FROM entidades e LEFT JOIN dados_parceria p ON p.entidade_id = e.id
        WHERE e.id = :id
    """), {"id": entidade_id}).fetchone()
    if not m:
        return ""
    m = m._mapping
    reps = conn.execute(text("""
        SELECT mes_referencia, repasse_valor_final, repasse_vencimento, repasse_data_pagamento,
               prestacao_oficio, prestacao_data_entrega
        FROM repasses_mensais WHERE entidade_id = :id ORDER BY mes_referencia
    """), {"id": entidade_id}).fetchall()

    linhas = [
        f"DETALHE DA ENTIDADE: {m['razao_social']}",
        f"- CNPJ: {m['cnpj'] or '—'} | Status: {m['situacao'] or '—'} | Valor: {_brl(m['valor'])}",
        f"- Responsável legal: {m['responsavel_nome'] or '—'} (CPF: {m['cpf_representante'] or '—'}, Tel: {m['telefone'] or '—'}) | Vereador: {m['vereador'] or '—'}",
        f"- PA Emenda: {m['pa_emenda'] or '—'} | PA Formalização: {m['pa_formalizacao'] or '—'} "
        f"| Nº Emenda: {m['numero_emenda'] or '—'}",
        f"- Justificativa: {m['justificativa'] or '—'}",
        f"- Objeto: {m['objeto_descricao'] or '—'}",
        f"- Ajuste/Termo: {m['ajuste_termo'] or '—'} | Gestor: {m['gestor_parceria'] or '—'}",
        f"- Vigência: {_d(m['inicio_atividades'])} a {_d(m['termino_atividades'])} "
        f"| Meta mensal: {m['meta_mes_atendimentos'] or 0}",
        f"- Histórico: {(m['historico'] or '—')}",
    ]
    if reps:
        linhas.append("- Repasses:")
        for r in reps:
            rm = r._mapping
            pago = "pago em " + _d(rm["repasse_data_pagamento"]) if rm["repasse_data_pagamento"] else "não pago"
            linhas.append(
                f"   • {rm['mes_referencia']}: {_brl(rm['repasse_valor_final'])} "
                f"(venc. {_d(rm['repasse_vencimento'])}, {pago})"
            )
    else:
        linhas.append("- Repasses: nenhum lançado.")
    return "\n".join(linhas)


def montar_contexto(pergunta: str) -> str:
    """Monta o bloco de CONTEXTO completo, respeitando o orçamento de caracteres."""
    with _engine.connect() as conn:
        partes = [agregados(conn), roster(conn)]
        for eid in _ids_relevantes(conn, pergunta):
            partes.append(detalhe_entidade(conn, eid))
    contexto = "\n\n".join(p for p in partes if p)
    if len(contexto) > MAX_CHARS:
        contexto = contexto[:MAX_CHARS] + "\n[...contexto truncado por limite de tamanho...]"
    return contexto
