#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import hashlib
import sys

# Configuração do banco
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': '',
    'database': 'escola_db',
    'charset': 'utf8mb4'
}

def main():
    try:
        print("🔄 Conectando ao banco de dados...")
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            print("📋 Criando tabela usuarios...")
            
            # Criar tabela usuarios
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
            
            print("👤 Criando usuário admin...")
            
            # Hash da senha admin123
            admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
            
            # Inserir admin
            cursor.execute("""
            INSERT IGNORE INTO usuarios (username, email, senha_hash, tipo_usuario) 
            VALUES ('admin', 'admin@escola.com', %s, 'admin')
            """, (admin_password,))
            
            connection.commit()
            
            # Verificar se foi criado
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username='admin'")
            count = cursor.fetchone()[0]
            
            print(f"✅ Sucesso!")
            print(f"✅ Tabela usuarios criada!")
            print(f"✅ Admin criado: {'Sim' if count > 0 else 'Não'}")
            print(f"📝 Credenciais:")
            print(f"   Username: admin")
            print(f"   Senha: admin123")
            print(f"   Hash: {admin_password}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)
    finally:
        if 'connection' in locals():
            connection.close()
            print("🔒 Conexão fechada")

if __name__ == "__main__":
    main()
