import pymysql
import hashlib

# Configuração do banco
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': '',
    'database': 'escola_db',
    'charset': 'utf8mb4'
}

def criar_admin():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            # Criar tabela usuarios se não existir
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                senha_hash VARCHAR(64) NOT NULL,
                tipo_usuario ENUM('admin', 'usuario') DEFAULT 'usuario',
                ativo BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_login TIMESTAMP NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # Criar admin
            admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute("""
            INSERT IGNORE INTO usuarios (username, email, senha_hash, tipo_usuario) 
            VALUES ('admin', 'admin@escola.com', %s, 'admin')
            """, (admin_password,))
            
            connection.commit()
            print("✅ Tabela e usuário admin criados!")
            print("Username: admin")
            print("Senha: admin123")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    criar_admin()
