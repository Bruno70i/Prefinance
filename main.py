import os
os.environ["PGCLIENTENCODING"] = "utf-8"

import uuid
import json
from datetime import date
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, status, UploadFile, File, Response, Request, Depends
from fastapi.responses import StreamingResponse
import io
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import excel_modelo
from validadores import validar_cnpj, apenas_digitos, validar_cpf, parse_cnpj
import ia_contexto
import ollama_service
import import_planilha
import auth

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

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = exc.errors()
    mensagens = []
    for err in errors:
        loc_list = err.get("loc", [])
        # Remove a palavra 'body' do início do caminho de erro se for do payload de request
        if loc_list and loc_list[0] == "body":
            loc_list = loc_list[1:]
        loc = " -> ".join(str(l) for l in loc_list)
        msg = err.get("msg", "Erro de validação")
        # Limpa o prefixo do erro de Pydantic
        if "Value error, " in msg:
            msg = msg.replace("Value error, ", "")
        
        if loc:
            mensagens.append(f"{loc}: {msg}")
        else:
            mensagens.append(msg)
            
    msg_final = "; ".join(mensagens)
    return JSONResponse(
        status_code=400,
        content={"detail": f"Erro de validação: {msg_final}"}
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
    meta_mes_atendimentos: Optional[str] = Field(None, description="Meta mensal total de atendimentos da parceria")
    responsavel_entidade: Optional[str] = Field(None, description="Responsável pela entidade na parceria")
    especialidades: Optional[Dict[str, int]] = Field(default_factory=dict, description="Especialidades e metas individuais associadas")

    @model_validator(mode="after")
    def _validar_vigencia(self):
        if self.inicio_atividades and self.termino_atividades:
            if self.inicio_atividades > self.termino_atividades:
                raise ValueError("A data de início não pode ser posterior à data de término.")
        return self

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

    @field_validator("mes_referencia")
    @classmethod
    def _formato_mes(cls, v: str) -> str:
        import re
        if v and not re.fullmatch(r"\d{2}\.\d{4}", v.strip()):
            raise ValueError("mes_referencia deve estar no formato MM.AAAA (ex.: 01.2026).")
        return v.strip()

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

    @model_validator(mode="after")
    def _validar_extras(self):
        import re
        from validadores import apenas_digitos, validar_cpf
        
        extras = self.configuracoes_extras or {}
        
        # 1. Validação de E-mail
        email = extras.get("email_contato")
        if email:
            email_str = str(email).strip()
            if not re.fullmatch(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email_str):
                raise ValueError("E-mail institucional com formato inválido.")
                
        # 2. Validação de Telefone
        telefone = extras.get("telefone")
        if telefone:
            tel_digitos = apenas_digitos(str(telefone))
            if tel_digitos and len(tel_digitos) not in (10, 11):
                raise ValueError("O telefone deve conter exatamente 10 ou 11 dígitos.")
                
        # 3. Validação de CPF do Representante
        cpf_rep = extras.get("cpf_representante")
        if cpf_rep:
            cpf_digitos = apenas_digitos(str(cpf_rep))
            if cpf_digitos and not validar_cpf(cpf_digitos):
                raise ValueError("CPF do representante legal inválido.")
                
        return self

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

class ChatRequest(BaseModel):
    pergunta: str = Field(..., min_length=1, description="Pergunta do usuário")
    historico: Optional[List[Dict[str, str]]] = Field(default_factory=list,
        description="Mensagens anteriores [{role:'user'|'assistant', content:'...'}]")
    contexto_planilha: Optional[str] = Field(default=None, description="Texto vindo da planilha de upload")

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

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    senha: str = Field(..., min_length=1)

class UsuarioCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    nome: str = Field(..., min_length=1, max_length=160)
    senha: str = Field(..., min_length=4)
    ativo: bool = True

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    senha: Optional[str] = None     # se vier preenchida, redefine a senha (recuperação)
    ativo: Optional[bool] = None

@app.get("/")
def read_root():
    return {"status": "online", "message": "PreFinance API Backend está ativo."}

# --- Rotas de Autenticação ---
@app.post("/api/auth/login")
def login(req: LoginRequest, response: Response):
    if auth.autenticar_admin_env(req.username, req.senha):
        token = auth.criar_token({"sub": req.username, "nome": req.username, "papel": "admin"})
    else:
        with engine.connect() as conn:
            row = conn.execute(text(
                "SELECT username, nome, senha_hash, ativo FROM usuarios WHERE username = :u"
            ), {"u": req.username}).fetchone()
        if (not row) or (not row.ativo) or (not auth.verificar_senha(req.senha, row.senha_hash)):
            raise HTTPException(status_code=401, detail="Usuário ou senha inválidos.")
        token = auth.criar_token({"sub": row.username, "nome": row.nome, "papel": "usuario"})
        try:
            with engine.begin() as conn:
                conn.execute(text("UPDATE usuarios SET ultimo_login = CURRENT_TIMESTAMP WHERE username = :u"),
                             {"u": req.username})
        except Exception:
            pass

    response.set_cookie("access_token", token, httponly=True, samesite="lax",
                        max_age=auth.TOKEN_HORAS * 3600, path="/")
    return {"ok": True}

@app.get("/api/auth/me")
def me(usuario: dict = Depends(auth.get_current_user)):
    return {"username": usuario["sub"], "nome": usuario.get("nome"), "papel": usuario.get("papel")}

@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"ok": True}

