# Script para popular o banco de dados com dados de teste
from datetime import date, datetime
import sys
import os

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_session, close_db_session, init_db, DatabaseTransaction
from models import Turma, Aluno

def criar_turmas_exemplo():
    """Criar turmas de exemplo"""
    turmas = [
        {"nome": "1º Ano A", "capacidade": 30},
        {"nome": "1º Ano B", "capacidade": 28},
        {"nome": "1º Ano C", "capacidade": 25},
        {"nome": "2º Ano A", "capacidade": 30},
        {"nome": "2º Ano B", "capacidade": 27},
        {"nome": "2º Ano C", "capacidade": 29},
        {"nome": "3º Ano A", "capacidade": 25},
        {"nome": "3º Ano B", "capacidade": 24},
        {"nome": "3º Ano C", "capacidade": 26},
        {"nome": "Turma Especial", "capacidade": 15}
    ]
    
    return [Turma(**turma_data) for turma_data in turmas]

def criar_alunos_exemplo():
    """Criar alunos de exemplo"""
    alunos = [
        {
            "nome": "Ana Carolina Silva Santos",
            "data_nascimento": date(2008, 3, 15),
            "email": "ana.silva@email.com",
            "status": "ativo",
            "turma_id": 1
        },
        {
            "nome": "Bruno Eduardo Oliveira Costa",
            "data_nascimento": date(2007, 7, 22),
            "email": "bruno.oliveira@email.com",
            "status": "ativo",
            "turma_id": 1
        },
        {
            "nome": "Camila Beatriz Lima Ferreira",
            "data_nascimento": date(2009, 1, 10),
            "email": "camila.lima@email.com",
            "status": "ativo",
            "turma_id": 2
        },
        {
            "nome": "Diego Fernando Santos Rocha",
            "data_nascimento": date(2008, 11, 5),
            "email": "diego.santos@email.com",
            "status": "ativo",
            "turma_id": 2
        },
        {
            "nome": "Eduarda Cristina Mendes Alves",
            "data_nascimento": date(2007, 9, 18),
            "email": "eduarda.mendes@email.com",
            "status": "ativo",
            "turma_id": 3
        },
        {
            "nome": "Felipe Gabriel Costa Pereira",
            "data_nascimento": date(2008, 4, 8),
            "email": "felipe.costa@email.com",
            "status": "ativo",
            "turma_id": 3
        },
        {
            "nome": "Gabriela Maria Rodrigues Lima",
            "data_nascimento": date(2009, 6, 12),
            "email": "gabriela.rodrigues@email.com",
            "status": "ativo",
            "turma_id": 4
        },
        {
            "nome": "Henrique José Fernandes Silva",
            "data_nascimento": date(2007, 2, 28),
            "email": "henrique.fernandes@email.com",
            "status": "ativo",
            "turma_id": 4
        },
        {
            "nome": "Isabella Sophia Martins Souza",
            "data_nascimento": date(2008, 8, 14),
            "email": "isabella.martins@email.com",
            "status": "ativo",
            "turma_id": 5
        },
        {
            "nome": "João Pedro Araújo Barbosa",
            "data_nascimento": date(2007, 12, 3),
            "email": "joao.araujo@email.com",
            "status": "ativo",
            "turma_id": 5
        },
        {
            "nome": "Larissa Vitória Gomes Castro",
            "data_nascimento": date(2009, 5, 20),
            "email": "larissa.gomes@email.com",
            "status": "ativo",
            "turma_id": 6
        },
        {
            "nome": "Matheus Alexandre Dias Moreira",
            "data_nascimento": date(2008, 10, 16),
            "email": "matheus.dias@email.com",
            "status": "ativo",
            "turma_id": 6
        },
        {
            "nome": "Natália Fernanda Cardoso Ribeiro",
            "data_nascimento": date(2007, 1, 25),
            "email": "natalia.cardoso@email.com",
            "status": "ativo",
            "turma_id": 7
        },
        {
            "nome": "Otávio Rafael Correia Nunes",
            "data_nascimento": date(2008, 7, 9),
            "email": "otavio.correia@email.com",
            "status": "ativo",
            "turma_id": 7
        },
        {
            "nome": "Priscila Amanda Teixeira Monteiro",
            "data_nascimento": date(2009, 3, 7),
            "email": "priscila.teixeira@email.com",
            "status": "ativo",
            "turma_id": 8
        },
        {
            "nome": "Rafael Leonardo Vieira Campos",
            "data_nascimento": date(2007, 11, 21),
            "email": "rafael.vieira@email.com",
            "status": "ativo",
            "turma_id": 8
        },
        {
            "nome": "Sofia Helena Nascimento Freitas",
            "data_nascimento": date(2008, 9, 4),
            "email": "sofia.nascimento@email.com",
            "status": "ativo",
            "turma_id": 9
        },
        {
            "nome": "Thiago Gustavo Ramos Machado",
            "data_nascimento": date(2007, 4, 17),
            "email": "thiago.ramos@email.com",
            "status": "ativo",
            "turma_id": 9
        },
        {
            "nome": "Valentina Júlia Carvalho Lopes",
            "data_nascimento": date(2009, 8, 30),
            "email": "valentina.carvalho@email.com",
            "status": "ativo",
            "turma_id": 10
        },
        {
            "nome": "Wellington Victor Melo Torres",
            "data_nascimento": date(2008, 2, 11),
            "email": "wellington.melo@email.com",
            "status": "ativo",
            "turma_id": 10
        },
        # Alguns alunos sem turma (inativos)
        {
            "nome": "Xavier Antônio Pinto Duarte",
            "data_nascimento": date(2007, 6, 19),
            "email": "xavier.pinto@email.com",
            "status": "inativo",
            "turma_id": None
        },
        {
            "nome": "Yasmin Beatriz Moura Santana",
            "data_nascimento": date(2008, 12, 8),
            "email": "yasmin.moura@email.com",
            "status": "inativo",
            "turma_id": None
        },
        {
            "nome": "Zacarias Miguel Cunha Barros",
            "data_nascimento": date(2009, 4, 26),
            "email": "zacarias.cunha@email.com",
            "status": "inativo",
            "turma_id": None
        },
        # Alguns alunos com nomes compostos e sem email
        {
            "nome": "Ana Luiza de Souza e Silva",
            "data_nascimento": date(2008, 5, 14),
            "email": None,
            "status": "ativo",
            "turma_id": 1
        },
        {
            "nome": "José Carlos dos Santos Junior",
            "data_nascimento": date(2007, 10, 23),
            "email": None,
            "status": "ativo",
            "turma_id": 2
        }
    ]
    
    return [Aluno(**aluno_data) for aluno_data in alunos]

