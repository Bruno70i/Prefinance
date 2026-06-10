import os
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Carrega variáveis de ambiente de um arquivo .env
load_dotenv()

# Configuração da conexão com o banco PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "prefinance")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print(f"Tentando conectar ao banco: {DB_HOST}:{DB_PORT}/{DB_NAME} (Usuário: {DB_USER})")

try:
    engine = create_engine(DATABASE_URL)
    
    # 1. Carrega o arquivo SQL de DDL tratando variações de encoding no Windows
    ddl_sql = ""
    try:
        with open("schema.sql", "r", encoding="utf-8") as f:
            ddl_sql = f.read()
    except UnicodeDecodeError:
        with open("schema.sql", "r", encoding="latin1") as f:
            ddl_sql = f.read()
    
    # Executa a criação da tabela
    with engine.begin() as conn:
        print("Executando DDL (criação da tabela entidades)...")
        # psycopg2 requires splitting statements or executing them. SQLAlchemy handles raw SQL.
        # We split by semicolon to execute clean commands or run them as a block
        conn.execute(text(ddl_sql))
        print("Tabela 'entidades' criada/verificada com sucesso!")

    # 2. Carrega as entidades mapeadas no Passo 1 com fallback de encoding
    entidades = []
    try:
        with open("entidades_mapeadas.json", "r", encoding="utf-8") as f:
            entidades = json.load(f)
    except UnicodeDecodeError:
        with open("entidades_mapeadas.json", "r", encoding="latin1") as f:
            entidades = json.load(f)
    
    # 3. Faz o seed dos dados no banco
    inserted_count = 0
    updated_count = 0
    
    with engine.begin() as conn:
        for ent in entidades:
            razao_social = ent["razao_social"]
            cnpj = ent["cnpj"]
            responsavel = ent["responsavel_nome"]
            extras = json.dumps(ent["configuracoes_extras"])
            
            # Verifica se já existe por CNPJ (se CNPJ existir) ou por Razão Social
            if cnpj:
                query_check = text("SELECT id FROM entidades WHERE cnpj = :cnpj")
                result = conn.execute(query_check, {"cnpj": cnpj}).fetchone()
            else:
                query_check = text("SELECT id FROM entidades WHERE razao_social = :razao_social")
                result = conn.execute(query_check, {"razao_social": razao_social}).fetchone()
                
            if result:
                # Faz o Update
                ent_id = result[0]
                query_update = text("""
                    UPDATE entidades 
                    SET razao_social = :razao_social, 
                        responsavel_nome = :responsavel, 
                        configuracoes_extras = :extras
                    WHERE id = :id
                """)
                conn.execute(query_update, {
                    "razao_social": razao_social,
                    "responsavel": responsavel,
                    "extras": extras,
                    "id": ent_id
                })
                updated_count += 1
                print(f"Atualizado: {razao_social}")
            else:
                # Faz o Insert
                query_insert = text("""
                    INSERT INTO entidades (razao_social, cnpj, responsavel_nome, configuracoes_extras)
                    VALUES (:razao_social, :cnpj, :responsavel, :extras)
                """)
                conn.execute(query_insert, {
                    "razao_social": razao_social,
                    "cnpj": cnpj,
                    "responsavel": responsavel,
                    "extras": extras
                })
                inserted_count += 1
                print(f"Inserido: {razao_social}")
                
    print(f"\n--- Migração Concluída ---")
    print(f"Total Inseridas: {inserted_count}")
    print(f"Total Atualizadas: {updated_count}")
    
except Exception as e:
    print(f"\n[ERRO] Falha durante a migração/seed do banco de dados:")
    print(e)
    print("\n👉 Para rodar a migração, certifique-se de configurar as variáveis de ambiente corretas em um arquivo '.env'.")
