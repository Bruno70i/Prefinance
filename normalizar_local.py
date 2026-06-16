# normalizar_local.py
import os
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Garante o carregamento do .env local
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "prefinance")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

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
    
    # Se já estiver no formato correto
    if re.fullmatch(r"\d{2}\.\d{4}", v):
        return v
        
    # Tenta separar por separadores comuns
    partes = re.split(r"[\/\-\.\s]+", v)
    if len(partes) != 2:
        return valor
        
    p1, p2 = partes[0], partes[1]
    mes = ""
    ano = ""
    
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

print(f"Conectando a {DB_HOST}:{DB_PORT}/{DB_NAME}...")
try:
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT id, mes_referencia FROM repasses_mensais")).fetchall()
        print(f"Total de repasses encontrados: {len(rows)}")
        
        alterados = 0
        for row in rows:
            original = row.mes_referencia or ""
            normalizado = normalizar_competencia(original)
            if original != normalizado:
                conn.execute(
                    text("UPDATE repasses_mensais SET mes_referencia = :n WHERE id = :id"),
                    {"n": normalizado, "id": row.id}
                )
                print(f"ID {row.id}: '{original}' -> '{normalizado}'")
                alterados += 1
                
        print(f"Normalização concluída. Total alterado: {alterados}")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Erro na migração de dados: {e}")