def popular_banco():
    """Popular o banco de dados com dados de exemplo"""
    try:
        print("🌱 Iniciando população do banco de dados...")
        
        # Verificar se já existem dados
        with DatabaseTransaction() as db:
            turmas_existentes = db.query(Turma).count()
            alunos_existentes = db.query(Aluno).count()
            
            if turmas_existentes > 0 or alunos_existentes > 0:
                resposta = input(f"⚠️ Já existem {turmas_existentes} turmas e {alunos_existentes} alunos no banco. Deseja continuar? (s/n): ")
                if resposta.lower() not in ['s', 'sim', 'y', 'yes']:
                    print("❌ Operação cancelada pelo usuário")
                    return False
        
        # Criar turmas
        print("📚 Criando turmas...")
        turmas = criar_turmas_exemplo()
        
        with DatabaseTransaction() as db:
            for turma in turmas:
                # Verificar se turma já existe
                turma_existente = db.query(Turma).filter(Turma.nome == turma.nome).first()
                if not turma_existente:
                    db.add(turma)
                    print(f"  ✅ Turma criada: {turma.nome}")
                else:
                    print(f"  ⚠️ Turma já existe: {turma.nome}")
        
        # Criar alunos
        print("👥 Criando alunos...")
        alunos = criar_alunos_exemplo()
        
        with DatabaseTransaction() as db:
            for aluno in alunos:
                # Verificar se aluno já existe (por email ou nome)
                aluno_existente = db.query(Aluno).filter(
                    (Aluno.email == aluno.email) if aluno.email else (Aluno.nome == aluno.nome)
                ).first()
                
                if not aluno_existente:
                    db.add(aluno)
                    turma_nome = ""
                    if aluno.turma_id:
                        turma = db.query(Turma).filter(Turma.id == aluno.turma_id).first()
                        turma_nome = f" (Turma: {turma.nome})" if turma else " (Turma não encontrada)"
                    print(f"  ✅ Aluno criado: {aluno.nome}{turma_nome}")
                else:
                    print(f"  ⚠️ Aluno já existe: {aluno.nome}")
        
        # Estatísticas finais
        with DatabaseTransaction() as db:
            total_turmas = db.query(Turma).count()
            total_alunos = db.query(Aluno).count()
            alunos_ativos = db.query(Aluno).filter(Aluno.status == "ativo").count()
            alunos_inativos = db.query(Aluno).filter(Aluno.status == "inativo").count()
            
            print("\n📊 Estatísticas do banco de dados:")
            print(f"   📚 Total de turmas: {total_turmas}")
            print(f"   👥 Total de alunos: {total_alunos}")
            print(f"   ✅ Alunos ativos: {alunos_ativos}")
            print(f"   ❌ Alunos inativos: {alunos_inativos}")
            
            # Estatísticas por turma
            print("\n📋 Ocupação por turma:")
            turmas_db = db.query(Turma).all()
            for turma in turmas_db:
                ocupacao = db.query(Aluno).filter(Aluno.turma_id == turma.id).count()
                percentual = (ocupacao / turma.capacidade) * 100 if turma.capacidade > 0 else 0
                print(f"   {turma.nome}: {ocupacao}/{turma.capacidade} ({percentual:.1f}%)")
        
        print("\n🎉 Banco de dados populado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao popular banco de dados: {e}")
        return False

