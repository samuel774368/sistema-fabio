#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import pymysql
import uvicorn
from datetime import date, datetime
import hashlib
import jwt
import os

# Modelos Pydantic
class UsuarioLogin(BaseModel):
    username: str
    password: str

class UsuarioCreate(BaseModel):
    username: str
    email: str
    password: str
    tipo_usuario: str = "usuario"

class UsuarioResponse(BaseModel):
    id: int
    username: str
    email: str
    tipo_usuario: str
    ativo: bool

class PerfilUsuario(BaseModel):
    id: int
    username: str
    email: str
    tipo_usuario: str
    data_criacao: str
    ultimo_login: str
    tempo_login_atual: str
    total_alunos_cadastrados: int
    total_matriculas_realizadas: int
    sessoes_ativas: int

class AlunoBase(BaseModel):
    nome: str
    data_nascimento: date
    email: Optional[str] = None
    status: str = "ativo"
    turma_id: Optional[int] = None

class AlunoCreate(AlunoBase):
    pass

class Aluno(AlunoBase):
    id: int

class TurmaBase(BaseModel):
    nome: str
    capacidade: int

class TurmaCreate(TurmaBase):
    pass

class Turma(TurmaBase):
    id: int

# Configuração do banco e JWT
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': '',
    'database': 'escola_db',
    'charset': 'utf8mb4'
}

SECRET_KEY = "escola_secretkey_2025_fabio_sistema"
ALGORITHM = "HS256"

# Security
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Cria hash da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    return hash_password(password) == hashed_password

