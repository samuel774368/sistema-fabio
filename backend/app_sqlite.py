#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
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

class ProfessorBase(BaseModel):
    nome: str
    email: str
    especialidade: str
    telefone: Optional[str] = None
    status: str = "ativo"

class ProfessorCreate(ProfessorBase):
    pass

class Professor(ProfessorBase):
    id: int

class VinculacaoBase(BaseModel):
    usuario_id: int
    aluno_id: int
    tipo_vinculo: str = "responsavel"  # responsavel, pai, mae, tutor

class VinculacaoCreate(VinculacaoBase):
    pass

class Vinculacao(VinculacaoBase):
    id: int

class SolicitacaoMatriculaBase(BaseModel):
    nome_aluno: str
    data_nascimento: date
    email_aluno: Optional[str] = None
    observacoes: Optional[str] = None
    turma_solicitada: Optional[str] = None

class SolicitacaoMatriculaCreate(SolicitacaoMatriculaBase):
    pass

class SolicitacaoMatricula(SolicitacaoMatriculaBase):
    id: int
    usuario_id: int
    status: str  # 'pendente', 'aprovada', 'rejeitada'
    data_solicitacao: str
    data_resposta: Optional[str] = None
    resposta_admin: Optional[str] = None
    aluno_id: Optional[int] = None  # ID do aluno criado se aprovado