def limpar_banco():
    """Limpar todos os dados do banco"""
    try:
        with DatabaseTransaction() as db:
            # Contar registros antes
            total_alunos = db.query(Aluno).count()
            total_turmas = db.query(Turma).count()
            
            if total_alunos == 0 and total_turmas == 0:
                print("ℹ️ Banco de dados já está vazio")
                return True
            
            resposta = input(f"⚠️ Isso irá apagar {total_alunos} alunos e {total_turmas} turmas. Continuar? (s/n): ")
            if resposta.lower() not in ['s', 'sim', 'y', 'yes']:
                print("❌ Operação cancelada pelo usuário")
                return False
            
            # Apagar alunos primeiro (devido à foreign key)
            db.query(Aluno).delete()
            print(f"🗑️ {total_alunos} alunos removidos")
            
            # Apagar turmas
            db.query(Turma).delete()
            print(f"🗑️ {total_turmas} turmas removidas")
            
            print("✅ Banco de dados limpo com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao limpar banco de dados: {e}")
        return False

def verificar_integridade():
    """Verificar integridade dos dados"""
    try:
        print("🔍 Verificando integridade dos dados...")
        
        with DatabaseTransaction() as db:
            # Verificar alunos órfãos (com turma_id que não existe)
            alunos_orfaos = db.query(Aluno).filter(
                Aluno.turma_id.isnot(None),
                ~Aluno.turma_id.in_(db.query(Turma.id))
            ).all()
            
            if alunos_orfaos:
                print(f"⚠️ Encontrados {len(alunos_orfaos)} alunos com turma inexistente:")
                for aluno in alunos_orfaos:
                    print(f"   - {aluno.nome} (turma_id: {aluno.turma_id})")
            
            # Verificar turmas superlotadas
            turmas = db.query(Turma).all()
            turmas_superlotadas = []
            
            for turma in turmas:
                ocupacao = db.query(Aluno).filter(Aluno.turma_id == turma.id).count()
                if ocupacao > turma.capacidade:
                    turmas_superlotadas.append((turma, ocupacao))
            
            if turmas_superlotadas:
                print(f"⚠️ Encontradas {len(turmas_superlotadas)} turmas superlotadas:")
                for turma, ocupacao in turmas_superlotadas:
                    print(f"   - {turma.nome}: {ocupacao}/{turma.capacidade}")
            
            # Verificar emails duplicados
            emails_duplicados = db.query(Aluno.email).filter(
                Aluno.email.isnot(None)
            ).group_by(Aluno.email).having(db.func.count(Aluno.email) > 1).all()
            
            if emails_duplicados:
                print(f"⚠️ Encontrados {len(emails_duplicados)} emails duplicados:")
                for email in emails_duplicados:
                    alunos_com_email = db.query(Aluno).filter(Aluno.email == email[0]).all()
                    print(f"   - {email[0]}: {[a.nome for a in alunos_com_email]}")
            
            if not alunos_orfaos and not turmas_superlotadas and not emails_duplicados:
                print("✅ Integridade dos dados OK!")
                return True
            else:
                return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar integridade: {e}")
        return False

