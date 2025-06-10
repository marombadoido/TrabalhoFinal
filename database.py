import psycopg2

def get_connection():
    try:
        print("📌 Iniciando conexão com o banco de dados PostgreSQL...")
        conn = psycopg2.connect(
            dbname="sistemaagendamento",
            user="postgres",
            password="StrongPassword123!",
            host="34.136.2.112",
            port="5432"
        )
        print("✅ Conexão OK!")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None