# Configuração do banco e JWT
DB_PATH = "escola.db"
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
    """Cria conexão com o banco SQLite"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

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

def init_database():
    """Inicializar banco de dados e criar tabelas"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Criar tabela usuarios
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                senha_hash VARCHAR(64) NOT NULL,
                tipo_usuario TEXT DEFAULT 'usuario',
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_login TIMESTAMP NULL
            )
            """)
            
            # Criar tabela turmas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS turmas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(100) NOT NULL UNIQUE,
                capacidade INTEGER NOT NULL
            )
            """)
            
            # Criar tabela alunos
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(80) NOT NULL,
                data_nascimento DATE NOT NULL,
                email VARCHAR(120) UNIQUE NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'ativo',
                turma_id INTEGER NULL,
                FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE SET NULL
            )
            """)
            
            # Criar tabela professores
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS professores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                especialidade VARCHAR(100) NOT NULL,
                telefone VARCHAR(20) NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'ativo',
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Criar tabela de vinculações (usuários -> alunos)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vinculacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                aluno_id INTEGER NOT NULL,
                tipo_vinculo VARCHAR(20) DEFAULT 'responsavel',
                data_vinculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
                UNIQUE(usuario_id, aluno_id)
            )
            """)
            
            # Criar tabela de solicitações de matrícula
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS solicitacoes_matricula (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                nome_aluno VARCHAR(100) NOT NULL,
                data_nascimento DATE NOT NULL,
                email_aluno VARCHAR(120) NULL,
                observacoes TEXT NULL,
                turma_solicitada VARCHAR(100) NULL,
                status VARCHAR(20) DEFAULT 'pendente',
                data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_resposta TIMESTAMP NULL,
                resposta_admin TEXT NULL,
                aluno_id INTEGER NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE SET NULL
            )
            """)
            
            # Criar admin padrão
            admin_password = hash_password('admin123')
            cursor.execute("""
            INSERT OR IGNORE INTO usuarios (username, email, senha_hash, tipo_usuario) 
            VALUES (?, ?, ?, ?)
            """, ('admin', 'admin@escola.com', admin_password, 'admin'))
            
            # Inserir algumas turmas de exemplo
            turmas_exemplo = [
                ("1º Ano A", 30),
                ("2º Ano A", 28),
                ("3º Ano A", 25)
            ]
            
            for nome, capacidade in turmas_exemplo:
                cursor.execute("""
                INSERT OR IGNORE INTO turmas (nome, capacidade) 
                VALUES (?, ?)
                """, (nome, capacidade))
            
            # Inserir alguns alunos de exemplo
            alunos_exemplo = [
                ("Ana Silva", "2010-03-15", "ana@email.com", "ativo", 1),
                ("Bruno Santos", "2009-07-22", "bruno@email.com", "ativo", 1),
                ("Carla Costa", "2008-01-10", "carla@email.com", "ativo", 2),
                ("Diego Oliveira", "2007-11-05", "diego@email.com", "ativo", 2),
                ("Elena Lima", "2006-09-18", "elena@email.com", "ativo", 3)
            ]
            
            for nome, data_nasc, email, status, turma_id in alunos_exemplo:
                cursor.execute("""
                INSERT OR IGNORE INTO alunos (nome, data_nascimento, email, status, turma_id) 
                VALUES (?, ?, ?, ?, ?)
                """, (nome, data_nasc, email, status, turma_id))
            
            # Inserir professores de exemplo
            professores_exemplo = [
                ("Prof. Maria João", "maria.joao@escola.com", "Matemática", "(11) 99999-1111", "ativo"),
                ("Prof. Carlos Silva", "carlos.silva@escola.com", "Português", "(11) 99999-2222", "ativo"),
                ("Prof. Ana Beatriz", "ana.beatriz@escola.com", "História", "(11) 99999-3333", "ativo"),
                ("Prof. João Pedro", "joao.pedro@escola.com", "Geografia", "(11) 99999-4444", "ativo"),
                ("Prof. Fernanda Lima", "fernanda.lima@escola.com", "Ciências", "(11) 99999-5555", "ativo")
            ]
            
            for nome, email, especialidade, telefone, status in professores_exemplo:
                cursor.execute("""
                INSERT OR IGNORE INTO professores (nome, email, especialidade, telefone, status) 
                VALUES (?, ?, ?, ?, ?)
                """, (nome, email, especialidade, telefone, status))
            
            # Criar usuários pais de exemplo
            usuarios_pais = [
                ("pai_ana", "pai.ana@email.com", hash_password("123456"), "usuario"),
                ("mae_bruno", "mae.bruno@email.com", hash_password("123456"), "usuario"),
                ("resp_carla", "resp.carla@email.com", hash_password("123456"), "usuario")
            ]
            
            for username, email, senha_hash, tipo in usuarios_pais:
                cursor.execute("""
                INSERT OR IGNORE INTO usuarios (username, email, senha_hash, tipo_usuario) 
                VALUES (?, ?, ?, ?)
                """, (username, email, senha_hash, tipo))
            
            conn.commit()
            print("✅ Banco SQLite inicializado com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro na inicialização do banco: {e}")

@app.on_event("startup")
async def startup_event():
    init_database()

# ENDPOINTS DE AUTENTICAÇÃO
@app.post("/login")
async def login(usuario: UsuarioLogin):
    """Login do usuário"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, senha_hash, tipo_usuario, ativo 
            FROM usuarios WHERE username=? AND ativo=1
        """, (usuario.username,))
        
        user_data = cursor.fetchone()
        if not user_data:
            raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
        
        user_id, username, email, senha_hash, tipo_usuario, ativo = user_data
        
        if not verify_password(usuario.password, senha_hash):
            raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
        
        # Atualizar último login
        cursor.execute("UPDATE usuarios SET ultimo_login=datetime('now') WHERE id=?", (user_id,))
        conn.commit()
        
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

@app.post("/register")
async def register(usuario: UsuarioCreate):
    """Registro de novo usuário"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Verificar se usuário já existe
        cursor.execute("SELECT id FROM usuarios WHERE username=? OR email=?", 
                     (usuario.username, usuario.email))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Usuário ou email já existe")
        
        # Criar usuário
        senha_hash = hash_password(usuario.password)
        cursor.execute("""
            INSERT INTO usuarios (username, email, senha_hash, tipo_usuario) 
            VALUES (?, ?, ?, ?)
        """, (usuario.username, usuario.email, senha_hash, usuario.tipo_usuario))
        
        conn.commit()
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

@app.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Informações do usuário atual"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, tipo_usuario, ativo, data_criacao, ultimo_login
            FROM usuarios WHERE id=?
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