def menu_principal():
    """Menu principal do script"""
    while True:
        print("\n" + "="*50)
        print("🏫 SISTEMA DE GESTÃO ESCOLAR - SEED DATA")
        print("="*50)
        print("1. 🌱 Popular banco com dados de exemplo")
        print("2. 🗑️ Limpar todos os dados")
        print("3. 🔍 Verificar integridade dos dados")
        print("4. 📊 Mostrar estatísticas")
        print("5. 🔄 Resetar banco (limpar + popular)")
        print("6. ❌ Sair")
        print("="*50)
        
        try:
            opcao = input("Escolha uma opção (1-6): ").strip()
            
            if opcao == "1":
                popular_banco()
            elif opcao == "2":
                limpar_banco()
            elif opcao == "3":
                verificar_integridade()
            elif opcao == "4":
                mostrar_estatisticas()
            elif opcao == "5":
                print("🔄 Resetando banco de dados...")
                if limpar_banco():
                    popular_banco()
            elif opcao == "6":
                print("👋 Até logo!")
                break
            else:
                print("❌ Opção inválida! Escolha entre 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

def mostrar_estatisticas():
    """Mostrar estatísticas do banco de dados"""
    try:
        with DatabaseTransaction() as db:
            total_turmas = db.query(Turma).count()
            total_alunos = db.query(Aluno).count()
            alunos_ativos = db.query(Aluno).filter(Aluno.status == "ativo").count()
            alunos_inativos = db.query(Aluno).filter(Aluno.status == "inativo").count()
            alunos_sem_turma = db.query(Aluno).filter(Aluno.turma_id.is_(None)).count()
            
            print("\n📊 ESTATÍSTICAS DO SISTEMA")
            print("="*40)
            print(f"📚 Total de turmas: {total_turmas}")
            print(f"👥 Total de alunos: {total_alunos}")
            print(f"✅ Alunos ativos: {alunos_ativos}")
            print(f"❌ Alunos inativos: {alunos_inativos}")
            print(f"🚫 Alunos sem turma: {alunos_sem_turma}")
            
            if total_turmas > 0:
                print("\n📋 OCUPAÇÃO POR TURMA:")
                print("-" * 40)
                turmas = db.query(Turma).order_by(Turma.nome).all()
                
                for turma in turmas:
                    ocupacao = db.query(Aluno).filter(Aluno.turma_id == turma.id).count()
                    percentual = (ocupacao / turma.capacidade) * 100 if turma.capacidade > 0 else 0
                    
                    # Indicador visual
                    if percentual >= 90:
                        indicador = "🔴"
                    elif percentual >= 70:
                        indicador = "🟡"
                    else:
                        indicador = "🟢"
                    
                    print(f"{indicador} {turma.nome:<15} {ocupacao:>2}/{turma.capacidade:<2} ({percentual:>5.1f}%)")
            
            print("="*40)
            
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")

if __name__ == "__main__":
    try:
        # Inicializar banco de dados
        print("🚀 Inicializando sistema...")
        init_db()
        
        # Executar menu principal
        menu_principal()
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)
