import os
os.environ["PGCLIENTENCODING"] = "utf-8"

import uuid
import json
from datetime import date
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
import io
import pandas as pd
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Carrega variáveis de ambiente
load_dotenv()

app = FastAPI(
    title="PreFinance API Backend",
    description="API para gerenciar entidades e integrações do sistema PreFinance",
    version="1.0.0"
)

# Configuração de CORS para permitir requisições do frontend Nuxt 3
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite qualquer origem em desenvolvimento. Pode ser restrito a ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do banco de dados
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "prefinance")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Inicialização do Engine SQLAlchemy
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
except Exception as db_init_err:
    print(f"Erro ao inicializar conexão com o banco de dados: {db_init_err}")
    engine = None

# Schema de Parceria (Tabela 1:1 dados_parceria)
class ParceriaCreate(BaseModel):
    ajuste_termo: Optional[str] = Field(None, description="Ajuste / Termo de Fomento (Ex: TERMO DE FOMENTO 29/2026)")
    inicio_atividades: Optional[date] = Field(None, description="Data de início das atividades")
    termino_atividades: Optional[date] = Field(None, description="Data de término das atividades")
    gestor_parceria: Optional[str] = Field(None, description="Nome do gestor público da parceria")
    projeto: Optional[str] = Field(None, description="Nome do projeto da parceria")
    categorias: Optional[Dict[str, bool]] = Field(default_factory=dict, description="Categorias/Áreas da parceria (booleanos)")
    atendimento_descricao: Optional[str] = Field(None, description="Público-alvo ou descrição dos atendimentos")
    meta_mes_atendimentos: Optional[int] = Field(0, description="Meta mensal total de atendimentos da parceria")
    responsavel_entidade: Optional[str] = Field(None, description="Responsável pela entidade na parceria")
    especialidades: Optional[Dict[str, int]] = Field(default_factory=dict, description="Especialidades e metas individuais associadas")

# Schema de Repasse Mensal (Tabela 1:N repasses_mensais)
class RepasseCreate(BaseModel):
    mes_referencia: str = Field(..., description="Mês de referência do repasse (Ex: Janeiro/2025)")
    repasse_oficio: Optional[str] = Field(None, description="Número do Ofício de repasse")
    repasse_periodo: Optional[str] = Field(None, description="Período do repasse (Ex: Janeiro)")
    repasse_parcela: Optional[float] = Field(0.0, description="Valor bruto da parcela de repasse")
    repasse_retencao: Optional[float] = Field(0.0, description="Valor de retenções do repasse")
    repasse_valor_final: Optional[float] = Field(0.0, description="Valor líquido creditado")
    repasse_vencimento: Optional[date] = Field(None, description="Data de vencimento do repasse")
    repasse_pa: Optional[str] = Field(None, description="Processo Administrativo de Repasse")
    repasse_data_pagamento: Optional[date] = Field(None, description="Data efetiva do pagamento")
    prestacao_oficio: Optional[str] = Field(None, description="Número do Ofício da prestação de contas")
    prestacao_data_entrega: Optional[date] = Field(None, description="Data de entrega da prestação de contas")
    prestacao_pa: Optional[str] = Field(None, description="Processo Administrativo de Prestação de Contas")
    prestacao_sugestao_glosa: Optional[float] = Field(0.0, description="Sugestão de glosa de valores")
    prestacao_reconsideracao: Optional[float] = Field(0.0, description="Valor reconsiderado de glosa")
    prestacao_mts: Optional[str] = Field(None, description="Manifestação Técnica do Setor (MTS)")

# Schema Pydantic para validação dos dados de entrada do formulário
class EntidadeCreate(BaseModel):
    razao_social: str = Field(..., min_length=1, description="Razão Social da entidade (obrigatório)")
    cnpj: Optional[str] = Field(None, description="CNPJ formatado ou apenas números")
    responsavel_nome: Optional[str] = Field(None, description="Nome do responsável direto")
    situacao: Optional[str] = Field(None, description="Situação atual da formalização")
    historico: Optional[str] = Field(None, description="Registro cronológico de eventos e datas")
    pa_emenda: Optional[str] = Field(None, description="Processo Administrativo de Emenda")
    localizacao_pa_emenda: Optional[str] = Field(None, description="Localização física ou digital do PA de emenda")
    emenda_alterada: Optional[str] = Field(None, description="Indicação se a emenda foi alterada")
    pa_formalizacao: Optional[str] = Field(None, description="Processo Administrativo de Formalização")
    numero_emenda: Optional[str] = Field(None, description="Número da emenda parlamentar")
    vereador: Optional[str] = Field(None, description="Nome do vereador autor da emenda")
    justificativa: Optional[str] = Field(None, description="Justificativa da emenda")
    valor: Optional[float] = Field(None, description="Valor monetário total destinado")
    cod_scim: Optional[str] = Field(None, description="Código identificador do sistema SCIM")
    pa_empenho: Optional[str] = Field(None, description="Processo Administrativo de Empenho")
    objeto_descricao: Optional[str] = Field(None, description="Descrição detalhada do objeto da emenda/parceria")
    parceria: Optional[ParceriaCreate] = Field(None, description="Dados operacionais da parceria vinculados (tabela 1:1)")
    repasses: Optional[List[RepasseCreate]] = Field(default_factory=list, description="Lista de lançamentos de repasses mensais (tabela 1:N)")
    configuracoes_extras: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configurações e dados adicionais da entidade")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "razao_social": "Associação de Assistência Social Antigravitacional",
                "cnpj": "12.345.678/0001-99",
                "responsavel_nome": "João da Silva",
                "configuracoes_extras": {
                    "metas": {"atendimentos_mensais": 150},
                    "historico_formalizacao": "Termo de fomento assinado em 2026."
                }
            }
        }
    )

def safe_str_decode(err: Exception) -> str:
    """
    Decodifica com segurança a mensagem de erro para evitar erros de UTF-8 no Windows,
    especialmente quando a exceção vem do SQLAlchemy contendo erros do driver.
    """
    # 0. Se for o próprio erro de decodificação de codec do Python
    if isinstance(err, UnicodeDecodeError) or "codec can't decode" in str(err):
        return "Conexão rejeitada pelo banco de dados (provavelmente senha incorreta do PostgreSQL no seu arquivo .env ou banco offline)."

    # 1. Se houver um erro original do psycopg2 encapsulado
    orig_err = getattr(err, "orig", None)
    if orig_err is not None:
        # Se for OperationalError ou similar do psycopg2, tenta pegar o pgerror bruto
        pgerror = getattr(orig_err, "pgerror", None)
        if pgerror is not None:
            try:
                if isinstance(pgerror, bytes):
                    return pgerror.decode("cp1252", errors="replace")
                return str(pgerror)
            except Exception:
                pass
        
        # Tenta decodificar os argumentos do erro original
        args = getattr(orig_err, "args", None)
        if args:
            try:
                decoded = []
                for arg in args:
                    if isinstance(arg, bytes):
                        decoded.append(arg.decode("cp1252", errors="replace"))
                    else:
                        decoded.append(str(arg))
                return " - ".join(decoded)
            except Exception:
                pass

    # 2. Tenta a representação padrão
    try:
        return str(err)
    except Exception as decode_fail:
        # 3. Se str(err) falhar, tenta inspecionar os argumentos da própria exceção recebida
        args = getattr(err, "args", None)
        if args:
            try:
                decoded = []
                for arg in args:
                    if isinstance(arg, bytes):
                        decoded.append(arg.decode("cp1252", errors="replace"))
                    else:
                        decoded.append(str(arg))
                return " - ".join(decoded)
            except Exception:
                pass
        return "Conexão rejeitada pelo banco de dados (provavelmente senha incorreta do PostgreSQL no seu arquivo .env ou banco offline)."

