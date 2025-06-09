import pyodbc

def get_connection():
    try:
        print("📌 Iniciando conexão no database.py!")
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=SUP_SUPORTE_01;'      # Mantém exatamente igual ao ambiente do Windows
            'DATABASE=SistemaAgendamento;'
            'Trusted_Connection=yes;'      # Usa autenticação do Windows
        )
        print("✅ Conexão OK!")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None
