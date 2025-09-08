#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

def hash_password(password):
    """Cria hash da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def criar_tabela_usuarios():
    """Cria a tabela de usuários"""
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
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
            
            # Criar usuário administrador padrão
            admin_password = hash_password('admin123')
            cursor.execute("""
            INSERT IGNORE INTO usuarios (username, email, senha_hash, tipo_usuario) 
            VALUES ('admin', 'admin@escola.com', %s, 'admin')
            """, (admin_password,))
            
            connection.commit()
            print("✅ Tabela de usuários criada com sucesso!")
            print("✅ Usuário admin criado!")
            print("   Username: admin")
            print("   Senha: admin123")
            print("   Tipo: administrador")
            
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    criar_tabela_usuarios()
