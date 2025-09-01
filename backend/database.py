# Configuração do banco de dados MySQL para o Sistema de Gestão Escolar
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import os
from models import Base

# Configuração do banco de dados MySQL
# Para XAMPP: usuario=root, senha=vazia, host=localhost, porta=3306
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/escola_db"

# Fallback para SQLite se MySQL não estiver disponível
SQLITE_URL = "sqlite:///./app.db"

# Criar engine do SQLAlchemy com tentativa de conexão MySQL
try:
    # Tentar conectar ao MySQL primeiro
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Definir como True para ver queries SQL no console
        pool_pre_ping=True,  # Verificar conexão antes de usar
        pool_recycle=3600  # Renovar conexões a cada hora
    )
    
    # Testar conexão
    engine.connect()
    print("✅ Conectado ao MySQL com sucesso!")
    
except Exception as e:
    print(f"⚠️ Erro ao conectar MySQL: {e}")
    print("🔄 Usando SQLite como fallback...")
    
    # Usar SQLite como fallback
    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},  # Necessário para SQLite
        echo=False
    )
    DATABASE_URL = SQLITE_URL

# Criar SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Criar todas as tabelas no banco de dados"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
    except SQLAlchemyError as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        raise

def init_db():
    """Inicializar o banco de dados"""
    try:
        # Verificar se o arquivo de banco existe
        db_exists = os.path.exists("app.db")
        
        if not db_exists:
            print("📊 Criando novo banco de dados...")
        else:
            print("📊 Conectando ao banco de dados existente...")
        
        # Criar tabelas
        create_tables()
        
        print("🚀 Banco de dados inicializado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        raise

def get_db() -> Session:
    """
    Dependency para obter sessão do banco de dados
    Usado como dependência no FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_db_session() -> Session:
    """
    Obter sessão do banco de dados para uso direto
    (fora do contexto FastAPI)
    """
    return SessionLocal()

def close_db_session(db: Session):
    """Fechar sessão do banco de dados"""
    try:
        db.close()
    except Exception as e:
        print(f"Erro ao fechar sessão: {e}")

def reset_database():
    """
    Resetar o banco de dados (apagar todas as tabelas e recriar)
    ⚠️ CUIDADO: Esta operação apaga todos os dados!
    """
    try:
        print("⚠️ Resetando banco de dados...")
        
        # Apagar todas as tabelas
        Base.metadata.drop_all(bind=engine)
        print("🗑️ Tabelas removidas")
        
        # Recriar todas as tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas recriadas")
        
        print("🔄 Banco de dados resetado com sucesso!")
        
    except SQLAlchemyError as e:
        print(f"❌ Erro ao resetar banco de dados: {e}")
        raise

def check_database_connection():
    """Verificar se a conexão com o banco está funcionando"""
    try:
        db = SessionLocal()
        # Executar uma query simples para testar a conexão
        db.execute("SELECT 1")
        db.close()
        print("✅ Conexão com banco de dados OK")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão com banco de dados: {e}")
        return False

def get_database_info():
    """Obter informações sobre o banco de dados"""
    try:
        db = SessionLocal()
        
        # Verificar se as tabelas existem
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        info = {
            "database_url": DATABASE_URL,
            "database_file": "app.db",
            "file_exists": os.path.exists("app.db"),
            "tables": tables,
            "engine_info": str(engine.url)
        }
        
        if os.path.exists("app.db"):
            file_size = os.path.getsize("app.db")
            info["file_size_bytes"] = file_size
            info["file_size_mb"] = round(file_size / 1024 / 1024, 2)
        
        db.close()
        return info
        
    except Exception as e:
        return {"error": str(e)}

# Função para backup do banco de dados
def backup_database(backup_path: str = None):
    """Criar backup do banco de dados"""
    import shutil
    from datetime import datetime
    
    try:
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_app_{timestamp}.db"
        
        if os.path.exists("app.db"):
            shutil.copy2("app.db", backup_path)
            print(f"✅ Backup criado: {backup_path}")
            return backup_path
        else:
            print("❌ Arquivo de banco não encontrado")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return None

# Função para restaurar backup
def restore_database(backup_path: str):
    """Restaurar banco de dados a partir de backup"""
    import shutil
    
    try:
        if not os.path.exists(backup_path):
            print(f"❌ Arquivo de backup não encontrado: {backup_path}")
            return False
        
        # Fazer backup do arquivo atual (se existir)
        if os.path.exists("app.db"):
            backup_current = backup_database("app_before_restore.db")
            print(f"📦 Backup atual salvo em: {backup_current}")
        
        # Restaurar backup
        shutil.copy2(backup_path, "app.db")
        print(f"✅ Banco restaurado de: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao restaurar backup: {e}")
        return False

# Contexto manager para transações
class DatabaseTransaction:
    """Context manager para gerenciar transações do banco"""
    
    def __init__(self):
        self.db = None
    
    def __enter__(self):
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Se houve exceção, fazer rollback
            self.db.rollback()
            print(f"❌ Transação cancelada: {exc_val}")
        else:
            # Se não houve exceção, fazer commit
            self.db.commit()
        
        self.db.close()

# Exemplo de uso do context manager:
# with DatabaseTransaction() as db:
#     # Operações no banco
#     aluno = Aluno(nome="Teste")
#     db.add(aluno)
#     # Commit automático se não houver erro, rollback se houver
