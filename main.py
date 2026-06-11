import os
os.environ["PGCLIENTENCODING"] = "utf-8"

import uuid
import json
from datetime import date
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, status
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

if __name__ == "__main__":
    import uvicorn
    # Inicia o servidor uvicorn na porta 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
