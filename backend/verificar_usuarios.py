#!/usr/bin/env python3
import sqlite3
import os

# Verificar se o arquivo existe
db_path = 'escola.db'
if not os.path.exists(db_path):
    print(f"❌ Arquivo {db_path} não encontrado!")
    exit()

print(f"✅ Arquivo {db_path} encontrado!")

try:
    # Conectar ao banco
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Listar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"\n📋 Tabelas no banco: {[t[0] for t in tables]}")
    
    # Verificar se a tabela usuarios existe
    if 'usuarios' in [t[0] for t in tables]:
        print("\n👥 Consultando usuários:")
        cursor.execute("SELECT id, username, email, tipo_usuario FROM usuarios;")
        users = cursor.fetchall()
        
        if users:
            for user in users:
                print(f"  ID: {user[0]} | Username: {user[1]} | Email: {user[2]} | Tipo: {user[3]}")
        else:
            print("  Nenhum usuário encontrado!")
    else:
        print("\n❌ Tabela 'usuarios' não encontrada!")
    
    conn.close()
    print("\n✅ Consulta finalizada!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