@app.get("/")
def read_root():
    return {"status": "online", "message": "PreFinance API Backend está ativo."}

@app.get("/api/entidades")
def get_entidades():
    """
    Lista todas as entidades cadastradas.
    """
    if not engine:
        raise HTTPException(status_code=500, detail="Banco de dados não inicializado.")
    
    try:
        with engine.begin() as conn:
            query = text("""
                SELECT id, razao_social, cnpj, responsavel_nome, situacao, numero_emenda, valor, configuracoes_extras 
                FROM entidades 
                ORDER BY razao_social ASC
            """)
            res = conn.execute(query).fetchall()
            
            entidades = []
            for row in res:
                entidades.append({
                    "id": row.id,
                    "razao_social": row.razao_social,
                    "cnpj": row.cnpj,
                    "responsavel_nome": row.responsavel_nome,
                    "situacao": row.situacao,
                    "numero_emenda": row.numero_emenda,
                    "valor": row.valor,
                    "configuracoes_extras": row.configuracoes_extras
                })
            return entidades
    except Exception as e:
        error_msg = safe_str_decode(e)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar entidades: {error_msg}")

@app.post("/api/entidades", status_code=status.HTTP_201_CREATED)
def create_entidade(entidade: EntidadeCreate):
    """
    Endpoint para inserção de uma nova entidade no banco de dados PostgreSQL.
    """
    if not engine:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Serviço de banco de dados não inicializado. Verifique as configurações de ambiente."
        )

    # Preparação dos dados para inserção
    try:
        extras_json = json.dumps(entidade.configuracoes_extras) if entidade.configuracoes_extras else json.dumps({})
        
        with engine.begin() as conn:
            # Executa a inserção retornando o id gerado
            query_insert = text("""
                INSERT INTO entidades (
                    razao_social, cnpj, responsavel_nome, situacao, historico, 
                    pa_emenda, localizacao_pa_emenda, emenda_alterada, pa_formalizacao, 
                    numero_emenda, vereador, justificativa, valor, cod_scim, pa_empenho, 
                    objeto_descricao, configuracoes_extras
                )
                VALUES (
                    :razao_social, :cnpj, :responsavel, :situacao, :historico, 
                    :pa_emenda, :localizacao_pa_emenda, :emenda_alterada, :pa_formalizacao, 
                    :numero_emenda, :vereador, :justificativa, :valor, :cod_scim, :pa_empenho, 
                    :objeto_descricao, :extras
                )
                RETURNING id;
            """)
            
            result = conn.execute(query_insert, {
                "razao_social": entidade.razao_social.strip(),
                "cnpj": entidade.cnpj.strip() if entidade.cnpj else None,
                "responsavel": entidade.responsavel_nome.strip() if entidade.responsavel_nome else None,
                "situacao": entidade.situacao.strip() if entidade.situacao else None,
                "historico": entidade.historico.strip() if entidade.historico else None,
                "pa_emenda": entidade.pa_emenda.strip() if entidade.pa_emenda else None,
                "localizacao_pa_emenda": entidade.localizacao_pa_emenda.strip() if entidade.localizacao_pa_emenda else None,
                "emenda_alterada": entidade.emenda_alterada.strip() if entidade.emenda_alterada else None,
                "pa_formalizacao": entidade.pa_formalizacao.strip() if entidade.pa_formalizacao else None,
                "numero_emenda": entidade.numero_emenda.strip() if entidade.numero_emenda else None,
                "vereador": entidade.vereador.strip() if entidade.vereador else None,
                "justificativa": entidade.justificativa.strip() if entidade.justificativa else None,
                "valor": entidade.valor,
                "cod_scim": entidade.cod_scim.strip() if entidade.cod_scim else None,
                "pa_empenho": entidade.pa_empenho.strip() if entidade.pa_empenho else None,
                "objeto_descricao": entidade.objeto_descricao.strip() if entidade.objeto_descricao else None,
                "extras": extras_json
            })
            
            # Recupera o ID gerado pelo Postgres
            new_id = result.fetchone()[0]
            
            # Se dados de parceria aninhados forem enviados, realiza a gravação 1:1 na tabela dados_parceria
            if entidade.parceria:
                parc = entidade.parceria
                query_insert_parceria = text("""
                    INSERT INTO dados_parceria (
                        entidade_id, ajuste_termo, inicio_atividades, termino_atividades,
                        gestor_parceria, projeto, categorias, atendimento_descricao,
                        meta_mes_atendimentos, responsavel_entidade, especialidades
                    )
                    VALUES (
                        :entidade_id, :ajuste_termo, :inicio_atividades, :termino_atividades,
                        :gestor_parceria, :projeto, :categorias, :atendimento_descricao,
                        :meta_mes_atendimentos, :responsavel_entidade, :especialidades
                    )
                """)
                
                # Conversão de datas e JSONs
                inicio_str = parc.inicio_atividades.isoformat() if parc.inicio_atividades else None
                termino_str = parc.termino_atividades.isoformat() if parc.termino_atividades else None
                
                conn.execute(query_insert_parceria, {
                    "entidade_id": new_id,
                    "ajuste_termo": parc.ajuste_termo.strip() if parc.ajuste_termo else None,
                    "inicio_atividades": inicio_str,
                    "termino_atividades": termino_str,
                    "gestor_parceria": parc.gestor_parceria.strip() if parc.gestor_parceria else None,
                    "projeto": parc.projeto.strip() if parc.projeto else None,
                    "categorias": json.dumps(parc.categorias),
                    "atendimento_descricao": parc.atendimento_descricao.strip() if parc.atendimento_descricao else None,
                    "meta_mes_atendimentos": parc.meta_mes_atendimentos,
                    "responsavel_entidade": parc.responsavel_entidade.strip() if parc.responsavel_entidade else None,
                    "especialidades": json.dumps(parc.especialidades)
                })

            # Se houver uma lista de repasses de competência aninhados, insere-os em lote de forma atômica (1:N)
            if entidade.repasses:
                query_insert_repasse = text("""
                    INSERT INTO repasses_mensais (
                        entidade_id, mes_referencia, repasse_oficio, repasse_periodo,
                        repasse_parcela, repasse_retencao, repasse_valor_final, repasse_vencimento,
                        repasse_pa, repasse_data_pagamento, prestacao_oficio, prestacao_data_entrega,
                        prestacao_pa, prestacao_sugestao_glosa, prestacao_reconsideracao, prestacao_mts
                    )
                    VALUES (
                        :entidade_id, :mes_referencia, :repasse_oficio, :repasse_periodo,
                        :repasse_parcela, :repasse_retencao, :repasse_valor_final, :repasse_vencimento,
                        :repasse_pa, :repasse_data_pagamento, :prestacao_oficio, :prestacao_data_entrega,
                        :prestacao_pa, :prestacao_sugestao_glosa, :prestacao_reconsideracao, :prestacao_mts
                    )
                """)
                
                for rep in entidade.repasses:
                    conn.execute(query_insert_repasse, {
                        "entidade_id": new_id,
                        "mes_referencia": rep.mes_referencia.strip(),
                        "repasse_oficio": rep.repasse_oficio.strip() if rep.repasse_oficio else None,
                        "repasse_periodo": rep.repasse_periodo.strip() if rep.repasse_periodo else None,
                        "repasse_parcela": rep.repasse_parcela,
                        "repasse_retencao": rep.repasse_retencao,
                        "repasse_valor_final": rep.repasse_valor_final,
                        "repasse_vencimento": rep.repasse_vencimento.isoformat() if rep.repasse_vencimento else None,
                        "repasse_pa": rep.repasse_pa.strip() if rep.repasse_pa else None,
                        "repasse_data_pagamento": rep.repasse_data_pagamento.isoformat() if rep.repasse_data_pagamento else None,
                        "prestacao_oficio": rep.prestacao_oficio.strip() if rep.prestacao_oficio else None,
                        "prestacao_data_entrega": rep.prestacao_data_entrega.isoformat() if rep.prestacao_data_entrega else None,
                        "prestacao_pa": rep.prestacao_pa.strip() if rep.prestacao_pa else None,
                        "prestacao_sugestao_glosa": rep.prestacao_sugestao_glosa,
                        "prestacao_reconsideracao": rep.prestacao_reconsideracao,
                        "prestacao_mts": rep.prestacao_mts.strip() if rep.prestacao_mts else None
                    })
            
            return {
                "status": "success",
                "message": "Entidade, dados de parceria e repasses salvos com sucesso!",
                "id": str(new_id)
            }

    except HTTPException as http_err:
        # Repassa exceções HTTP geradas por nós (como CNPJ duplicado)
        raise http_err
    except SQLAlchemyError as db_err:
        error_msg = safe_str_decode(db_err)
        print(f"Erro de Banco de Dados durante inserção: {error_msg}")
        
        # Identifica erro comum de chave única/restrição no PostgreSQL
        if "unique constraint" in error_msg.lower() or "duplicar chave" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro de restrição de unicidade: Uma entidade com estes dados já existe."
            )
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro de banco de dados: {error_msg}"
        )
    except Exception as err:
        error_msg = safe_str_decode(err)
        print(f"Erro inesperado: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado no servidor: {error_msg}"
        )