@app.get("/perfil", response_model=PerfilUsuario)
async def get_perfil_completo(current_user: dict = Depends(get_current_user)):
    """Perfil completo do usuário com estatísticas"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Buscar dados do usuário
        cursor.execute("""
            SELECT id, username, email, tipo_usuario, data_criacao, ultimo_login
            FROM usuarios WHERE id=?
        """, (current_user["id"],))
        
        user_data = cursor.fetchone()
        if not user_data:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Calcular tempo de login atual
        tempo_login = "Primeira sessão"
        if user_data[5]:
            try:
                agora = datetime.now()
                ultimo_login = datetime.fromisoformat(user_data[5].replace('Z', '+00:00'))
                delta = agora - ultimo_login
                horas = int(delta.total_seconds() // 3600)
                minutos = int((delta.total_seconds() % 3600) // 60)
                tempo_login = f"{horas}h {minutos}min"
            except:
                tempo_login = "N/A"
        
        # Contar alunos cadastrados
        total_alunos = 0
        if user_data[3] == 'admin':
            cursor.execute("SELECT COUNT(*) FROM alunos")
            result = cursor.fetchone()
            total_alunos = result[0] if result else 0
        
        return PerfilUsuario(
            id=user_data[0],
            username=user_data[1],
            email=user_data[2],
            tipo_usuario=user_data[3],
            data_criacao=user_data[4] or "N/A",
            ultimo_login=user_data[5] or "Nunca",
            tempo_login_atual=tempo_login,
            total_alunos_cadastrados=total_alunos,
            total_matriculas_realizadas=0,
            sessoes_ativas=1
        )

# ENDPOINTS ALUNOS (Protegidos)
@app.get("/alunos", response_model=List[Aluno])
async def listar_alunos(current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
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

@app.post("/alunos", response_model=Aluno)
async def criar_aluno(aluno: AlunoCreate, admin_user: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alunos (nome, data_nascimento, email, status, turma_id) VALUES (?, ?, ?, ?, ?)",
            (aluno.nome, aluno.data_nascimento, aluno.email, aluno.status, aluno.turma_id)
        )
        conn.commit()
        aluno_id = cursor.lastrowid
        
        return {
            "id": aluno_id,
            "nome": aluno.nome,
            "data_nascimento": aluno.data_nascimento,
            "email": aluno.email,
            "status": aluno.status,
            "turma_id": aluno.turma_id
        }

@app.put("/alunos/{aluno_id}", response_model=Aluno)
async def atualizar_aluno(aluno_id: int, aluno: AlunoCreate, admin_user: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE alunos SET nome=?, data_nascimento=?, email=?, status=?, turma_id=? WHERE id=?",
            (aluno.nome, aluno.data_nascimento, aluno.email, aluno.status, aluno.turma_id, aluno_id)
        )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
            
        conn.commit()
        
        return {
            "id": aluno_id,
            "nome": aluno.nome,
            "data_nascimento": aluno.data_nascimento,
            "email": aluno.email,
            "status": aluno.status,
            "turma_id": aluno.turma_id
        }

@app.delete("/alunos/{aluno_id}")
async def deletar_aluno(aluno_id: int, admin_user: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alunos WHERE id=?", (aluno_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
            
        conn.commit()
        return {"message": "Aluno deletado com sucesso"}

# ENDPOINTS TURMAS (Protegidos)
@app.get("/turmas", response_model=List[Turma])
async def listar_turmas(current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
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

@app.post("/turmas", response_model=Turma)
async def criar_turma(turma: TurmaCreate, admin_user: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO turmas (nome, capacidade) VALUES (?, ?)", (turma.nome, turma.capacidade))
        conn.commit()
        
        turma_id = cursor.lastrowid
        
        return {
            "id": turma_id,
            "nome": turma.nome,
            "capacidade": turma.capacidade
        }

@app.put("/turmas/{turma_id}", response_model=Turma)
async def atualizar_turma(turma_id: int, turma: TurmaCreate, admin_user: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE turmas SET nome=?, capacidade=? WHERE id=?", (turma.nome, turma.capacidade, turma_id))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
            
        conn.commit()
        
        return {
            "id": turma_id,
            "nome": turma.nome,
            "capacidade": turma.capacidade
        }

@app.delete("/turmas/{turma_id}")
async def deletar_turma(turma_id: int, admin_user: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM turmas WHERE id=?", (turma_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
            
        conn.commit()
        
        return {"message": "Turma deletada com sucesso"}

# ENDPOINTS PROFESSORES (Protegidos)
@app.get("/professores", response_model=List[Professor])
async def listar_professores(current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, especialidade, telefone, status FROM professores ORDER BY nome")
        professores = cursor.fetchall()
        
        result = []
        for prof in professores:
            result.append({
                "id": prof[0],
                "nome": prof[1],
                "email": prof[2],
                "especialidade": prof[3],
                "telefone": prof[4],
                "status": prof[5]
            })
        return result

@app.post("/professores", response_model=Professor)
async def criar_professor(professor: ProfessorCreate, admin_user: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO professores (nome, email, especialidade, telefone, status) VALUES (?, ?, ?, ?, ?)",
            (professor.nome, professor.email, professor.especialidade, professor.telefone, professor.status)
        )
        conn.commit()
        professor_id = cursor.lastrowid
        
        return {
            "id": professor_id,
            "nome": professor.nome,
            "email": professor.email,
            "especialidade": professor.especialidade,
            "telefone": professor.telefone,
            "status": professor.status
        }

@app.put("/professores/{professor_id}", response_model=Professor)
async def atualizar_professor(professor_id: int, professor: ProfessorCreate, admin_user: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE professores SET nome=?, email=?, especialidade=?, telefone=?, status=? WHERE id=?",
            (professor.nome, professor.email, professor.especialidade, professor.telefone, professor.status, professor_id)
        )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Professor não encontrado")
            
        conn.commit()
        
        return {
            "id": professor_id,
            "nome": professor.nome,
            "email": professor.email,
            "especialidade": professor.especialidade,
            "telefone": professor.telefone,
            "status": professor.status
        }

@app.delete("/professores/{professor_id}")
async def deletar_professor(professor_id: int, admin_user: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM professores WHERE id=?", (professor_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Professor não encontrado")
            
        conn.commit()
        return {"message": "Professor deletado com sucesso"}

# ENDPOINTS VINCULAÇÕES (Protegidos)
@app.get("/vinculacoes")
async def listar_vinculacoes(admin_user: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.id, v.usuario_id, u.username, v.aluno_id, a.nome, v.tipo_vinculo
            FROM vinculacoes v
            JOIN usuarios u ON v.usuario_id = u.id
            JOIN alunos a ON v.aluno_id = a.id
            ORDER BY u.username, a.nome
        """)
        vinculacoes = cursor.fetchall()
        
        result = []
        for v in vinculacoes:
            result.append({
                "id": v[0],
                "usuario_id": v[1],
                "usuario_nome": v[2],
                "aluno_id": v[3],
                "aluno_nome": v[4],
                "tipo_vinculo": v[5]
            })
        return result

