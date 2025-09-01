#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql

def criar_tabela_matriculas():
    """Cria a tabela de matrículas se não existir"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='escola_db',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Criar tabela matrículas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matriculas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    aluno_id INT NOT NULL,
                    turma_id INT NOT NULL,
                    data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
                    FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_matricula (aluno_id, turma_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
            """)
            
            connection.commit()
            print("✅ Tabela 'matriculas' criada com sucesso!")
            
            # Verificar se existem dados
            cursor.execute("SELECT COUNT(*) FROM matriculas")
            count = cursor.fetchone()[0]
            print(f"📊 Total de matrículas: {count}")
            
        connection.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    criar_tabela_matriculas()
