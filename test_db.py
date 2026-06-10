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

# Conecta ao postgres padrão primeiro para verificar/criar o banco
admin_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
print(f"Conectando ao banco administrativo: {admin_url}")

try:
    engine = create_engine(admin_url)
    with engine.connect() as conn:
        # Verifica se o banco de dados prefinance existe
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'prefinance'"))
        exists = result.fetchone()
        if not exists:
            print("Banco 'prefinance' não existe. Criando...")
            # psycopg2 não permite CREATE DATABASE dentro de blocos de transação normais.
            # Precisamos fechar a transação implícita (autocommit)
            conn.execution_options(isolation_level="AUTOCOMMIT").execute(text("CREATE DATABASE prefinance"))
            print("Banco 'prefinance' criado com sucesso!")
        else:
            print("Banco 'prefinance' já existe.")
except Exception as e:
    print("Erro ao verificar/criar banco administrativo:")
    try:
        print(str(e))
    except UnicodeDecodeError:
        print("Erro de encoding ao tentar exibir erro admin!")
        if hasattr(e, "args"):
            print("Args:", [arg.decode('cp1252', errors='replace') if isinstance(arg, bytes) else str(arg) for arg in e.args])
        else:
            print("Detalhes indisponíveis devido a encoding.")

# Agora testa conectar ao banco prefinance
app_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(f"\nConectando ao banco do aplicativo: {app_url}")
try:
    engine = create_engine(app_url)
    with engine.connect() as conn:
        print("Conexão ao banco prefinance estabelecida com sucesso!")
except Exception as e:
    print("Erro ao conectar no banco prefinance:")
    try:
        print(str(e))
    except UnicodeDecodeError:
        print("Erro de encoding ao tentar exibir erro app!")
        if hasattr(e, "args"):
            print("Args:", [arg.decode('cp1252', errors='replace') if isinstance(arg, bytes) else str(arg) for arg in e.args])
        else:
            print("Detalhes indisponíveis devido a encoding.")
