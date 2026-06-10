import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Carrega as variáveis de ambiente
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "prefinance")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print(f"Tentando criar a tabela dados_parceria no banco: {DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    engine = create_engine(DATABASE_URL)
    
    # Carrega o DDL de dados_parceria
    with open("dados_parceria_schema.sql", "r", encoding="utf-8") as f:
        migration_sql = f.read()
        
    # Executa o DDL
    with engine.begin() as conn:
        print("Executando CREATE TABLE dados_parceria...")
        conn.execute(text(migration_sql))
        print("Tabela 'dados_parceria' criada com sucesso!")
except Exception as e:
    print("\n[ERRO] Falha ao criar a tabela:")
    print(e)
