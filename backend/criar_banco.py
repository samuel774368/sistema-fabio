# Script para criar tabelas diretamente no MySQL
import pymysql
import sys
from datetime import date

def criar_tabelas_mysql():
    """Criar tabelas diretamente no MySQL"""
    try:
        print("🔧 Criando tabelas no banco escola_db...")
        
        # Conectar ao MySQL
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='escola_db',
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # SQL para criar tabela turmas
        sql_turmas = """
        CREATE TABLE IF NOT EXISTS turmas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL UNIQUE,
            capacidade INT NOT NULL,
            INDEX idx_turma_nome (nome)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """
        
        # SQL para criar tabela alunos
        sql_alunos = """
        CREATE TABLE IF NOT EXISTS alunos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(80) NOT NULL,
            data_nascimento DATE NOT NULL,
            email VARCHAR(120) UNIQUE NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'inativo',
            turma_id INT NULL,
            INDEX idx_aluno_nome (nome),
            INDEX idx_aluno_email (email),
            INDEX idx_aluno_status (status),
            FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """
        
        # Executar comandos
        print("📚 Criando tabela turmas...")
        cursor.execute(sql_turmas)
        
        print("👥 Criando tabela alunos...")
        cursor.execute(sql_alunos)
        
        connection.commit()
        print("✅ Tabelas criadas com sucesso!")
        
        # Verificar tabelas criadas
        cursor.execute("SHOW TABLES")
        tabelas = [tabela[0] for tabela in cursor.fetchall()]
        print(f"📋 Tabelas existentes: {tabelas}")
        
        cursor.close()
        connection.close()
        return True
        
    except pymysql.Error as e:
        print(f"❌ Erro MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def popular_dados():
    """Popular tabelas com dados de exemplo"""
    try:
        print("\n🌱 Populando banco com dados de exemplo...")
        
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='escola_db',
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Verificar se já tem dados
        cursor.execute("SELECT COUNT(*) FROM turmas")
        turmas_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alunos") 
        alunos_count = cursor.fetchone()[0]
        
        if turmas_count > 0 or alunos_count > 0:
            print(f"⚠️ Já existem {turmas_count} turmas e {alunos_count} alunos")
            resposta = input("Deseja continuar mesmo assim? (s/n): ")
            if resposta.lower() not in ['s', 'sim', 'y', 'yes']:
                print("❌ Operação cancelada")
                return False
        
        # Inserir turmas
        print("📚 Inserindo turmas...")
        turmas = [
            ("1º Ano A", 30),
            ("1º Ano B", 28),
            ("1º Ano C", 25),
            ("2º Ano A", 30),
            ("2º Ano B", 27),
            ("2º Ano C", 29),
            ("3º Ano A", 25),
            ("3º Ano B", 24),
            ("3º Ano C", 26),
            ("Turma Especial", 15)
        ]
        
        sql_insert_turma = "INSERT IGNORE INTO turmas (nome, capacidade) VALUES (%s, %s)"
        for turma in turmas:
            cursor.execute(sql_insert_turma, turma)
            print(f"  ✅ Turma: {turma[0]}")
        
        # Inserir alunos
        print("👥 Inserindo alunos...")
        alunos = [
            ("Ana Carolina Silva Santos", "2008-03-15", "ana.silva@email.com", "ativo", 1),
            ("Bruno Eduardo Oliveira Costa", "2007-07-22", "bruno.oliveira@email.com", "ativo", 1),
            ("Camila Beatriz Lima Ferreira", "2009-01-10", "camila.lima@email.com", "ativo", 2),
            ("Diego Fernando Santos Rocha", "2008-11-05", "diego.santos@email.com", "ativo", 2),
            ("Eduarda Cristina Mendes Alves", "2007-09-18", "eduarda.mendes@email.com", "ativo", 3),
            ("Felipe Gabriel Costa Pereira", "2008-04-08", "felipe.costa@email.com", "ativo", 3),
            ("Gabriela Maria Rodrigues Lima", "2009-06-12", "gabriela.rodrigues@email.com", "ativo", 4),
            ("Henrique José Fernandes Silva", "2007-02-28", "henrique.fernandes@email.com", "ativo", 4),
            ("Isabella Sophia Martins Souza", "2008-08-14", "isabella.martins@email.com", "ativo", 5),
            ("João Pedro Araújo Barbosa", "2007-12-03", "joao.araujo@email.com", "ativo", 5),
            ("Larissa Vitória Gomes Castro", "2009-05-20", "larissa.gomes@email.com", "ativo", 6),
            ("Matheus Alexandre Dias Moreira", "2008-10-16", "matheus.dias@email.com", "ativo", 6),
            ("Natália Fernanda Cardoso Ribeiro", "2007-01-25", "natalia.cardoso@email.com", "ativo", 7),
            ("Otávio Rafael Correia Nunes", "2008-07-09", "otavio.correia@email.com", "ativo", 7),
            ("Priscila Amanda Teixeira Monteiro", "2009-03-07", "priscila.teixeira@email.com", "ativo", 8),
            ("Rafael Leonardo Vieira Campos", "2007-11-21", "rafael.vieira@email.com", "ativo", 8),
            ("Sofia Helena Nascimento Freitas", "2008-09-04", "sofia.nascimento@email.com", "ativo", 9),
            ("Thiago Gustavo Ramos Machado", "2007-04-17", "thiago.ramos@email.com", "ativo", 9),
            ("Valentina Júlia Carvalho Lopes", "2009-08-30", "valentina.carvalho@email.com", "ativo", 10),
            ("Wellington Victor Melo Torres", "2008-02-11", "wellington.melo@email.com", "ativo", 10),
            ("Xavier Antônio Pinto Duarte", "2007-06-19", "xavier.pinto@email.com", "inativo", None),
            ("Yasmin Beatriz Moura Santana", "2008-12-08", "yasmin.moura@email.com", "inativo", None),
            ("Zacarias Miguel Cunha Barros", "2009-04-26", "zacarias.cunha@email.com", "inativo", None),
            ("Ana Luiza de Souza e Silva", "2008-05-14", None, "ativo", 1),
            ("José Carlos dos Santos Junior", "2007-10-23", None, "ativo", 2)
        ]
        
        sql_insert_aluno = """
        INSERT IGNORE INTO alunos (nome, data_nascimento, email, status, turma_id) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        for aluno in alunos:
            cursor.execute(sql_insert_aluno, aluno)
            turma_info = f" (Turma {aluno[4]})" if aluno[4] else " (Sem turma)"
            print(f"  ✅ Aluno: {aluno[0]}{turma_info}")
        
        connection.commit()
        
        # Estatísticas finais
        cursor.execute("SELECT COUNT(*) FROM turmas")
        total_turmas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alunos")
        total_alunos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alunos WHERE status = 'ativo'")
        alunos_ativos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alunos WHERE status = 'inativo'")
        alunos_inativos = cursor.fetchone()[0]
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   📚 Total de turmas: {total_turmas}")
        print(f"   👥 Total de alunos: {total_alunos}")
        print(f"   ✅ Alunos ativos: {alunos_ativos}")
        print(f"   ❌ Alunos inativos: {alunos_inativos}")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 Banco populado com sucesso!")
        return True
        
    except pymysql.Error as e:
        print(f"❌ Erro MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def menu():
    """Menu principal"""
    while True:
        print("\n" + "="*50)
        print("🏫 CONFIGURAÇÃO DO BANCO ESCOLA")
        print("="*50)
        print("1. 🔧 Criar tabelas")
        print("2. 🌱 Popular com dados de exemplo")
        print("3. 🔄 Criar tabelas + Popular")
        print("4. 📊 Ver estatísticas")
        print("5. ❌ Sair")
        print("="*50)
        
        opcao = input("Escolha uma opção (1-5): ").strip()
        
        if opcao == "1":
            criar_tabelas_mysql()
        elif opcao == "2":
            popular_dados()
        elif opcao == "3":
            if criar_tabelas_mysql():
                popular_dados()
        elif opcao == "4":
            ver_estatisticas()
        elif opcao == "5":
            print("👋 Tchau!")
            break
        else:
            print("❌ Opção inválida!")

def ver_estatisticas():
    """Ver estatísticas do banco"""
    try:
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='escola_db',
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Estatísticas gerais
        cursor.execute("SELECT COUNT(*) FROM turmas")
        total_turmas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alunos")
        total_alunos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alunos WHERE status = 'ativo'")
        alunos_ativos = cursor.fetchone()[0]
        
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"📚 Turmas: {total_turmas}")
        print(f"👥 Alunos: {total_alunos}")
        print(f"✅ Ativos: {alunos_ativos}")
        
        # Ocupação por turma
        cursor.execute("""
            SELECT t.nome, t.capacidade, COUNT(a.id) as ocupacao
            FROM turmas t
            LEFT JOIN alunos a ON t.id = a.turma_id
            GROUP BY t.id, t.nome, t.capacidade
            ORDER BY t.nome
        """)
        
        print(f"\n📋 OCUPAÇÃO POR TURMA:")
        for turma in cursor.fetchall():
            nome, capacidade, ocupacao = turma
            percentual = (ocupacao / capacidade) * 100 if capacidade > 0 else 0
            print(f"   {nome}: {ocupacao}/{capacidade} ({percentual:.1f}%)")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    menu()