# --- CRUD de Usuários (Admin) ---
@app.get("/api/admin/usuarios")
def listar_usuarios(admin: dict = Depends(auth.get_current_admin)):
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT id, username, nome, ativo, criado_em, ultimo_login
            FROM usuarios ORDER BY nome
        """)).fetchall()
    return [{
        "id": str(r.id), "username": r.username, "nome": r.nome, "ativo": r.ativo,
        "criado_em": r.criado_em.isoformat() if r.criado_em else None,
        "ultimo_login": r.ultimo_login.isoformat() if r.ultimo_login else None,
    } for r in rows]

@app.post("/api/admin/usuarios", status_code=status.HTTP_201_CREATED)
def criar_usuario(req: UsuarioCreate, admin: dict = Depends(auth.get_current_admin)):
    if req.username.strip().lower() == auth.ADMIN_LOGIN.lower():
        raise HTTPException(status_code=400, detail="Esse nome de usuário é reservado ao administrador.")
    senha_hash = auth.gerar_hash_senha(req.senha)
    try:
        with engine.begin() as conn:
            row = conn.execute(text("""
                INSERT INTO usuarios (username, nome, senha_hash, ativo)
                VALUES (:u, :n, :h, :a) RETURNING id
            """), {"u": req.username.strip(), "n": req.nome.strip(), "h": senha_hash, "a": req.ativo}).fetchone()
        return {"id": str(row.id), "ok": True}
    except SQLAlchemyError as e:
        if "unique" in str(e).lower():
            raise HTTPException(status_code=409, detail="Já existe um usuário com esse username.")
        raise HTTPException(status_code=500, detail="Erro ao criar usuário.")

@app.put("/api/admin/usuarios/{user_id}")
def atualizar_usuario(user_id: str, req: UsuarioUpdate, admin: dict = Depends(auth.get_current_admin)):
    campos, params = [], {"id": user_id}
    if req.nome is not None:
        campos.append("nome = :n"); params["n"] = req.nome.strip()
    if req.ativo is not None:
        campos.append("ativo = :a"); params["a"] = req.ativo
    if req.senha:
        campos.append("senha_hash = :h"); params["h"] = auth.gerar_hash_senha(req.senha)
    if not campos:
        return {"ok": True}
    with engine.begin() as conn:
        res = conn.execute(text(f"UPDATE usuarios SET {', '.join(campos)} WHERE id = :id"), params)
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return {"ok": True}

@app.delete("/api/admin/usuarios/{user_id}")
def excluir_usuario(user_id: str, admin: dict = Depends(auth.get_current_admin)):
    with engine.begin() as conn:
        res = conn.execute(text("DELETE FROM usuarios WHERE id = :id"), {"id": user_id})
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return {"ok": True}

@app.get("/api/entidades")
def get_entidades(usuario: dict = Depends(auth.get_current_user)):
    """
    Lista todas as entidades cadastradas.
    """
    if not engine:
        raise HTTPException(status_code=500, detail="Banco de dados não inicializado.")
    
    try:
        with engine.begin() as conn:
            query = text("""
                SELECT id, razao_social, cnpj, responsavel_nome, situacao, numero_emenda, valor, configuracoes_extras, created_at, criado_por 
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
                    "configuracoes_extras": row.configuracoes_extras,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "criado_por": row.criado_por
                })
            return entidades
    except Exception as e:
        error_msg = safe_str_decode(e)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar entidades: {error_msg}")

