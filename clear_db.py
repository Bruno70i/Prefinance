import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Carrega variáveis de ambiente
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

print(f"Conectando para limpar o banco de dados: {DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        # Exclui todos os dados da tabela principal e tabelas vinculadas em cascata
        conn.execute(text("TRUNCATE TABLE entidades CASCADE;"))
        print("Sucesso: Todas as tabelas foram limpas com sucesso (entidades, dados_parceria, repasses_mensais)!")
except Exception as err:
    print(f"Erro ao limpar banco de dados: {err}")