@app.get("/api/entidades")
def list_entidades():
    """
    Retorna a lista de todas as entidades cadastradas no banco, enriquecidas com seus
    dados de parceria (1:1) e lançamentos de repasses (1:N).
    """
    if not engine:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Serviço de banco de dados não inicializado."
        )
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT e.*, 
                       p.ajuste_termo, p.inicio_atividades, p.termino_atividades, p.gestor_parceria,
                       p.projeto, p.categorias, p.atendimento_descricao, p.meta_mes_atendimentos,
                       p.responsavel_entidade, p.especialidades
                FROM entidades e
                LEFT JOIN dados_parceria p ON e.id = p.entidade_id
                ORDER BY e.razao_social ASC;
            """)
            result = conn.execute(query)
            entidades = []
            for row in result:
                row_map = row._mapping
                
                extras = row_map["configuracoes_extras"]
                if isinstance(extras, str):
                    extras = json.loads(extras)
                elif extras is None:
                    extras = {}
                
                entidade = {
                    "id": str(row_map["id"]),
                    "razao_social": row_map["razao_social"],
                    "cnpj": row_map["cnpj"],
                    "responsavel_nome": row_map["responsavel_nome"],
                    "situacao": row_map["situacao"],
                    "historico": row_map["historico"],
                    "pa_emenda": row_map["pa_emenda"],
                    "localizacao_pa_emenda": row_map["localizacao_pa_emenda"],
                    "emenda_alterada": row_map["emenda_alterada"],
                    "pa_formalizacao": row_map["pa_formalizacao"],
                    "numero_emenda": row_map["numero_emenda"],
                    "vereador": row_map["vereador"],
                    "justificativa": row_map["justificativa"],
                    "valor": float(row_map["valor"]) if row_map["valor"] is not None else None,
                    "cod_scim": row_map["cod_scim"],
                    "pa_empenho": row_map["pa_empenho"],
                    "objeto_descricao": row_map["objeto_descricao"],
                    "configuracoes_extras": extras,
                    "created_at": row_map["created_at"].isoformat() if row_map["created_at"] else None,
                    "updated_at": row_map["updated_at"].isoformat() if row_map["updated_at"] else None
                }
                
                if row_map["ajuste_termo"] or row_map["projeto"]:
                    cats = row_map["categorias"]
                    if isinstance(cats, str):
                        cats = json.loads(cats)
                    esps = row_map["especialidades"]
                    if isinstance(esps, str):
                        esps = json.loads(esps)
                        
                    entidade["parceria"] = {
                        "ajuste_termo": row_map["ajuste_termo"],
                        "inicio_atividades": row_map["inicio_atividades"].isoformat() if row_map["inicio_atividades"] else None,
                        "termino_atividades": row_map["termino_atividades"].isoformat() if row_map["termino_atividades"] else None,
                        "gestor_parceria": row_map["gestor_parceria"],
                        "projeto": row_map["projeto"],
                        "categorias": cats or {},
                        "atendimento_descricao": row_map["atendimento_descricao"],
                        "meta_mes_atendimentos": row_map["meta_mes_atendimentos"],
                        "responsavel_entidade": row_map["responsavel_entidade"],
                        "especialidades": esps or {}
                    }
                else:
                    entidade["parceria"] = None
                
                repasses_query = text("""
                    SELECT * FROM repasses_mensais 
                    WHERE entidade_id = :entidade_id 
                    ORDER BY 
                        CASE WHEN mes_referencia ~ '^\d{2}\.\d{4}$' THEN
                            TO_DATE(mes_referencia, 'MM.YYYY')
                        ELSE
                            CURRENT_DATE
                        END DESC, 
                        mes_referencia DESC
                """)
                repasses_res = conn.execute(repasses_query, {"entidade_id": row_map["id"]})
                repasses_list = []
                for rep in repasses_res:
                    r = dict(rep._mapping)
                    r["id"] = str(r["id"])
                    r["entidade_id"] = str(r["entidade_id"])
                    if r.get("repasse_vencimento"):
                        r["repasse_vencimento"] = r["repasse_vencimento"].isoformat()
                    if r.get("repasse_data_pagamento"):
                        r["repasse_data_pagamento"] = r["repasse_data_pagamento"].isoformat()
                    if r.get("prestacao_data_entrega"):
                        r["prestacao_data_entrega"] = r["prestacao_data_entrega"].isoformat()
                    for key in ["repasse_parcela", "repasse_retencao", "repasse_valor_final", "prestacao_sugestao_glosa", "prestacao_reconsideracao"]:
                        if r.get(key) is not None:
                            r[key] = float(r[key])
                    repasses_list.append(r)
                
                entidade["repasses"] = repasses_list
                entidades.append(entidade)
                
            return entidades
            
    except Exception as err:
        error_msg = safe_str_decode(err)
        print(f"Erro ao listar entidades: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar entidades: {error_msg}"
        )

@app.put("/api/entidades/{entidade_id}")
def update_entidade(entidade_id: str, entidade: EntidadeCreate):
    """
    Atualiza uma entidade existente, incluindo seus dados de parceria e repasses de forma atômica.
    """
    if not engine:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Serviço de banco de dados não inicializado."
        )
    try:
        try:
            uuid.UUID(entidade_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de entidade inválido (deve ser UUID)."
            )

        extras_json = json.dumps(entidade.configuracoes_extras) if entidade.configuracoes_extras else json.dumps({})

        with engine.begin() as conn:
            check_exist = conn.execute(text("SELECT id FROM entidades WHERE id = :id"), {"id": entidade_id}).fetchone()
            if not check_exist:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Entidade não encontrada."
                )

            query_update = text("""
                UPDATE entidades SET
                    razao_social = :razao_social, 
                    cnpj = :cnpj, 
                    responsavel_nome = :responsavel, 
                    situacao = :situacao, 
                    historico = :historico, 
                    pa_emenda = :pa_emenda, 
                    localizacao_pa_emenda = :localizacao_pa_emenda, 
                    emenda_alterada = :emenda_alterada, 
                    pa_formalizacao = :pa_formalizacao, 
                    numero_emenda = :numero_emenda, 
                    vereador = :vereador, 
                    justificativa = :justificativa, 
                    valor = :valor, 
                    cod_scim = :cod_scim, 
                    pa_empenho = :pa_empenho, 
                    objeto_descricao = :objeto_descricao, 
                    configuracoes_extras = :extras,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id;
            """)
            
            conn.execute(query_update, {
                "id": entidade_id,
                "razao_social": entidade.razao_social.strip(),
                "cnpj": entidade.cnpj.strip() if entidade.cnpj else None,
                "responsavel": entidade.responsavel_nome.strip() if entidade.responsavel_nome else None,
                "situacao": entidade.situacao.strip() if entidade.situacao else None,
                "historico": entidade.historico.strip() if entidade.historico else None,
                "pa_emenda": entidade.pa_emenda.strip() if entidade.pa_emenda else None,
                "localizacao_pa_emenda": entidade.localizacao_pa_emenda.strip() if entidade.localizacao_pa_emenda else None,
                "emenda_alterada": entidade.emenda_alterada.strip() if entidade.emenda_alterada else None,
                "pa_formalizacao": entidade.pa_formalizacao.strip() if entidade.pa_formalizacao else None,
                "numero_emenda": entidade.numero_emenda.strip() if entidade.numero_emenda else None,
                "vereador": entidade.vereador.strip() if entidade.vereador else None,
                "justificativa": entidade.justificativa.strip() if entidade.justificativa else None,
                "valor": entidade.valor,
                "cod_scim": entidade.cod_scim.strip() if entidade.cod_scim else None,
                "pa_empenho": entidade.pa_empenho.strip() if entidade.pa_empenho else None,
                "objeto_descricao": entidade.objeto_descricao.strip() if entidade.objeto_descricao else None,
                "extras": extras_json
            })

            if entidade.parceria:
                parc = entidade.parceria
                conn.execute(text("DELETE FROM dados_parceria WHERE entidade_id = :id"), {"id": entidade_id})
                
                query_insert_parceria = text("""
                    INSERT INTO dados_parceria (
                        entidade_id, ajuste_termo, inicio_atividades, termino_atividades,
                        gestor_parceria, projeto, categorias, atendimento_descricao,
                        meta_mes_atendimentos, responsavel_entidade, especialidades
                    )
                    VALUES (
                        :entidade_id, :ajuste_termo, :inicio_atividades, :termino_atividades,
                        :gestor_parceria, :projeto, :categorias, :atendimento_descricao,
                        :meta_mes_atendimentos, :responsavel_entidade, :especialidades
                    )
                """)
                
                inicio_str = parc.inicio_atividades.isoformat() if parc.inicio_atividades else None
                termino_str = parc.termino_atividades.isoformat() if parc.termino_atividades else None
                
                conn.execute(query_insert_parceria, {
                    "entidade_id": entidade_id,
                    "ajuste_termo": parc.ajuste_termo.strip() if parc.ajuste_termo else None,
                    "inicio_atividades": inicio_str,
                    "termino_atividades": termino_str,
                    "gestor_parceria": parc.gestor_parceria.strip() if parc.gestor_parceria else None,
                    "projeto": parc.projeto.strip() if parc.projeto else None,
                    "categorias": json.dumps(parc.categorias),
                    "atendimento_descricao": parc.atendimento_descricao.strip() if parc.atendimento_descricao else None,
                    "meta_mes_atendimentos": parc.meta_mes_atendimentos,
                    "responsavel_entidade": parc.responsavel_entidade.strip() if parc.responsavel_entidade else None,
                    "especialidades": json.dumps(parc.especialidades)
                })

            if entidade.repasses is not None:
                conn.execute(text("DELETE FROM repasses_mensais WHERE entidade_id = :id"), {"id": entidade_id})
                
                query_insert_repasse = text("""
                    INSERT INTO repasses_mensais (
                        entidade_id, mes_referencia, repasse_oficio, repasse_periodo,
                        repasse_parcela, repasse_retencao, repasse_valor_final, repasse_vencimento,
                        repasse_pa, repasse_data_pagamento, prestacao_oficio, prestacao_data_entrega,
                        prestacao_pa, prestacao_sugestao_glosa, prestacao_reconsideracao, prestacao_mts
                    )
                    VALUES (
                        :entidade_id, :mes_referencia, :repasse_oficio, :repasse_periodo,
                        :repasse_parcela, :repasse_retencao, :repasse_valor_final, :repasse_vencimento,
                        :repasse_pa, :repasse_data_pagamento, :prestacao_oficio, :prestacao_data_entrega,
                        :prestacao_pa, :prestacao_sugestao_glosa, :prestacao_reconsideracao, :prestacao_mts
                    )
                """)
                
                for rep in entidade.repasses:
                    conn.execute(query_insert_repasse, {
                        "entidade_id": entidade_id,
                        "mes_referencia": rep.mes_referencia.strip(),
                        "repasse_oficio": rep.repasse_oficio.strip() if rep.repasse_oficio else None,
                        "repasse_periodo": rep.repasse_periodo.strip() if rep.repasse_periodo else None,
                        "repasse_parcela": rep.repasse_parcela,
                        "repasse_retencao": rep.repasse_retencao,
                        "repasse_valor_final": rep.repasse_valor_final,
                        "repasse_vencimento": rep.repasse_vencimento.isoformat() if rep.repasse_vencimento else None,
                        "repasse_pa": rep.repasse_pa.strip() if rep.repasse_pa else None,
                        "repasse_data_pagamento": rep.repasse_data_pagamento.isoformat() if rep.repasse_data_pagamento else None,
                        "prestacao_oficio": rep.prestacao_oficio.strip() if rep.prestacao_oficio else None,
                        "prestacao_data_entrega": rep.prestacao_data_entrega.isoformat() if rep.prestacao_data_entrega else None,
                        "prestacao_pa": rep.prestacao_pa.strip() if rep.prestacao_pa else None,
                        "prestacao_sugestao_glosa": rep.prestacao_sugestao_glosa,
                        "prestacao_reconsideracao": rep.prestacao_reconsideracao,
                        "prestacao_mts": rep.prestacao_mts.strip() if rep.prestacao_mts else None
                    })

            return {
                "id": entidade_id,
                "razao_social": entidade.razao_social,
                "cnpj": entidade.cnpj,
                "responsavel_nome": entidade.responsavel_nome,
                "configuracoes_extras": entidade.configuracoes_extras
            }

    except HTTPException as http_err:
        raise http_err
    except SQLAlchemyError as db_err:
        error_msg = safe_str_decode(db_err)
        print(f"Erro de Banco de Dados durante atualização: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro de banco de dados: {error_msg}"
        )
    except Exception as err:
        error_msg = safe_str_decode(err)
        print(f"Erro inesperado durante atualização: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado no servidor: {error_msg}"
        )

@app.get("/api/entidades/{entidade_id}/repasses")
def get_repasses(entidade_id: str):
    """
    Retorna todos os repasses vinculados a uma entidade específica.
    """
    if not engine:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Serviço de banco de dados não inicializado."
        )
    try:
        try:
            uuid.UUID(entidade_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de entidade inválido (deve ser UUID)."
            )

        with engine.connect() as conn:
            query = text("""
                SELECT 
                    id, entidade_id, mes_referencia, repasse_oficio, repasse_periodo,
                    repasse_parcela, repasse_retencao, repasse_valor_final, repasse_vencimento,
                    repasse_pa, repasse_data_pagamento, prestacao_oficio, prestacao_data_entrega,
                    prestacao_pa, prestacao_sugestao_glosa, prestacao_reconsideracao, prestacao_mts
                FROM repasses_mensais
                WHERE entidade_id = :entidade_id
                ORDER BY TO_DATE(mes_referencia, 'MM.YYYY') DESC, mes_referencia DESC
            """)
            result = conn.execute(query, {"entidade_id": entidade_id})
            repasses = []
            for row in result:
                r = dict(row._mapping)
                if r.get("repasse_vencimento"):
                    r["repasse_vencimento"] = r["repasse_vencimento"].isoformat()
                if r.get("repasse_data_pagamento"):
                    r["repasse_data_pagamento"] = r["repasse_data_pagamento"].isoformat()
                if r.get("prestacao_data_entrega"):
                    r["prestacao_data_entrega"] = r["prestacao_data_entrega"].isoformat()
                r["id"] = str(r["id"])
                r["entidade_id"] = str(r["entidade_id"])
                for key in ["repasse_parcela", "repasse_retencao", "repasse_valor_final", "prestacao_sugestao_glosa", "prestacao_reconsideracao"]:
                    if r.get(key) is not None:
                        r[key] = float(r[key])
                repasses.append(r)
            return repasses

    except HTTPException as http_err:
        raise http_err
    except Exception as err:
        error_msg = safe_str_decode(err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar repasses: {error_msg}"
        )

@app.post("/api/entidades/{entidade_id}/repasses", status_code=status.HTTP_201_CREATED)
def create_repasse_individual(entidade_id: str, repasse: RepasseCreate):
    """
    Adiciona um novo repasse mensal a uma entidade existente.
    """
    if not engine:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Serviço de banco de dados não inicializado."
        )
    try:
        try:
            uuid.UUID(entidade_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de entidade inválido (deve ser UUID)."
            )

        with engine.begin() as conn:
            check_entidade = conn.execute(text("SELECT id FROM entidades WHERE id = :id"), {"id": entidade_id}).fetchone()
            if not check_entidade:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Entidade não encontrada."
                )

            query_insert = text("""
                INSERT INTO repasses_mensais (
                    entidade_id, mes_referencia, repasse_oficio, repasse_periodo,
                    repasse_parcela, repasse_retencao, repasse_valor_final, repasse_vencimento,
                    repasse_pa, repasse_data_pagamento, prestacao_oficio, prestacao_data_entrega,
                    prestacao_pa, prestacao_sugestao_glosa, prestacao_reconsideracao, prestacao_mts
                )
                VALUES (
                    :entidade_id, :mes_referencia, :repasse_oficio, :repasse_periodo,
                    :repasse_parcela, :repasse_retencao, :repasse_valor_final, :repasse_vencimento,
                    :repasse_pa, :repasse_data_pagamento, :prestacao_oficio, :prestacao_data_entrega,
                    :prestacao_pa, :prestacao_sugestao_glosa, :prestacao_reconsideracao, :prestacao_mts
                )
                RETURNING id;
            """)

            result = conn.execute(query_insert, {
                "entidade_id": entidade_id,
                "mes_referencia": repasse.mes_referencia.strip(),
                "repasse_oficio": repasse.repasse_oficio.strip() if repasse.repasse_oficio else None,
                "repasse_periodo": repasse.repasse_periodo.strip() if repasse.repasse_periodo else None,
                "repasse_parcela": repasse.repasse_parcela,
                "repasse_retencao": repasse.repasse_retencao,
                "repasse_valor_final": repasse.repasse_valor_final,
                "repasse_vencimento": repasse.repasse_vencimento.isoformat() if repasse.repasse_vencimento else None,
                "repasse_pa": repasse.repasse_pa.strip() if repasse.repasse_pa else None,
                "repasse_data_pagamento": repasse.repasse_data_pagamento.isoformat() if repasse.repasse_data_pagamento else None,
                "prestacao_oficio": repasse.prestacao_oficio.strip() if repasse.prestacao_oficio else None,
                "prestacao_data_entrega": repasse.prestacao_data_entrega.isoformat() if repasse.prestacao_data_entrega else None,
                "prestacao_pa": repasse.prestacao_pa.strip() if repasse.prestacao_pa else None,
                "prestacao_sugestao_glosa": repasse.prestacao_sugestao_glosa,
                "prestacao_reconsideracao": repasse.prestacao_reconsideracao,
                "prestacao_mts": repasse.prestacao_mts.strip() if repasse.prestacao_mts else None
            })

            new_repasse_id = result.fetchone()[0]
            return {
                "status": "success",
                "message": "Repasse mensal adicionado com sucesso!",
                "id": str(new_repasse_id)
            }

    except HTTPException as http_err:
        raise http_err
    except SQLAlchemyError as db_err:
        error_msg = safe_str_decode(db_err)
        if "unique constraint" in error_msg.lower() or "duplicar chave" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro de duplicidade: Já existe um lançamento de repasse para o mês de referência informado."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro de banco de dados: {error_msg}"
        )
    except Exception as err:
        error_msg = safe_str_decode(err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado no servidor: {error_msg}"
        )

@app.delete("/api/entidades/{entidade_id}", status_code=status.HTTP_200_OK)
def delete_entidade(entidade_id: str):
    """
    Exclui uma entidade cadastrada e todos os seus registros relacionados no banco de dados.
    """
    if not engine:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Serviço de banco de dados não inicializado."
        )
    try:
        try:
            uuid.UUID(entidade_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de entidade inválido (deve ser UUID)."
            )

        with engine.begin() as conn:
            check_exist = conn.execute(text("SELECT id FROM entidades WHERE id = :id"), {"id": entidade_id}).fetchone()
            if not check_exist:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Entidade não encontrada."
                )

            # A exclusão limpa dados_parceria e repasses_mensais em cascata no Postgres
            conn.execute(text("DELETE FROM entidades WHERE id = :id"), {"id": entidade_id})
            
            return {
                "status": "success",
                "message": "Entidade excluída com sucesso."
            }

    except HTTPException as http_err:
        raise http_err
    except Exception as err:
        error_msg = safe_str_decode(err)
        print(f"Erro ao excluir entidade: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir entidade: {error_msg}"
        )

def apply_excel_styles(worksheet):
    # Cabeçalhos: Fundo azul (#003366), Texto Branco, Negrito, Centralizado.
    header_fill = PatternFill(start_color="003366", end_color="003366", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    center_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    # Bordas
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    if worksheet.max_row < 1:
        return
        
    # Estilizar cabeçalhos
    for col in range(1, worksheet.max_column + 1):
        cell = worksheet.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_alignment
        cell.border = thin_border
        
    # Estilizar dados e ajustar largura
    for col in range(1, worksheet.max_column + 1):
        max_length = 0
        column_letter = get_column_letter(col)
        
        # Nome da coluna para identificar se é moeda
        header_value = str(worksheet.cell(row=1, column=col).value or "")
        is_currency = "(R$)" in header_value
        
        for row in range(1, worksheet.max_row + 1):
            cell = worksheet.cell(row=row, column=col)
            
            # Aplicar borda nas células com dados
            if row > 1:
                cell.border = thin_border
                
            # Formatar Moeda
            if row > 1 and is_currency:
                try:
                    if cell.value is not None and str(cell.value).strip() != "":
                        cell.value = float(cell.value)
                        cell.number_format = 'R$ #,##0.00'
                except ValueError:
                    pass

            try:
                if cell.value:
                    # Avaliar tamanho para largura, considerando formatação de moeda
                    val_str = f"R$ {cell.value:,.2f}" if (row > 1 and is_currency and isinstance(cell.value, (int, float))) else str(cell.value)
                    max_length = max(max_length, len(val_str))
            except:
                pass
        
        # Ajustar largura (+2 para margem)
        worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)

@app.get("/api/export/geral")
def export_geral():
    """
    Exporta todas as entidades cadastradas e seus repasses para um arquivo Excel com múltiplas abas.
    """
    if not engine:
        raise HTTPException(status_code=500, detail="Banco de dados não inicializado.")
    
    try:
        with engine.connect() as conn:
            # Busca todas as entidades e parcerias
            query = text("""
                SELECT e.*, 
                       p.ajuste_termo, p.inicio_atividades, p.termino_atividades, p.gestor_parceria,
                       p.projeto, p.categorias, p.atendimento_descricao, p.meta_mes_atendimentos,
                       p.responsavel_entidade, p.especialidades
                FROM entidades e
                LEFT JOIN dados_parceria p ON e.id = p.entidade_id
                ORDER BY e.razao_social ASC;
            """)
            result = conn.execute(query)
            
            formalizacoes = []
            parcerias = []
            financeiro_list = []
            
            for row in result:
                row_map = row._mapping
                entidade_id = row_map["id"]
                razao_social = row_map["razao_social"]
                cnpj = row_map["cnpj"]
                
                # 1. Dados de Formalização
                formalizacoes.append({
                    "Razão Social": razao_social,
                    "CNPJ": cnpj,
                    "PA Emenda": row_map["pa_emenda"] or "",
                    "PA Formalização": row_map["pa_formalizacao"] or "",
                    "Tipo de Instrumento": row_map["situacao"] or "",
                    "Número da Emenda": row_map["numero_emenda"] or "",
                    "Vereador Proponente": row_map["vereador"] or "",
                    "Valor Destinado (R$)": float(row_map["valor"]) if row_map["valor"] is not None else 0.0,
                    "Responsável Legal": row_map["responsavel_nome"] or "",
                    "Justificativa": row_map["justificativa"] or "",
                    "Histórico": row_map["historico"] or ""
                })
                
                # 2. Dados da Parceria
                if row_map["ajuste_termo"] or row_map["projeto"]:
                    parcerias.append({
                        "Razão Social": razao_social,
                        "CNPJ": cnpj,
                        "Ajuste / Termo": row_map["ajuste_termo"] or "",
                        "Gestor da Parceria": row_map["gestor_parceria"] or "",
                        "Projeto / Objeto": row_map["projeto"] or "",
                        "Início da Vigência": row_map["inicio_atividades"].strftime('%d/%m/%Y') if row_map["inicio_atividades"] else "",
                        "Término da Vigência": row_map["termino_atividades"].strftime('%d/%m/%Y') if row_map["termino_atividades"] else "",
                        "Meta Mensal Atendimentos": row_map["meta_mes_atendimentos"] or 0,
                        "Responsável Entidade": row_map["responsavel_entidade"] or ""
                    })
                
                # 3. Lançamentos Financeiros (Repasses e Prestações de Contas)
                repasses_query = text("""
                    SELECT * FROM repasses_mensais 
                    WHERE entidade_id = :entidade_id 
                    ORDER BY mes_referencia ASC
                """)
                repasses_res = conn.execute(repasses_query, {"entidade_id": entidade_id})
                
                for rep in repasses_res:
                    r = rep._mapping
                    financeiro_list.append({
                        "Razão Social": razao_social,
                        "CNPJ": cnpj,
                        "PA Empenho": row_map["pa_empenho"] or "",
                        "Código SCIM": row_map["cod_scim"] or "",
                        "Descrição do Objeto": row_map["objeto_descricao"] or "",
                        "Mês Referência": r["mes_referencia"] or "",
                        "Valor Parcela (R$)": float(r["repasse_parcela"]) if r["repasse_parcela"] is not None else 0.0,
                        "Retenções (R$)": float(r["repasse_retencao"]) if r["repasse_retencao"] is not None else 0.0,
                        "Valor Líquido (R$)": float(r["repasse_valor_final"]) if r["repasse_valor_final"] is not None else 0.0,
                        "Data Vencimento": r["repasse_vencimento"].strftime('%d/%m/%Y') if r["repasse_vencimento"] else "",
                        "PA Repasse": r["repasse_pa"] or "",
                        "Data Pagamento": r["repasse_data_pagamento"].strftime('%d/%m/%Y') if r["repasse_data_pagamento"] else "",
                        "Ofício Prestação": r["prestacao_oficio"] or "",
                        "Data Entrega Prestação": r["prestacao_data_entrega"].strftime('%d/%m/%Y') if r["prestacao_data_entrega"] else "",
                        "PA Prestação": r["prestacao_pa"] or "",
                        "Sugestão Glosa (R$)": float(r["prestacao_sugestao_glosa"]) if r["prestacao_sugestao_glosa"] is not None else 0.0,
                        "Reconsideração Glosa (R$)": float(r["prestacao_reconsideracao"]) if r["prestacao_reconsideracao"] is not None else 0.0,
                        "Manifestação MTS": r["prestacao_mts"] or ""
                    })

            # Cria os DataFrames
            df_formalizacoes = pd.DataFrame(formalizacoes)
            df_parcerias = pd.DataFrame(parcerias)
            df_financeiro = pd.DataFrame(financeiro_list)

            # Grava no buffer BytesIO
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                if not df_formalizacoes.empty:
                    df_formalizacoes.to_excel(writer, sheet_name="Formalização", index=False)
                else:
                    pd.DataFrame(columns=["Sem dados"]).to_excel(writer, sheet_name="Formalização", index=False)
                
                if not df_parcerias.empty:
                    df_parcerias.to_excel(writer, sheet_name="Dados da Parceria", index=False)
                else:
                    pd.DataFrame(columns=["Sem dados"]).to_excel(writer, sheet_name="Dados da Parceria", index=False)
                
                if not df_financeiro.empty:
                    df_financeiro.to_excel(writer, sheet_name="Controle Financeiro", index=False)
                else:
                    pd.DataFrame(columns=["Sem dados"]).to_excel(writer, sheet_name="Controle Financeiro", index=False)

                for sheet in writer.sheets.values():
                    apply_excel_styles(sheet)

            output.seek(0)
            
            headers = {
                'Content-Disposition': 'attachment; filename="Prefinance_Exportacao_Geral.xlsx"'
            }
            return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
            
    except Exception as e:
        error_msg = safe_str_decode(e)
        raise HTTPException(status_code=500, detail=f"Erro ao exportar dados consolidados: {error_msg}")

@app.get("/api/export/entidade/{entidade_id}")
def export_entidade(entidade_id: str, etapa: str = "todos"):
    """
    Exporta dados de uma entidade específica filtrado pela etapa.
    """
    if not engine:
        raise HTTPException(status_code=500, detail="Banco de dados não inicializado.")
    
    try:
        try:
            uuid.UUID(entidade_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="ID de entidade inválido (deve ser UUID).")

        with engine.connect() as conn:
            query = text("""
                SELECT e.*, 
                       p.ajuste_termo, p.inicio_atividades, p.termino_atividades, p.gestor_parceria,
                       p.projeto, p.categorias, p.atendimento_descricao, p.meta_mes_atendimentos,
                       p.responsavel_entidade, p.especialidades
                FROM entidades e
                LEFT JOIN dados_parceria p ON e.id = p.entidade_id
                WHERE e.id = :id;
            """)
            row = conn.execute(query, {"id": entidade_id}).fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Entidade não encontrada.")
                
            row_map = row._mapping
            razao_social = row_map["razao_social"]
            cnpj = row_map["cnpj"]
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                
                # 1. Formalização
                if etapa in ("todos", "formalizacao"):
                    data_formalizacao = [{
                        "Razão Social": razao_social,
                        "CNPJ": cnpj,
                        "PA Emenda": row_map["pa_emenda"] or "",
                        "PA Formalização": row_map["pa_formalizacao"] or "",
                        "Tipo de Instrumento": row_map["situacao"] or "",
                        "Número da Emenda": row_map["numero_emenda"] or "",
                        "Vereador Proponente": row_map["vereador"] or "",
                        "Valor Destinado (R$)": float(row_map["valor"]) if row_map["valor"] is not None else 0.0,
                        "Responsável Legal": row_map["responsavel_nome"] or "",
                        "Justificativa": row_map["justificativa"] or "",
                        "Histórico": row_map["historico"] or ""
                    }]
                    pd.DataFrame(data_formalizacao).to_excel(writer, sheet_name="Formalização", index=False)
                
                # 2. Dados da Parceria
                if etapa in ("todos", "parceria"):
                    data_parceria = [{
                        "Razão Social": razao_social,
                        "CNPJ": cnpj,
                        "Ajuste / Termo": row_map["ajuste_termo"] or "",
                        "Gestor da Parceria": row_map["gestor_parceria"] or "",
                        "Projeto / Objeto": row_map["projeto"] or "",
                        "Início da Vigência": row_map["inicio_atividades"].strftime('%d/%m/%Y') if row_map["inicio_atividades"] else "",
                        "Término da Vigência": row_map["termino_atividades"].strftime('%d/%m/%Y') if row_map["termino_atividades"] else "",
                        "Meta Mensal Atendimentos": row_map["meta_mes_atendimentos"] or 0,
                        "Responsável Entidade": row_map["responsavel_entidade"] or ""
                    }]
                    pd.DataFrame(data_parceria).to_excel(writer, sheet_name="Dados da Parceria", index=False)
                
                # 3. Controle Financeiro / Repasses
                if etapa in ("todos", "financeiro"):
                    repasses_query = text("""
                        SELECT * FROM repasses_mensais 
                        WHERE entidade_id = :entidade_id 
                        ORDER BY mes_referencia ASC
                    """)
                    repasses_res = conn.execute(repasses_query, {"entidade_id": entidade_id})
                    
                    financeiro_list = []
                    for rep in repasses_res:
                        r = rep._mapping
                        financeiro_list.append({
                            "Razão Social": razao_social,
                            "CNPJ": cnpj,
                            "PA Empenho": row_map["pa_empenho"] or "",
                            "Código SCIM": row_map["cod_scim"] or "",
                            "Descrição do Objeto": row_map["objeto_descricao"] or "",
                            "Mês Referência": r["mes_referencia"] or "",
                            "Valor Parcela (R$)": float(r["repasse_parcela"]) if r["repasse_parcela"] is not None else 0.0,
                            "Retenções (R$)": float(r["repasse_retencao"]) if r["repasse_retencao"] is not None else 0.0,
                            "Valor Líquido (R$)": float(r["repasse_valor_final"]) if r["repasse_valor_final"] is not None else 0.0,
                            "Data Vencimento": r["repasse_vencimento"].strftime('%d/%m/%Y') if r["repasse_vencimento"] else "",
                            "PA Repasse": r["repasse_pa"] or "",
                            "Data Pagamento": r["repasse_data_pagamento"].strftime('%d/%m/%Y') if r["repasse_data_pagamento"] else "",
                            "Ofício Prestação": r["prestacao_oficio"] or "",
                            "Data Entrega Prestação": r["prestacao_data_entrega"].strftime('%d/%m/%Y') if r["prestacao_data_entrega"] else "",
                            "PA Prestação": r["prestacao_pa"] or "",
                            "Sugestão Glosa (R$)": float(r["prestacao_sugestao_glosa"]) if r["prestacao_sugestao_glosa"] is not None else 0.0,
                            "Reconsideração Glosa (R$)": float(r["prestacao_reconsideracao"]) if r["prestacao_reconsideracao"] is not None else 0.0,
                            "Manifestação MTS": r["prestacao_mts"] or ""
                        })
                    if not financeiro_list:
                        # Se não há repasses ainda, adiciona linha básica vazia apenas com cabeçalho da entidade
                        financeiro_list.append({
                            "Razão Social": razao_social,
                            "CNPJ": cnpj,
                            "PA Empenho": row_map["pa_empenho"] or "",
                            "Código SCIM": row_map["cod_scim"] or "",
                            "Descrição do Objeto": row_map["objeto_descricao"] or "",
                            "Mês Referência": "",
                            "Valor Parcela (R$)": 0.0,
                            "Retenções (R$)": 0.0,
                            "Valor Líquido (R$)": 0.0,
                            "Data Vencimento": "",
                            "PA Repasse": "",
                            "Data Pagamento": "",
                            "Ofício Prestação": "",
                            "Data Entrega Prestação": "",
                            "PA Prestação": "",
                            "Sugestão Glosa (R$)": 0.0,
                            "Reconsideração Glosa (R$)": 0.0,
                            "Manifestação MTS": ""
                        })
                    pd.DataFrame(financeiro_list).to_excel(writer, sheet_name="Controle Financeiro", index=False)

                for sheet in writer.sheets.values():
                    apply_excel_styles(sheet)

            output.seek(0)
            
            nome_arq = f"Prefinance_Exportacao_{razao_social.replace(' ', '_')}_{etapa}.xlsx"
            headers = {
                'Content-Disposition': f'attachment; filename="{nome_arq}"'
            }
            return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
            
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        error_msg = safe_str_decode(e)
        raise HTTPException(status_code=500, detail=f"Erro ao exportar dados da entidade: {error_msg}")

@app.post("/api/export/dados")
def export_dados(dados: dict, etapa: str = "todos"):
    """
    Exporta os dados enviados diretamente no corpo da requisição para um arquivo Excel (rascunho).
    """
    def format_date_str(date_str):
        if not date_str or not isinstance(date_str, str):
            return ""
        parts = date_str.split('-')
        if len(parts) == 3 and len(parts[0]) == 4:
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
        return date_str

    try:
        razao_social = dados.get("razao_social") or "Nova Parceria"
        cnpj = dados.get("cnpj") or ""
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            
            # 1. Formalização
            if etapa in ("todos", "formalizacao"):
                val_destinado = dados.get("valor")
                try:
                    val_destinado = float(val_destinado) if val_destinado is not None and str(val_destinado).strip() != "" else 0.0
                except (ValueError, TypeError):
                    val_destinado = 0.0
                    
                data_formalizacao = [{
                    "Razão Social": razao_social,
                    "CNPJ": cnpj,
                    "PA Emenda": dados.get("pa_emenda") or "",
                    "PA Formalização": dados.get("pa_formalizacao") or "",
                    "Tipo de Instrumento": dados.get("situacao") or "",
                    "Número da Emenda": dados.get("numero_emenda") or "",
                    "Vereador Proponente": dados.get("vereador") or "",
                    "Valor Destinado (R$)": val_destinado,
                    "Responsável Legal": dados.get("responsavel_nome") or "",
                    "Justificativa": dados.get("justificativa") or "",
                    "Histórico": dados.get("historico") or ""
                }]
                pd.DataFrame(data_formalizacao).to_excel(writer, sheet_name="Formalização", index=False)
            
            # 2. Dados da Parceria
            if etapa in ("todos", "parceria"):
                ajuste_termo = ""
                gestor_parceria = ""
                projeto = ""
                inicio_atividades = ""
                termino_atividades = ""
                meta_mes_atendimentos = 0
                responsavel_entidade = ""
                
                parceria = dados.get("parceria")
                if isinstance(parceria, dict):
                    ajuste_termo = parceria.get("ajuste_termo") or ""
                    gestor_parceria = parceria.get("gestor_parceria") or ""
                    projeto = parceria.get("projeto") or ""
                    inicio_atividades = format_date_str(parceria.get("inicio_atividades"))
                    termino_atividades = format_date_str(parceria.get("termino_atividades"))
                    try:
                        meta_mes_atendimentos = int(parceria.get("meta_mes_atendimentos")) if parceria.get("meta_mes_atendimentos") is not None else 0
                    except (ValueError, TypeError):
                        meta_mes_atendimentos = 0
                    responsavel_entidade = parceria.get("responsavel_entidade") or ""
                
                data_parceria = [{
                    "Razão Social": razao_social,
                    "CNPJ": cnpj,
                    "Ajuste / Termo": ajuste_termo,
                    "Gestor da Parceria": gestor_parceria,
                    "Projeto / Objeto": projeto,
                    "Início da Vigência": inicio_atividades,
                    "Término da Vigência": termino_atividades,
                    "Meta Mensal Atendimentos": meta_mes_atendimentos,
                    "Responsável Entidade": responsavel_entidade
                }]
                pd.DataFrame(data_parceria).to_excel(writer, sheet_name="Dados da Parceria", index=False)
            
            # 3. Controle Financeiro / Repasses
            if etapa in ("todos", "financeiro"):
                financeiro_list = []
                repasses = dados.get("repasses")
                if isinstance(repasses, list):
                    for rep in repasses:
                        if isinstance(rep, dict):
                            try:
                                v_parc = float(rep.get("repasse_parcela")) if rep.get("repasse_parcela") is not None and str(rep.get("repasse_parcela")).strip() != "" else 0.0
                            except (ValueError, TypeError):
                                v_parc = 0.0
                            try:
                                v_ret = float(rep.get("repasse_retencao")) if rep.get("repasse_retencao") is not None and str(rep.get("repasse_retencao")).strip() != "" else 0.0
                            except (ValueError, TypeError):
                                v_ret = 0.0
                            try:
                                v_liq = float(rep.get("repasse_valor_final")) if rep.get("repasse_valor_final") is not None and str(rep.get("repasse_valor_final")).strip() != "" else 0.0
                            except (ValueError, TypeError):
                                v_liq = 0.0
                            try:
                                v_glosa = float(rep.get("prestacao_sugestao_glosa")) if rep.get("prestacao_sugestao_glosa") is not None and str(rep.get("prestacao_sugestao_glosa")).strip() != "" else 0.0
                            except (ValueError, TypeError):
                                v_glosa = 0.0
                            try:
                                v_recons = float(rep.get("prestacao_reconsideracao")) if rep.get("prestacao_reconsideracao") is not None and str(rep.get("prestacao_reconsideracao")).strip() != "" else 0.0
                            except (ValueError, TypeError):
                                v_recons = 0.0
                                
                            financeiro_list.append({
                                "Razão Social": razao_social,
                                "CNPJ": cnpj,
                                "PA Empenho": dados.get("pa_empenho") or "",
                                "Código SCIM": dados.get("cod_scim") or "",
                                "Descrição do Objeto": dados.get("objeto_descricao") or "",
                                "Mês Referência": rep.get("mes_referencia") or "",
                                "Valor Parcela (R$)": v_parc,
                                "Retenções (R$)": v_ret,
                                "Valor Líquido (R$)": v_liq,
                                "Data Vencimento": format_date_str(rep.get("repasse_vencimento")),
                                "PA Repasse": rep.get("repasse_pa") or "",
                                "Data Pagamento": format_date_str(rep.get("repasse_data_pagamento")),
                                "Ofício Prestação": rep.get("prestacao_oficio") or "",
                                "Data Entrega Prestação": format_date_str(rep.get("prestacao_data_entrega")),
                                "PA Prestação": rep.get("prestacao_pa") or "",
                                "Sugestão Glosa (R$)": v_glosa,
                                "Reconsideração Glosa (R$)": v_recons,
                                "Manifestação MTS": rep.get("prestacao_mts") or ""
                            })
                
                if not financeiro_list:
                    financeiro_list.append({
                        "Razão Social": razao_social,
                        "CNPJ": cnpj,
                        "PA Empenho": dados.get("pa_empenho") or "",
                        "Código SCIM": dados.get("cod_scim") or "",
                        "Descrição do Objeto": dados.get("objeto_descricao") or "",
                        "Mês Referência": "",
                        "Valor Parcela (R$)": 0.0,
                        "Retenções (R$)": 0.0,
                        "Valor Líquido (R$)": 0.0,
                        "Data Vencimento": "",
                        "PA Repasse": "",
                        "Data Pagamento": "",
                        "Ofício Prestação": "",
                        "Data Entrega Prestação": "",
                        "PA Prestação": "",
                        "Sugestão Glosa (R$)": 0.0,
                        "Reconsideração Glosa (R$)": 0.0,
                        "Manifestação MTS": ""
                    })
                pd.DataFrame(financeiro_list).to_excel(writer, sheet_name="Controle Financeiro", index=False)

            for sheet in writer.sheets.values():
                apply_excel_styles(sheet)
 
        output.seek(0)
        
        nome_arq = f"Prefinance_Exportacao_{razao_social.replace(' ', '_')}_{etapa}.xlsx"
        headers = {
            'Content-Disposition': f'attachment; filename="{nome_arq}"'
        }
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
        
    except Exception as e:
        error_msg = safe_str_decode(e)
        raise HTTPException(status_code=500, detail=f"Erro ao exportar dados temporários: {error_msg}")

if __name__ == "__main__":
    import uvicorn
    # Inicia o servidor uvicorn na porta 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
