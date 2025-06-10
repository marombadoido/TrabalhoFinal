import psycopg2

def get_connection():
    try:
        print("📌 Iniciando conexão no database.py (PostgreSQL)!")

        conn = psycopg2.connect(
            dbname='postgres',                   # Nome inicial do banco
            user='postgres',                     # Usuário padrão
            password='StrongPassword123!',       # A senha que você definiu
            host='34.136.2.112',                 # Endereço IP público da sua instância
            port='5432'                          # Porta padrão do PostgreSQL
        )

        print("✅ Conexão OK!")
        return conn

    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None
