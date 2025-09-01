#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql

def inserir_turmas_teste():
    """Insere turmas de teste se não existirem"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='escola_db',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Verificar se já existem turmas
            cursor.execute("SELECT COUNT(*) FROM turmas")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("📚 Inserindo turmas de teste...")
                
                turmas_teste = [
                    ("1º Ano A", 30),
                    ("1º Ano B", 30),
                    ("2º Ano A", 25),
                    ("2º Ano B", 25),
                    ("3º Ano A", 28),
                    ("Turma Especial", 15)
                ]
                
                for nome, capacidade in turmas_teste:
                    cursor.execute(
                        "INSERT INTO turmas (nome, capacidade) VALUES (%s, %s)",
                        (nome, capacidade)
                    )
                
                connection.commit()
                print(f"✅ {len(turmas_teste)} turmas inseridas com sucesso!")
            else:
                print(f"📊 Já existem {count} turmas no banco")
                
        connection.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    inserir_turmas_teste()
