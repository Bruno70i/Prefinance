import psycopg2
import sys

print("Testando conexão via psycopg2 diretamente...")
try:
    # Tenta conectar e capturar o erro bruto
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres"
    )
    print("Conexão com postgres admin estabelecida com sucesso!")
    conn.close()
except Exception as e:
    print("Erro capturado!")
    # O erro original de conexão em psycopg2 geralmente está no e.pgerror ou similar,
    # mas o próprio str(e) pode falhar no decode. Vamos tentar inspecionar os bytes.
    print(f"Tipo do erro: {type(e)}")
    
    # Se for OperationalError ou similar, podemos inspecionar os atributos
    for attr in dir(e):
        if not attr.startswith('__'):
            try:
                val = getattr(e, attr)
                if isinstance(val, bytes):
                    print(f"{attr} (bytes): {val.decode('cp1252', errors='replace')}")
                elif isinstance(val, str):
                    print(f"{attr}: {val}")
            except Exception as attr_err:
                pass
                
    # Vamos tentar decodificar a mensagem de erro do sistema
    try:
        # Se for um OperationalError do psycopg2, ele herda de Exception
        msg = e.args[0]
        if isinstance(msg, bytes):
            print("Mensagem binária decodificada (CP1252):", msg.decode('cp1252', errors='replace'))
        else:
            print("Mensagem string original:", str(msg))
    except Exception as parse_err:
        print("Falha ao decodificar args da exceção:", parse_err)