@app.post("/api/entidades", status_code=status.HTTP_201_CREATED)
def create_entidade(entidade: EntidadeCreate, usuario: dict = Depends(auth.get_current_user)):
    """
    Endpoint para inserção de uma nova entidade no banco de dados PostgreSQL.
    """
    if not engine:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Serviço de banco de dados não inicializado. Verifique as configurações de ambiente."
        )

    if entidade.repasses:
        soma = sum(float(r.repasse_parcela or 0) for r in entidade.repasses)
        total = float(entidade.valor or 0)
        if total > 0 and abs(soma - total) > 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A soma das parcelas ({soma:.2f}) difere do valor total ({total:.2f})."
            )

    # Preparação dos dados para inserção
    try:
        extras_json = json.dumps(entidade.configuracoes_extras) if entidade.configuracoes_extras else json.dumps({})
        
        with engine.begin() as conn:
            _cnpj_digitos = apenas_digitos(entidade.cnpj or "")
            if _cnpj_digitos:
                if not validar_cnpj(_cnpj_digitos):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CNPJ inválido (dígito verificador não confere).")
                dup = conn.execute(text("""
                    SELECT razao_social FROM entidades
                    WHERE regexp_replace(cnpj, '\\D', '', 'g') = :d LIMIT 1
                """), {"d": _cnpj_digitos}).fetchone()
                if dup:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"CNPJ já cadastrado para: {dup.razao_social}")

            _cnpj_raiz = _cnpj_digitos[0:8] if len(_cnpj_digitos) == 14 else None
            _cnpj_ordem = _cnpj_digitos[8:12] if len(_cnpj_digitos) == 14 else None

            _extras = entidade.configuracoes_extras or {}
            _cpf_rep = apenas_digitos(str(_extras.get("cpf_representante") or "")) or None
            _telefone = apenas_digitos(str(_extras.get("telefone") or "")) or None

            # Executa a inserção retornando o id gerado
            query_insert = text("""
                INSERT INTO entidades (
                    razao_social, cnpj, responsavel_nome, situacao, historico, 
                    pa_emenda, localizacao_pa_emenda, emenda_alterada, pa_formalizacao, 
                    numero_emenda, vereador, justificativa, valor, cod_scim, pa_empenho, 
                    objeto_descricao, configuracoes_extras,
                    cpf_representante, telefone, cnpj_raiz, cnpj_ordem, criado_por
                )
                VALUES (
                    :razao_social, :cnpj, :responsavel, :situacao, :historico, 
                    :pa_emenda, :localizacao_pa_emenda, :emenda_alterada, :pa_formalizacao, 
                    :numero_emenda, :vereador, :justificativa, :valor, :cod_scim, :pa_empenho, 
                    :objeto_descricao, :extras,
                    :cpf_representante, :telefone, :cnpj_raiz, :cnpj_ordem, :criado_por
                )
                RETURNING id;
            """)
            
            result = conn.execute(query_insert, {
                "razao_social": entidade.razao_social.strip(),
                "cnpj": _cnpj_digitos if _cnpj_digitos else None,
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
                "extras": extras_json,
                "cpf_representante": _cpf_rep,
                "telefone": _telefone,
                "cnpj_raiz": _cnpj_raiz,
                "cnpj_ordem": _cnpj_ordem,
                "criado_por": usuario.get("nome") or usuario.get("sub")
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

@app.get("/api/entidades/check-cnpj")
def check_cnpj(cnpj: str, ignorar_id: str | None = None, usuario: dict = Depends(auth.get_current_user)):
    """Retorna se o CNPJ já existe e, em caso afirmativo, qual entidade o possui."""
    if not engine:
        raise HTTPException(status_code=500, detail="Banco de dados não inicializado.")
    digitos = apenas_digitos(cnpj)
    resposta = {"existe": False, "valido": validar_cnpj(digitos), "entidade_id": None, "razao_social": None}
    if len(digitos) != 14:
        return resposta
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT id, razao_social FROM entidades
            WHERE regexp_replace(cnpj, '\\D', '', 'g') = :d
              AND (:ignorar_id IS NULL OR id <> :ignorar_id)
            LIMIT 1
        """), {"d": digitos, "ignorar_id": ignorar_id}).fetchone()
        if row:
            resposta["existe"] = True
            resposta["entidade_id"] = str(row.id)
            resposta["razao_social"] = row.razao_social
    return resposta

@app.get("/api/representantes/check-cpf")
def check_cpf(cpf: str, ignorar_id: str | None = None, usuario: dict = Depends(auth.get_current_user)):
    """
    Lista as entidades em que o CPF já é representante e agrega totais.
    NÃO bloqueia nada — é informativo. `ignorar_id` exclui a própria entidade (modo edição).
    """
    if not engine:
        raise HTTPException(status_code=500, detail="Banco de dados não inicializado.")
    digitos = apenas_digitos(cpf)
    resp = {
        "valido": validar_cpf(digitos),
        "total_empresas": 0,
        "total_repassado": 0.0,
        "empresas": [],
    }
    if len(digitos) != 11:
        return resp

    with engine.connect() as conn:
        params = {"cpf": digitos}
        filtro_id = ""
        if ignorar_id:
            filtro_id = "AND e.id <> :ignorar_id"
            params["ignorar_id"] = ignorar_id

        # Empresas dessa pessoa + valor total de cada parceria
        rows = conn.execute(text(f"""
            SELECT e.id, e.razao_social, e.cnpj,
                   COALESCE(e.valor, 0) AS total_pago
            FROM entidades e
            WHERE e.cpf_representante = :cpf {filtro_id}
            ORDER BY e.razao_social
        """), params).fetchall()

        empresas = []
        total_geral = 0.0
        for row in rows:
            total_geral += float(row.total_pago or 0)
            empresas.append({
                "entidade_id": str(row.id),
                "razao_social": row.razao_social,
                "cnpj": row.cnpj,
                "total_repassado": float(row.total_pago or 0),
            })
        resp["empresas"] = empresas
        resp["total_empresas"] = len(empresas)
        resp["total_repassado"] = total_geral
    return resp

@app.get("/api/entidades/por-raiz/{raiz}")
def entidades_por_raiz(raiz: str, usuario: dict = Depends(auth.get_current_user)):
    """Lista todos os estabelecimentos (matriz + filiais) de uma mesma raiz de CNPJ."""
    if not engine:
        raise HTTPException(status_code=500, detail="Banco de dados não inicializado.")
    raiz_digitos = "".join(ch for ch in (raiz or "") if ch.isdigit())[:8]
    if len(raiz_digitos) != 8:
        return {"raiz": raiz_digitos, "estabelecimentos": []}
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT id, razao_social, cnpj, cnpj_ordem
            FROM entidades
            WHERE cnpj_raiz = :raiz
            ORDER BY cnpj_ordem
        """), {"raiz": raiz_digitos}).fetchall()
    return {
        "raiz": raiz_digitos,
        "estabelecimentos": [
            {
                "entidade_id": str(r.id),
                "razao_social": r.razao_social,
                "cnpj": r.cnpj,
                "ordem": r.cnpj_ordem,
                "tipo": "MATRIZ" if r.cnpj_ordem == "0001" else "FILIAL",
            } for r in rows
        ],
    }

