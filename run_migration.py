# run_migration.py
# Uso: python run_migration.py migrations/2026_validacoes.sql
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "prefinance")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

if len(sys.argv) < 2:
    print("Uso: python run_migration.py <caminho_do_arquivo.sql>")
    sys.exit(1)

caminho = sys.argv[1]
with open(caminho, "r", encoding="utf-8") as f:
    sql = f.read()

print(f"Aplicando migração: {caminho} em {DB_HOST}:{DB_PORT}/{DB_NAME}")
try:
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(text(sql))
    print("Migração aplicada com sucesso.")
except Exception as err:
    print(f"Erro ao aplicar migração: {err}")
    sys.exit(1)
