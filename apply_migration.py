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

print(f"Tentando aplicar a migração no banco: {DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    engine = create_engine(DATABASE_URL)
    
    # Carrega o DDL de migração
    with open("update_schema.sql", "r", encoding="utf-8") as f:
        migration_sql = f.read()
        
    # Executa a migração
    with engine.begin() as conn:
        print("Executando ALTER TABLE DDL...")
        conn.execute(text(migration_sql))
        print("Migração aplicada com sucesso! Todas as novas colunas foram criadas.")
except Exception as e:
    print("\n[ERRO] Falha ao rodar a migração:")
    print(e)