@app.get("/api/entidades/check-razao")
def check_razao(nome: str, ignorar_id: str | None = None, usuario: dict = Depends(auth.get_current_user)):
    """
    Busca por razões sociais muito parecidas para alertar o usuário (pg_trgm ou ILIKE).
    `ignorar_id` é usado para excluir a própria entidade em edição.
    """
    if not engine:
        raise HTTPException(status_code=500, detail="Banco de dados não inicializado.")
    
    nome_limpo = nome.strip()
    if not nome_limpo:
        return {"duplicatas": []}
        
    with engine.connect() as conn:
        try:
            # 1. Tenta usar similaridade do pg_trgm
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            query = text("""
                SELECT id, razao_social, cnpj, similarity(razao_social, :nome) AS sim
                FROM entidades
                WHERE similarity(razao_social, :nome) > 0.4
                  AND (:ignorar_id IS NULL OR id <> :ignorar_id)
                ORDER BY sim DESC
                LIMIT 5;
            """)
            rows = conn.execute(query, {"nome": nome_limpo, "ignorar_id": ignorar_id}).fetchall()
            duplicatas = [
                {
                    "entidade_id": str(r.id),
                    "razao_social": r.razao_social,
                    "cnpj": r.cnpj,
                    "similaridade": float(r.sim)
                } for r in rows
            ]
            return {"duplicatas": duplicatas}
        except Exception as e:
            # Fallback para busca ILIKE caso falhe pg_trgm por falta de permissão ou suporte
            print(f"pg_trgm falhou, usando fallback ILIKE: {e}")
            query = text("""
                SELECT id, razao_social, cnpj
                FROM entidades
                WHERE razao_social ILIKE :nome_like
                  AND (:ignorar_id IS NULL OR id <> :ignorar_id)
                LIMIT 5;
            """)
            rows = conn.execute(query, {"nome_like": f"%{nome_limpo}%", "ignorar_id": ignorar_id}).fetchall()
            duplicatas = [
                {
                    "entidade_id": str(r.id),
                    "razao_social": r.razao_social,
                    "cnpj": r.cnpj,
                    "similaridade": 0.5
                } for r in rows
            ]
            return {"duplicatas": duplicatas}