def create_access_token(user_id: int, username: str, tipo_usuario: str):
    """Cria token JWT"""
    payload = {
        "user_id": user_id,
        "username": username,
        "tipo_usuario": tipo_usuario,
        "exp": datetime.utcnow().timestamp() + 3600 * 24  # 24 horas
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_db_connection():
    """Cria conexão com o banco"""
    return pymysql.connect(**DB_CONFIG)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica token JWT e retorna usuário atual"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        username = payload.get("username")
        tipo_usuario = payload.get("tipo_usuario")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
            
        return {
            "id": user_id,
            "username": username,
            "tipo_usuario": tipo_usuario
        }
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")

def require_admin(current_user: dict = Depends(get_current_user)):
    """Verifica se o usuário é administrador"""
    if current_user["tipo_usuario"] != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores.")
    return current_user

# Criar app FastAPI
app = FastAPI(title="Sistema Escolar")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Inicializar banco de dados e criar tabelas"""
    try:
        connection = get_db_connection()
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
            
            # Criar admin padrão
            admin_password = hash_password('admin123')
            cursor.execute("""
            INSERT IGNORE INTO usuarios (username, email, senha_hash, tipo_usuario) 
            VALUES ('admin', 'admin@escola.com', %s, 'admin')
            """, (admin_password,))
            
            connection.commit()
            print("✅ Tabela usuarios inicializada!")
        connection.close()
    except Exception as e:
        print(f"❌ Erro na inicialização do banco: {e}")

# ENDPOINTS DE AUTENTICAÇÃO
@app.post("/login")
async def login(usuario: UsuarioLogin):
    """Login do usuário"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, senha_hash, tipo_usuario, ativo 
                FROM usuarios WHERE username=%s AND ativo=1
            """, (usuario.username,))
            
            user_data = cursor.fetchone()
            if not user_data:
                raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
            
            user_id, username, email, senha_hash, tipo_usuario, ativo = user_data
            
            if not verify_password(usuario.password, senha_hash):
                raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
            
            # Atualizar último login
            cursor.execute("UPDATE usuarios SET ultimo_login=NOW() WHERE id=%s", (user_id,))
            connection.commit()
            
            # Criar token
            token = create_access_token(user_id, username, tipo_usuario)
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user_id,
                    "username": username,
                    "email": email,
                    "tipo_usuario": tipo_usuario
                }
            }
    finally:
        connection.close()

@app.post("/register")
async def register(usuario: UsuarioCreate):
    """Registro de novo usuário"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar se usuário já existe
            cursor.execute("SELECT id FROM usuarios WHERE username=%s OR email=%s", 
                         (usuario.username, usuario.email))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Usuário ou email já existe")
            
            # Criar usuário
            senha_hash = hash_password(usuario.password)
            cursor.execute("""
                INSERT INTO usuarios (username, email, senha_hash, tipo_usuario) 
                VALUES (%s, %s, %s, %s)
            """, (usuario.username, usuario.email, senha_hash, usuario.tipo_usuario))
            
            connection.commit()
            user_id = cursor.lastrowid
            
            return {
                "message": "Usuário criado com sucesso",
                "user": {
                    "id": user_id,
                    "username": usuario.username,
                    "email": usuario.email,
                    "tipo_usuario": usuario.tipo_usuario
                }
            }
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@app.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Informações do usuário atual"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, tipo_usuario, ativo, data_criacao, ultimo_login
                FROM usuarios WHERE id=%s
            """, (current_user["id"],))
            
            user_data = cursor.fetchone()
            if not user_data:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
            return {
                "id": user_data[0],
                "username": user_data[1],
                "email": user_data[2],
                "tipo_usuario": user_data[3],
                "ativo": user_data[4],
                "data_criacao": user_data[5],
                "ultimo_login": user_data[6]
            }
    finally:
        connection.close()

@app.get("/perfil", response_model=PerfilUsuario)
async def get_perfil_completo(current_user: dict = Depends(get_current_user)):
    """Perfil completo do usuário com estatísticas"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Buscar dados do usuário
            cursor.execute("""
                SELECT id, username, email, tipo_usuario, data_criacao, ultimo_login
                FROM usuarios WHERE id=%s
            """, (current_user["id"],))
            
            user_data = cursor.fetchone()
            if not user_data:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
            # Calcular tempo de login atual (desde o último login até agora)
            tempo_login = "Primeira sessão"
            if user_data[5]:  # ultimo_login
                agora = datetime.now()
                ultimo_login = user_data[5]
                if isinstance(ultimo_login, str):
                    ultimo_login = datetime.fromisoformat(ultimo_login)
                delta = agora - ultimo_login
                horas = int(delta.total_seconds() // 3600)
                minutos = int((delta.total_seconds() % 3600) // 60)
                tempo_login = f"{horas}h {minutos}min"
            
            # Contar alunos cadastrados (se for admin)
            total_alunos = 0
            if user_data[3] == 'admin':  # Se for admin
                cursor.execute("SELECT COUNT(*) FROM alunos")
                result = cursor.fetchone()
                total_alunos = result[0] if result else 0
            
            # Contar matrículas (se existir tabela de matrículas)
            total_matriculas = 0
            try:
                cursor.execute("SELECT COUNT(*) FROM matriculas")
                result = cursor.fetchone()
                total_matriculas = result[0] if result else 0
            except:
                total_matriculas = 0
            
            return PerfilUsuario(
                id=user_data[0],
                username=user_data[1],
                email=user_data[2],
                tipo_usuario=user_data[3],
                data_criacao=user_data[4].strftime("%d/%m/%Y %H:%M") if user_data[4] else "N/A",
                ultimo_login=user_data[5].strftime("%d/%m/%Y %H:%M") if user_data[5] else "Nunca",
                tempo_login_atual=tempo_login,
                total_alunos_cadastrados=total_alunos,
                total_matriculas_realizadas=total_matriculas,
                sessoes_ativas=1  # Sempre 1 pois está logado
            )
    finally:
        connection.close()

# ENDPOINTS ALUNOS (Protegidos)
@app.get("/alunos", response_model=List[Aluno])
async def listar_alunos(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, nome, data_nascimento, email, status, turma_id FROM alunos ORDER BY nome")
            alunos = cursor.fetchall()
            
            result = []
            for aluno in alunos:
                result.append({
                    "id": aluno[0],
                    "nome": aluno[1],
                    "data_nascimento": aluno[2],
                    "email": aluno[3],
                    "status": aluno[4],
                    "turma_id": aluno[5]
                })
            return result
    finally:
        connection.close()

@app.post("/alunos", response_model=Aluno)
async def criar_aluno(aluno: AlunoCreate, admin_user: dict = Depends(require_admin)):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO alunos (nome, data_nascimento, email, status, turma_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (aluno.nome, aluno.data_nascimento, aluno.email, aluno.status, aluno.turma_id))
            connection.commit()
            aluno_id = cursor.lastrowid
            
            return {
                "id": aluno_id,
                "nome": aluno.nome,
                "data_nascimento": aluno.data_nascimento,
                "email": aluno.email,
                "status": aluno.status,
                "turma_id": aluno.turma_id
            }
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@app.put("/alunos/{aluno_id}", response_model=Aluno)
async def atualizar_aluno(aluno_id: int, aluno: AlunoCreate, admin_user: dict = Depends(require_admin)):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE alunos SET nome=%s, data_nascimento=%s, email=%s, status=%s, turma_id=%s WHERE id=%s"
            cursor.execute(sql, (aluno.nome, aluno.data_nascimento, aluno.email, aluno.status, aluno.turma_id, aluno_id))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Aluno não encontrado")
                
            connection.commit()
            
            return {
                "id": aluno_id,
                "nome": aluno.nome,
                "data_nascimento": aluno.data_nascimento,
                "email": aluno.email,
                "status": aluno.status,
                "turma_id": aluno.turma_id
            }
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@app.delete("/alunos/{aluno_id}")
async def deletar_aluno(aluno_id: int, admin_user: dict = Depends(require_admin)):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM alunos WHERE id=%s", (aluno_id,))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Aluno não encontrado")
                
            connection.commit()
            return {"message": "Aluno deletado com sucesso"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

# ENDPOINTS TURMAS (Protegidos)
@app.get("/turmas", response_model=List[Turma])
async def listar_turmas(current_user: dict = Depends(get_current_user)):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, nome, capacidade FROM turmas ORDER BY nome")
            turmas = cursor.fetchall()
            
            result = []
            for turma in turmas:
                result.append({
                    "id": turma[0],
                    "nome": turma[1],
                    "capacidade": turma[2]
                })
            return result
    finally:
        connection.close()

@app.post("/turmas", response_model=Turma)
async def criar_turma(turma: TurmaCreate, admin_user: dict = Depends(require_admin)):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO turmas (nome, capacidade) VALUES (%s, %s)"
            cursor.execute(sql, (turma.nome, turma.capacidade))
            connection.commit()
            
            turma_id = cursor.lastrowid
            
            return {
                "id": turma_id,
                "nome": turma.nome,
                "capacidade": turma.capacidade
            }
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@app.put("/turmas/{turma_id}", response_model=Turma)
async def atualizar_turma(turma_id: int, turma: TurmaCreate, admin_user: dict = Depends(require_admin)):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE turmas SET nome=%s, capacidade=%s WHERE id=%s"
            cursor.execute(sql, (turma.nome, turma.capacidade, turma_id))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Turma não encontrada")
                
            connection.commit()
            
            return {
                "id": turma_id,
                "nome": turma.nome,
                "capacidade": turma.capacidade
            }
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@app.delete("/turmas/{turma_id}")
async def deletar_turma(turma_id: int, admin_user: dict = Depends(require_admin)):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM turmas WHERE id=%s", (turma_id,))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Turma não encontrada")
                
            connection.commit()
            
            return {"message": "Turma deletada com sucesso"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()

@app.get("/")
async def root():
    return {"message": "Sistema Escolar API - Funcionando!"}

@app.get("/test-db")
async def test_db():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM alunos")
            count = cursor.fetchone()[0]
        connection.close()
        return {"status": "OK", "alunos": count}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
