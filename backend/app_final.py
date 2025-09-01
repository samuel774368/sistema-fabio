#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import pymysql
import uvicorn
from datetime import date

# Modelos Pydantic
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

# Configuração do banco
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': '',
    'database': 'escola_db',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """Cria conexão com o banco"""
    return pymysql.connect(**DB_CONFIG)

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

# ENDPOINTS ALUNOS
@app.get("/alunos", response_model=List[Aluno])
async def listar_alunos():
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
async def criar_aluno(aluno: AlunoCreate):
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
async def atualizar_aluno(aluno_id: int, aluno: AlunoCreate):
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
async def deletar_aluno(aluno_id: int):
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

# ENDPOINTS TURMAS
@app.get("/turmas", response_model=List[Turma])
async def listar_turmas():
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
async def criar_turma(turma: TurmaCreate):
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
async def atualizar_turma(turma_id: int, turma: TurmaCreate):
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
async def deletar_turma(turma_id: int):
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