@app.post("/api/admin/normalizar-competencias")
def normalizar_competencias(admin: dict = Depends(auth.get_current_admin)):
    """Normaliza o campo mes_referencia de repasses_mensais antigos para MM.AAAA."""
    if not engine:
        raise HTTPException(status_code=500, detail="Banco de dados não inicializado.")
    
    meses_mapeamento = {
        'janeiro': '01', 'fevereiro': '02', 'marco': '03', 'março': '03', 'abril': '04', 'maio': '05', 'junho': '06',
        'julho': '07', 'agosto': '08', 'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12',
        'january': '01', 'february': '02', 'march': '03', 'april': '04', 'may': '05', 'june': '06',
        'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11', 'december': '12',
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'jun': '06',
        'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
    }

    def normalizar_competencia(valor: str) -> str:
        if not valor:
            return valor
        v = valor.strip().lower()
        if re.fullmatch(r"\d{2}\.\d{4}", v):
            return v
        partes = re.split(r"[\/\-\.\s]+", v)
        if len(partes) != 2:
            return valor
        p1, p2 = partes[0], partes[1]
        mes, ano = "", ""
        if p2.isdigit() and len(p2) in (2, 4):
            ano = p2 if len(p2) == 4 else f"20{p2}"
            if p1 in meses_mapeamento:
                mes = meses_mapeamento[p1]
            elif p1.isdigit():
                mes = p1.zfill(2)
        elif p1.isdigit() and len(p1) in (2, 4):
            ano = p1 if len(p1) == 4 else f"20{p1}"
            if p2 in meses_mapeamento:
                mes = meses_mapeamento[p2]
            elif p2.isdigit():
                mes = p2.zfill(2)
        if mes and ano and len(mes) == 2 and len(ano) == 4:
            return f"{mes}.{ano}"
        return valor

    import re
    try:
        with engine.begin() as conn:
            rows = conn.execute(text("SELECT id, mes_referencia FROM repasses_mensais")).fetchall()
            alterados = 0
            for row in rows:
                original = row.mes_referencia or ""
                normalizado = normalizar_competencia(original)
                if original != normalizado:
                    conn.execute(
                        text("UPDATE repasses_mensais SET mes_referencia = :n WHERE id = :id"),
                        {"n": normalizado, "id": row.id}
                    )
                    alterados += 1
            return {"status": "success", "total_repasses": len(rows), "alterados": alterados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao normalizar: {str(e)}")

@app.get("/api/entidades")
def list_entidades(usuario: dict = Depends(auth.get_current_user)):
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
                    "updated_at": row_map["updated_at"].isoformat() if row_map["updated_at"] else None,
                    "criado_por": row_map["criado_por"]
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
@app.get("/api/entidades/{entidade_id}")
def get_entidade_completa(entidade_id: str, usuario: dict = Depends(auth.get_current_user)):
    """Retorna uma entidade com formalização + parceria + repasses aninhados (para edição)."""
    if not engine:
        raise HTTPException(status_code=500, detail="Banco de dados não inicializado.")
    try:
        uuid.UUID(entidade_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de entidade inválido (UUID).")

    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT e.*,
                   p.ajuste_termo, p.inicio_atividades, p.termino_atividades, p.gestor_parceria,
                   p.projeto, p.categorias, p.atendimento_descricao, p.meta_mes_atendimentos,
                   p.responsavel_entidade, p.especialidades
            FROM entidades e
            LEFT JOIN dados_parceria p ON e.id = p.entidade_id
            WHERE e.id = :id
        """), {"id": entidade_id}).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Entidade não encontrada.")
        m = row._mapping

        reps = conn.execute(text("""
            SELECT * FROM repasses_mensais
            WHERE entidade_id = :id
            ORDER BY mes_referencia ASC
        """), {"id": entidade_id}).fetchall()

    def d(v):  # date -> 'YYYY-MM-DD'
        return v.isoformat() if v is not None and hasattr(v, "isoformat") else (v or None)

    extras = m["configuracoes_extras"] or {}

    return {
        "id": str(m["id"]),
        # --- Formalização (colunas reais) ---
        "razao_social": m["razao_social"],
        "cnpj": m["cnpj"],
        "responsavel_nome": m["responsavel_nome"],
        "situacao": m["situacao"],
        "historico": m["historico"],
        "pa_emenda": m["pa_emenda"],
        "localizacao_pa_emenda": m["localizacao_pa_emenda"],
        "emenda_alterada": m["emenda_alterada"],
        "pa_formalizacao": m["pa_formalizacao"],
        "numero_emenda": m["numero_emenda"],
        "vereador": m["vereador"],
        "justificativa": m["justificativa"],
        "valor": float(m["valor"]) if m["valor"] is not None else None,
        "cod_scim": m["cod_scim"],
        "pa_empenho": m["pa_empenho"],
        "objeto_descricao": m["objeto_descricao"],
        "configuracoes_extras": extras,
        # --- Parceria (tabela 1:1) ---
        "parceria": {
            "ajuste_termo": m["ajuste_termo"],
            "inicio_atividades": d(m["inicio_atividades"]),
            "termino_atividades": d(m["termino_atividades"]),
            "gestor_parceria": m["gestor_parceria"],
            "projeto": m["projeto"],
            "categorias": m["categorias"] or {},
            "atendimento_descricao": m["atendimento_descricao"],
            "meta_mes_atendimentos": m["meta_mes_atendimentos"] or "",
            "responsavel_entidade": m["responsavel_entidade"],
            "especialidades": m["especialidades"] or {},
        },
        # --- Repasses (tabela 1:N) ---
        "repasses": [
            {
                "mes_referencia": r._mapping["mes_referencia"],
                "repasse_oficio": r._mapping["repasse_oficio"],
                "repasse_periodo": r._mapping["repasse_periodo"],
                "repasse_parcela": float(r._mapping["repasse_parcela"] or 0),
                "repasse_retencao": float(r._mapping["repasse_retencao"] or 0),
                "repasse_valor_final": float(r._mapping["repasse_valor_final"] or 0),
                "repasse_vencimento": d(r._mapping["repasse_vencimento"]),
                "repasse_pa": r._mapping["repasse_pa"],
                "repasse_data_pagamento": d(r._mapping["repasse_data_pagamento"]),
                "prestacao_oficio": r._mapping["prestacao_oficio"],
                "prestacao_data_entrega": d(r._mapping["prestacao_data_entrega"]),
                "prestacao_pa": r._mapping["prestacao_pa"],
                "prestacao_sugestao_glosa": float(r._mapping["prestacao_sugestao_glosa"] or 0),
                "prestacao_reconsideracao": float(r._mapping["prestacao_reconsideracao"] or 0),
                "prestacao_mts": r._mapping["prestacao_mts"],
            } for r in reps
        ],
    }

@app.put("/api/entidades/{entidade_id}")
def update_entidade(entidade_id: str, entidade: EntidadeCreate, usuario: dict = Depends(auth.get_current_user)):
    """
    Atualiza uma entidade existente, incluindo seus dados de parceria e repasses de forma atômica.
    """
    if not engine:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Serviço de banco de dados não inicializado."
        )

    if entidade.repasses:
        soma = sum(float(r.repasse_parcela or 0) for r in entidade.repasses)
        total = float(entidade.valor or 0)
        if total > 0 and abs(soma - total) > 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A soma das parcelas ({soma:.2f}) difere do valor total ({total:.2f})."
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

            _cnpj_digitos = apenas_digitos(entidade.cnpj or "")
            if _cnpj_digitos:
                if not validar_cnpj(_cnpj_digitos):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CNPJ inválido (dígito verificador não confere).")
                dup = conn.execute(text("""
                    SELECT razao_social FROM entidades
                    WHERE regexp_replace(cnpj, '\\D', '', 'g') = :d AND id <> :id LIMIT 1
                """), {"d": _cnpj_digitos, "id": entidade_id}).fetchone()
                if dup:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"CNPJ já cadastrado para: {dup.razao_social}")

            _cnpj_raiz = _cnpj_digitos[0:8] if len(_cnpj_digitos) == 14 else None
            _cnpj_ordem = _cnpj_digitos[8:12] if len(_cnpj_digitos) == 14 else None

            _extras = entidade.configuracoes_extras or {}
            _cpf_rep = apenas_digitos(str(_extras.get("cpf_representante") or "")) or None
            _telefone = apenas_digitos(str(_extras.get("telefone") or "")) or None

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
                    cpf_representante = :cpf_representante,
                    telefone = :telefone,
                    cnpj_raiz = :cnpj_raiz,
                    cnpj_ordem = :cnpj_ordem,
                    updated_at = CURRENT_TIMESTAMP,
                    atualizado_por = :atualizado_por
                WHERE id = :id;
            """)
            
            conn.execute(query_update, {
                "id": entidade_id,
                "razao_social": entidade.razao_social.strip(),
                "cnpj": _cnpj_digitos if _cnpj_digitos else None,
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
                "extras": extras_json,
                "cpf_representante": _cpf_rep,
                "telefone": _telefone,
                "cnpj_raiz": _cnpj_raiz,
                "cnpj_ordem": _cnpj_ordem,
                "atualizado_por": usuario.get("nome") or usuario.get("sub")
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
                "status": "success",
                "message": "Entidade atualizada com sucesso.",
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
def get_repasses(entidade_id: str, usuario: dict = Depends(auth.get_current_user)):
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
def create_repasse_individual(entidade_id: str, repasse: RepasseCreate, usuario: dict = Depends(auth.get_current_user)):
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
def delete_entidade(entidade_id: str, usuario: dict = Depends(auth.get_current_user)):
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
def export_geral(usuario: dict = Depends(auth.get_current_user)):
    """
    Exporta todas as entidades cadastradas e seus repasses para um arquivo Excel com múltiplas abas e formatação do modelo.
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
            
            entidades = [dict(row._mapping) for row in result]
            
            wb = openpyxl.Workbook()
            default_sheet = wb.active
            
            # 1. Cria a aba Formalização se houver entidades
            if entidades:
                ws_form = wb.create_sheet()
                excel_modelo.build_sheet_formalizacao(ws_form, entidades)
                
                # 2. Cria a aba Dados da Parceria
                ws_parc = wb.create_sheet()
                excel_modelo.build_sheet_parceria(ws_parc, entidades)
                
                # 3. Cria uma aba de Repasse para cada entidade
                for ent in entidades:
                    entidade_id = ent["id"]
                    repasses_query = text("""
                        SELECT * FROM repasses_mensais 
                        WHERE entidade_id = :entidade_id 
                        ORDER BY mes_referencia ASC
                    """)
                    repasses_res = conn.execute(repasses_query, {"entidade_id": entidade_id})
                    repasses = [dict(r._mapping) for r in repasses_res]
                    
                    ws_rep = wb.create_sheet()
                    excel_modelo.build_sheet_repasse(ws_rep, ent, repasses)
            else:
                # Caso não tenha nada cadastrado
                ws_empty = wb.create_sheet(title="Sem dados")
                ws_empty.cell(row=1, column=1, value="Nenhuma entidade cadastrada no banco de dados.")
                
            if default_sheet.title in wb.sheetnames:
                wb.remove(default_sheet)
                
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            
            headers = {
                'Content-Disposition': 'attachment; filename="Geral.xlsx"'
            }
            return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
            
    except Exception as e:
        error_msg = safe_str_decode(e)
        raise HTTPException(status_code=500, detail=f"Erro ao exportar dados consolidados: {error_msg}")

@app.get("/api/export/entidade/{entidade_id}")
def export_entidade(entidade_id: str, etapa: str = "todos", usuario: dict = Depends(auth.get_current_user)):
    """
    Exporta dados de uma entidade específica filtrado pela etapa usando o layout modelo.
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
                
            ent = dict(row._mapping)
            razao_social = ent["razao_social"]
            
            wb = openpyxl.Workbook()
            default_sheet = wb.active
            
            # 1. Formalização
            if etapa in ("todos", "formalizacao"):
                ws_form = wb.create_sheet()
                excel_modelo.build_sheet_formalizacao(ws_form, [ent])
            
            # 2. Dados da Parceria
            if etapa in ("todos", "parceria"):
                ws_parc = wb.create_sheet()
                excel_modelo.build_sheet_parceria(ws_parc, [ent])
            
            # 3. Controle Financeiro / Repasses
            if etapa in ("todos", "financeiro"):
                repasses_query = text("""
                    SELECT * FROM repasses_mensais 
                    WHERE entidade_id = :entidade_id 
                    ORDER BY mes_referencia ASC
                """)
                repasses_res = conn.execute(repasses_query, {"entidade_id": entidade_id})
                repasses = [dict(r._mapping) for r in repasses_res]
                
                ws_rep = wb.create_sheet()
                excel_modelo.build_sheet_repasse(ws_rep, ent, repasses)
                
            if default_sheet.title in wb.sheetnames:
                wb.remove(default_sheet)
                
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            
            secao = "Controle Financeiro" if etapa == "financeiro" else ("Dados da Parceria" if etapa == "parceria" else ("Formalização" if etapa == "formalizacao" else "Geral"))
            nome_arq = f"{razao_social} - {secao}.xlsx"
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
def export_dados(dados: dict, etapa: str = "todos", usuario: dict = Depends(auth.get_current_user)):
    """
    Exporta os dados enviados diretamente no corpo da requisição para um arquivo Excel (rascunho) usando o layout modelo.
    """
    try:
        razao_social = dados.get("razao_social") or "Nova Parceria"
        parceria = dados.get("parceria") or {}
        
        entidade_unificada = {
            "id": dados.get("id"),
            "razao_social": razao_social,
            "cnpj": dados.get("cnpj") or "",
            "situacao": dados.get("situacao") or "",
            "historico": dados.get("historico") or "",
            "pa_emenda": dados.get("pa_emenda") or "",
            "localizacao_pa_emenda": dados.get("localizacao_pa_emenda") or "",
            "emenda_alterada": dados.get("emenda_alterada") or "",
            "pa_formalizacao": dados.get("pa_formalizacao") or "",
            "numero_emenda": dados.get("numero_emenda") or "",
            "vereador": dados.get("vereador") or "",
            "justificativa": dados.get("justificativa") or "",
            "valor": dados.get("valor") or 0.0,
            
            # Dados da parceria extraídos do dicionário aninhado
            "ajuste_termo": parceria.get("ajuste_termo") or "",
            "inicio_atividades": parceria.get("inicio_atividades") or "",
            "termino_atividades": parceria.get("termino_atividades") or "",
            "gestor_parceria": parceria.get("gestor_parceria") or "",
            "projeto": parceria.get("projeto") or "",
            "categorias": parceria.get("categorias") or [],
            "atendimento_descricao": parceria.get("atendimento_descricao") or "",
            "meta_mes_atendimentos": parceria.get("meta_mes_atendimentos") or "",
            "especialidades": parceria.get("especialidades") or {},
            "responsavel_entidade": parceria.get("responsavel_entidade") or "",
            
            # Dados para o repasse
            "cod_scim": dados.get("cod_scim") or "",
            "pa_empenho": dados.get("pa_empenho") or "",
            "objeto_descricao": dados.get("objeto_descricao") or "",
        }
        
        repasses_raw = dados.get("repasses") or []
        repasses = []
        for r in repasses_raw:
            if isinstance(r, dict):
                repasses.append({
                    "mes_referencia": r.get("mes_referencia") or "",
                    "repasse_oficio": r.get("repasse_oficio") or "",
                    "repasse_periodo": r.get("repasse_periodo") or "",
                    "repasse_parcela": r.get("repasse_parcela") or 0.0,
                    "repasse_retencao": r.get("repasse_retencao") or 0.0,
                    "repasse_valor_final": r.get("repasse_valor_final") or 0.0,
                    "repasse_vencimento": r.get("repasse_vencimento") or "",
                    "repasse_pa": r.get("repasse_pa") or "",
                    "repasse_data_pagamento": r.get("repasse_data_pagamento") or "",
                    "prestacao_oficio": r.get("prestacao_oficio") or "",
                    "prestacao_data_entrega": r.get("prestacao_data_entrega") or "",
                    "prestacao_pa": r.get("prestacao_pa") or "",
                    "prestacao_sugestao_glosa": r.get("prestacao_sugestao_glosa") or 0.0,
                    "prestacao_reconsideracao": r.get("prestacao_reconsideracao") or 0.0,
                    "prestacao_mts": r.get("prestacao_mts") or "",
                })
                
        wb = openpyxl.Workbook()
        default_sheet = wb.active
        
        # 1. Formalização
        if etapa in ("todos", "formalizacao"):
            ws_form = wb.create_sheet()
            excel_modelo.build_sheet_formalizacao(ws_form, [entidade_unificada])
            
        # 2. Dados da Parceria
        if etapa in ("todos", "parceria"):
            ws_parc = wb.create_sheet()
            excel_modelo.build_sheet_parceria(ws_parc, [entidade_unificada])
            
        # 3. Controle Financeiro / Repasses
        if etapa in ("todos", "financeiro"):
            ws_rep = wb.create_sheet()
            excel_modelo.build_sheet_repasse(ws_rep, entidade_unificada, repasses)
            
        if default_sheet.title in wb.sheetnames:
            wb.remove(default_sheet)
            
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        secao = "Controle Financeiro" if etapa == "financeiro" else ("Dados da Parceria" if etapa == "parceria" else ("Formalização" if etapa == "formalizacao" else "Geral"))
        nome_arq = f"{razao_social} - {secao}.xlsx"
        headers = {
            'Content-Disposition': f'attachment; filename="{nome_arq}"'
        }
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
        
    except Exception as e:
        error_msg = safe_str_decode(e)
        raise HTTPException(status_code=500, detail=f"Erro ao exportar dados temporários: {error_msg}")

@app.post("/api/chat/upload-excel")
async def chat_upload_excel(file: UploadFile = File(...), usuario: dict = Depends(auth.get_current_user)):
    import ia_excel
    conteudo = await file.read()
    return {"contexto_planilha": ia_excel.excel_para_texto(conteudo)}

@app.post("/api/chat")
def chat(req: ChatRequest, usuario: dict = Depends(auth.get_current_user)):
    """Responde perguntas sobre os cadastros, com contexto ancorado no banco. Streaming."""
    if not ollama_service.disponivel():
        raise HTTPException(
            status_code=503,
            detail="Assistente de IA indisponível: verifique se o Ollama está em execução."
        )
    # Limita o histórico às últimas 6 trocas para não inflar o prompt
    historico = (req.historico or [])[-6:]
    contexto = ia_contexto.montar_contexto(req.pergunta)
    if req.contexto_planilha:
        contexto = contexto + "\n\n" + req.contexto_planilha

    def gerar():
        try:
            for token in ollama_service.stream_resposta(req.pergunta, contexto, historico):
                yield token
        except Exception as e:
            yield f"\n[Erro ao gerar resposta: {e}]"

    return StreamingResponse(gerar(), media_type="text/plain; charset=utf-8")

@app.post("/api/import/planilha")
async def importar_planilha(file: UploadFile = File(...), usuario: dict = Depends(auth.get_current_user)):
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

@app.get("/api/import/modelo")
def baixar_modelo_importacao(formato: str = "xlsx", usuario: dict = Depends(auth.get_current_user)):
    """Gera um arquivo EM BRANCO com os cabeçalhos esperados pela importação."""
    if formato == "csv":
        import csv as _csv
        headers = ["STATUS", "HISTÓRICO", "NOME", "CNPJ", "PA Emenda", "Localização do PA Emenda",
                   "Emenda Alterada?", "PA Formalização", "N.º", "Vereador", "Justificativa", "Valor"]
        buf = io.StringIO()
        w = _csv.writer(buf, delimiter=";")
        w.writerow(headers)
        w.writerow([""] * len(headers))
        dados = ("﻿" + buf.getvalue()).encode("utf-8")
        return StreamingResponse(
            io.BytesIO(dados),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="Modelo_Importacao_PreFinance.csv"'},
        )

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    excel_modelo.build_sheet_formalizacao(wb.create_sheet("tmp1"), [])
    excel_modelo.build_sheet_parceria(wb.create_sheet("tmp2"), [])
    excel_modelo.build_sheet_repasse(wb.create_sheet("tmp3"), {"razao_social": ""}, [])

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return StreamingResponse(
        out,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="Modelo_Importacao_PreFinance.xlsx"'},
    )

if __name__ == "__main__":
    import uvicorn
    # Inicia o servidor uvicorn na porta 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