@app.post("/vinculacoes")
async def criar_vinculacao(vinculacao: VinculacaoCreate, admin_user: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Verificar se usuário e aluno existem
        cursor.execute("SELECT id FROM usuarios WHERE id=? AND tipo_usuario='usuario'", (vinculacao.usuario_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        cursor.execute("SELECT id FROM alunos WHERE id=?", (vinculacao.aluno_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
        try:
            cursor.execute(
                "INSERT INTO vinculacoes (usuario_id, aluno_id, tipo_vinculo) VALUES (?, ?, ?)",
                (vinculacao.usuario_id, vinculacao.aluno_id, vinculacao.tipo_vinculo)
            )
            conn.commit()
            return {"message": "Vinculação criada com sucesso", "id": cursor.lastrowid}
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Vinculação já existe")

@app.delete("/vinculacoes/{vinculacao_id}")
async def deletar_vinculacao(vinculacao_id: int, admin_user: dict = Depends(require_admin)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vinculacoes WHERE id=?", (vinculacao_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Vinculação não encontrada")
            
        conn.commit()
        return {"message": "Vinculação deletada com sucesso"}

# ENDPOINT PARA USUÁRIOS VEREM SEUS ALUNOS
@app.get("/meus-alunos")
async def listar_meus_alunos(current_user: dict = Depends(get_current_user)):
    """Usuários comuns veem apenas os alunos vinculados a eles"""
    if current_user["tipo_usuario"] == "admin":
        # Admin vê todos os alunos
        return await listar_alunos(current_user)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.nome, a.data_nascimento, a.email, a.status, a.turma_id, t.nome as turma_nome
            FROM alunos a
            LEFT JOIN turmas t ON a.turma_id = t.id
            JOIN vinculacoes v ON a.id = v.aluno_id
            WHERE v.usuario_id = ?
            ORDER BY a.nome
        """, (current_user["id"],))
        
        alunos = cursor.fetchall()
        
        result = []
        for aluno in alunos:
            result.append({
                "id": aluno[0],
                "nome": aluno[1],
                "data_nascimento": aluno[2],
                "email": aluno[3],
                "status": aluno[4],
                "turma_id": aluno[5],
                "turma_nome": aluno[6] if aluno[6] else "Sem turma"
            })
        return result

# ==================== ENDPOINTS DE SOLICITAÇÕES DE MATRÍCULA ====================

@app.post("/solicitacoes-matricula")
async def criar_solicitacao_matricula(
    solicitacao: SolicitacaoMatriculaCreate,
    current_user: dict = Depends(get_current_user)
):
    """Usuário comum cria solicitação de matrícula"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO solicitacoes_matricula 
            (usuario_id, nome_aluno, data_nascimento, email_aluno, observacoes, turma_solicitada)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            current_user["id"],
            solicitacao.nome_aluno,
            solicitacao.data_nascimento,
            solicitacao.email_aluno,
            solicitacao.observacoes,
            solicitacao.turma_solicitada
        ))
        
        solicitacao_id = cursor.lastrowid
        conn.commit()
        
        return {
            "id": solicitacao_id,
            "message": "Solicitação de matrícula enviada com sucesso! Aguarde a análise do administrador."
        }

@app.get("/solicitacoes-matricula")
async def listar_solicitacoes_matricula(current_user: dict = Depends(get_current_user)):
    """Lista solicitações de matrícula (admin vê todas, usuário vê apenas suas)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if current_user["tipo_usuario"] == "admin":
            # Admin vê todas as solicitações
            cursor.execute("""
                SELECT s.*, u.username, u.email as email_usuario
                FROM solicitacoes_matricula s
                JOIN usuarios u ON s.usuario_id = u.id
                ORDER BY s.data_solicitacao DESC
            """)
        else:
            # Usuário comum vê apenas suas solicitações
            cursor.execute("""
                SELECT s.*, u.username, u.email as email_usuario
                FROM solicitacoes_matricula s
                JOIN usuarios u ON s.usuario_id = u.id
                WHERE s.usuario_id = ?
                ORDER BY s.data_solicitacao DESC
            """, (current_user["id"],))
        
        solicitacoes = cursor.fetchall()
        
        result = []
        for s in solicitacoes:
            result.append({
                "id": s[0],
                "usuario_id": s[1],
                "nome_aluno": s[2],
                "data_nascimento": s[3],
                "email_aluno": s[4],
                "observacoes": s[5],
                "turma_solicitada": s[6],
                "status": s[7],
                "data_solicitacao": s[8],
                "data_resposta": s[9],
                "resposta_admin": s[10],
                "aluno_id": s[11],
                "username": s[12],
                "email_usuario": s[13]
            })
        
        return result

@app.put("/solicitacoes-matricula/{solicitacao_id}/aprovar")
async def aprovar_solicitacao_matricula(
    solicitacao_id: int,
    resposta: dict,
    current_user: dict = Depends(require_admin)
):
    """Admin aprova solicitação e cria o aluno"""
    turma_id = resposta.get("turma_id")
    resposta_admin = resposta.get("resposta_admin", "Solicitação aprovada")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Buscar dados da solicitação
        cursor.execute("SELECT * FROM solicitacoes_matricula WHERE id = ?", (solicitacao_id,))
        solicitacao = cursor.fetchone()
        
        if not solicitacao:
            raise HTTPException(status_code=404, detail="Solicitação não encontrada")
        
        if solicitacao[7] != 'pendente':  # status
            raise HTTPException(status_code=400, detail="Solicitação já foi processada")
        
        # Criar o aluno
        cursor.execute("""
            INSERT INTO alunos (nome, data_nascimento, email, status, turma_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            solicitacao[2],  # nome_aluno
            solicitacao[3],  # data_nascimento
            solicitacao[4],  # email_aluno
            'ativo',
            turma_id
        ))
        
        aluno_id = cursor.lastrowid
        
        # Criar vínculo entre usuário e aluno
        cursor.execute("""
            INSERT INTO vinculacoes (usuario_id, aluno_id, tipo_vinculo)
            VALUES (?, ?, ?)
        """, (solicitacao[1], aluno_id, 'responsavel'))  # usuario_id
        
        # Atualizar solicitação
        cursor.execute("""
            UPDATE solicitacoes_matricula 
            SET status = 'aprovada', data_resposta = CURRENT_TIMESTAMP, 
                resposta_admin = ?, aluno_id = ?
            WHERE id = ?
        """, (resposta_admin, aluno_id, solicitacao_id))
        
        conn.commit()
        
        return {
            "message": "Solicitação aprovada e aluno criado com sucesso!",
            "aluno_id": aluno_id
        }

@app.put("/solicitacoes-matricula/{solicitacao_id}/rejeitar")
async def rejeitar_solicitacao_matricula(
    solicitacao_id: int,
    resposta: dict,
    current_user: dict = Depends(require_admin)
):
    """Admin rejeita solicitação"""
    resposta_admin = resposta.get("resposta_admin", "Solicitação rejeitada")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM solicitacoes_matricula WHERE id = ?", (solicitacao_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Solicitação não encontrada")
        
        if result[0] != 'pendente':
            raise HTTPException(status_code=400, detail="Solicitação já foi processada")
        
        cursor.execute("""
            UPDATE solicitacoes_matricula 
            SET status = 'rejeitada', data_resposta = CURRENT_TIMESTAMP, resposta_admin = ?
            WHERE id = ?
        """, (resposta_admin, solicitacao_id))
        
        conn.commit()
        
        return {"message": "Solicitação rejeitada"}

@app.get("/")
async def root():
    return {"message": "Sistema Escolar API - Funcionando com SQLite!"}

@app.get("/test-db")
async def test_db():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM alunos")
            count = cursor.fetchone()[0]
        return {"status": "OK", "alunos": count, "database": "SQLite"}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
