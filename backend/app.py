# Sistema de Gestão Escolar - Backend
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
import uvicorn
from datetime import datetime, date

from models import Turma, Aluno, TurmaCreate, TurmaUpdate, AlunoCreate, AlunoUpdate, MatriculaCreate
from database import get_db, init_db

app = FastAPI(
    title="Sistema de Gestão Escolar",
    description="API para gerenciamento de alunos e turmas escolares",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar banco de dados na inicialização
@app.on_event("startup")
async def startup_event():
    init_db()

# Endpoint de saúde
@app.get("/health")
async def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return {"status": "ok", "message": "Sistema de Gestão Escolar API"}

# === ENDPOINTS DE ALUNOS ===

@app.get("/alunos", response_model=List[dict])
async def listar_alunos(
    search: Optional[str] = Query(None, description="Buscar por nome ou email"),
    turma_id: Optional[int] = Query(None, description="Filtrar por turma"),
    status: Optional[str] = Query(None, description="Filtrar por status (ativo/inativo)"),
    db: Session = Depends(get_db)
):
    """Listar alunos com filtros opcionais"""
    try:
        query = db.query(Aluno)
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    Aluno.nome.ilike(f"%{search}%"),
                    Aluno.email.ilike(f"%{search}%")
                )
            )
        
        if turma_id:
            query = query.filter(Aluno.turma_id == turma_id)
            
        if status:
            query = query.filter(Aluno.status == status)
        
        alunos = query.all()
        
        # Converter para dict incluindo informações da turma
        resultado = []
        for aluno in alunos:
            aluno_dict = {
                "id": aluno.id,
                "nome": aluno.nome,
                "data_nascimento": aluno.data_nascimento.isoformat(),
                "email": aluno.email,
                "status": aluno.status,
                "turma_id": aluno.turma_id,
                "turma_nome": aluno.turma.nome if aluno.turma else None
            }
            resultado.append(aluno_dict)
        
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.post("/alunos", response_model=dict, status_code=201)
async def criar_aluno(aluno: AlunoCreate, db: Session = Depends(get_db)):
    """Criar novo aluno"""
    try:
        # Validações
        if len(aluno.nome) < 3 or len(aluno.nome) > 80:
            raise HTTPException(
                status_code=422, 
                detail="Nome deve ter entre 3 e 80 caracteres"
            )
        
        # Validar idade mínima (5 anos)
        hoje = date.today()
        idade = hoje.year - aluno.data_nascimento.year
        if hoje.month < aluno.data_nascimento.month or (
            hoje.month == aluno.data_nascimento.month and hoje.day < aluno.data_nascimento.day
        ):
            idade -= 1
        
        if idade < 5:
            raise HTTPException(
                status_code=422,
                detail="Aluno deve ter pelo menos 5 anos de idade"
            )
        
        # Validar se turma existe e tem capacidade
        if aluno.turma_id:
            turma = db.query(Turma).filter(Turma.id == aluno.turma_id).first()
            if not turma:
                raise HTTPException(status_code=404, detail="Turma não encontrada")
            
            alunos_na_turma = db.query(Aluno).filter(Aluno.turma_id == aluno.turma_id).count()
            if alunos_na_turma >= turma.capacidade:
                raise HTTPException(
                    status_code=422,
                    detail="Turma já atingiu a capacidade máxima"
                )
        
        # Criar aluno
        db_aluno = Aluno(**aluno.dict())
        db.add(db_aluno)
        db.commit()
        db.refresh(db_aluno)
        
        return {
            "id": db_aluno.id,
            "nome": db_aluno.nome,
            "data_nascimento": db_aluno.data_nascimento.isoformat(),
            "email": db_aluno.email,
            "status": db_aluno.status,
            "turma_id": db_aluno.turma_id,
            "message": "Aluno criado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.put("/alunos/{aluno_id}", response_model=dict)
async def atualizar_aluno(aluno_id: int, aluno: AlunoUpdate, db: Session = Depends(get_db)):
    """Atualizar aluno existente"""
    try:
        db_aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
        if not db_aluno:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
        # Validações similares ao criar
        if aluno.nome and (len(aluno.nome) < 3 or len(aluno.nome) > 80):
            raise HTTPException(
                status_code=422,
                detail="Nome deve ter entre 3 e 80 caracteres"
            )
        
        if aluno.data_nascimento:
            hoje = date.today()
            idade = hoje.year - aluno.data_nascimento.year
            if hoje.month < aluno.data_nascimento.month or (
                hoje.month == aluno.data_nascimento.month and hoje.day < aluno.data_nascimento.day
            ):
                idade -= 1
            
            if idade < 5:
                raise HTTPException(
                    status_code=422,
                    detail="Aluno deve ter pelo menos 5 anos de idade"
                )
        
        # Validar turma se fornecida
        if aluno.turma_id:
            turma = db.query(Turma).filter(Turma.id == aluno.turma_id).first()
            if not turma:
                raise HTTPException(status_code=404, detail="Turma não encontrada")
            
            # Verificar capacidade (excluindo o aluno atual)
            alunos_na_turma = db.query(Aluno).filter(
                and_(Aluno.turma_id == aluno.turma_id, Aluno.id != aluno_id)
            ).count()
            if alunos_na_turma >= turma.capacidade:
                raise HTTPException(
                    status_code=422,
                    detail="Turma já atingiu a capacidade máxima"
                )
        
        # Atualizar campos fornecidos
        for field, value in aluno.dict(exclude_unset=True).items():
            setattr(db_aluno, field, value)
        
        db.commit()
        db.refresh(db_aluno)
        
        return {
            "id": db_aluno.id,
            "nome": db_aluno.nome,
            "data_nascimento": db_aluno.data_nascimento.isoformat(),
            "email": db_aluno.email,
            "status": db_aluno.status,
            "turma_id": db_aluno.turma_id,
            "message": "Aluno atualizado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.delete("/alunos/{aluno_id}")
async def excluir_aluno(aluno_id: int, db: Session = Depends(get_db)):
    """Excluir aluno"""
    try:
        db_aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
        if not db_aluno:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
        db.delete(db_aluno)
        db.commit()
        
        return {"message": "Aluno excluído com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

# === ENDPOINTS DE TURMAS ===

@app.get("/turmas", response_model=List[dict])
async def listar_turmas(db: Session = Depends(get_db)):
    """Listar todas as turmas com informações de ocupação"""
    try:
        turmas = db.query(Turma).all()
        
        resultado = []
        for turma in turmas:
            alunos_count = db.query(Aluno).filter(Aluno.turma_id == turma.id).count()
            turma_dict = {
                "id": turma.id,
                "nome": turma.nome,
                "capacidade": turma.capacidade,
                "ocupacao": alunos_count,
                "disponivel": turma.capacidade - alunos_count
            }
            resultado.append(turma_dict)
        
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.post("/turmas", response_model=dict, status_code=201)
async def criar_turma(turma: TurmaCreate, db: Session = Depends(get_db)):
    """Criar nova turma"""
    try:
        # Validações
        if len(turma.nome) < 2:
            raise HTTPException(
                status_code=422,
                detail="Nome da turma deve ter pelo menos 2 caracteres"
            )
        
        if turma.capacidade < 1 or turma.capacidade > 50:
            raise HTTPException(
                status_code=422,
                detail="Capacidade deve ser entre 1 e 50 alunos"
            )
        
        # Verificar se já existe turma com mesmo nome
        turma_existente = db.query(Turma).filter(Turma.nome == turma.nome).first()
        if turma_existente:
            raise HTTPException(
                status_code=422,
                detail="Já existe uma turma com este nome"
            )
        
        # Criar turma
        db_turma = Turma(**turma.dict())
        db.add(db_turma)
        db.commit()
        db.refresh(db_turma)
        
        return {
            "id": db_turma.id,
            "nome": db_turma.nome,
            "capacidade": db_turma.capacidade,
            "ocupacao": 0,
            "disponivel": db_turma.capacidade,
            "message": "Turma criada com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.put("/turmas/{turma_id}", response_model=dict)
async def atualizar_turma(turma_id: int, turma: TurmaUpdate, db: Session = Depends(get_db)):
    """Atualizar turma existente"""
    try:
        db_turma = db.query(Turma).filter(Turma.id == turma_id).first()
        if not db_turma:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        
        # Validações
        if turma.nome and len(turma.nome) < 2:
            raise HTTPException(
                status_code=422,
                detail="Nome da turma deve ter pelo menos 2 caracteres"
            )
        
        if turma.capacidade and (turma.capacidade < 1 or turma.capacidade > 50):
            raise HTTPException(
                status_code=422,
                detail="Capacidade deve ser entre 1 e 50 alunos"
            )
        
        # Verificar se nova capacidade não é menor que alunos já matriculados
        if turma.capacidade:
            alunos_matriculados = db.query(Aluno).filter(Aluno.turma_id == turma_id).count()
            if turma.capacidade < alunos_matriculados:
                raise HTTPException(
                    status_code=422,
                    detail=f"Não é possível reduzir capacidade. Existem {alunos_matriculados} alunos matriculados"
                )
        
        # Verificar nome duplicado (excluindo a turma atual)
        if turma.nome:
            turma_existente = db.query(Turma).filter(
                and_(Turma.nome == turma.nome, Turma.id != turma_id)
            ).first()
            if turma_existente:
                raise HTTPException(
                    status_code=422,
                    detail="Já existe uma turma com este nome"
                )
        
        # Atualizar campos fornecidos
        for field, value in turma.dict(exclude_unset=True).items():
            setattr(db_turma, field, value)
        
        db.commit()
        db.refresh(db_turma)
        
        alunos_count = db.query(Aluno).filter(Aluno.turma_id == turma_id).count()
        
        return {
            "id": db_turma.id,
            "nome": db_turma.nome,
            "capacidade": db_turma.capacidade,
            "ocupacao": alunos_count,
            "disponivel": db_turma.capacidade - alunos_count,
            "message": "Turma atualizada com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.delete("/turmas/{turma_id}")
async def excluir_turma(turma_id: int, db: Session = Depends(get_db)):
    """Excluir turma (apenas se não houver alunos matriculados)"""
    try:
        db_turma = db.query(Turma).filter(Turma.id == turma_id).first()
        if not db_turma:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        
        # Verificar se há alunos matriculados
        alunos_count = db.query(Aluno).filter(Aluno.turma_id == turma_id).count()
        if alunos_count > 0:
            raise HTTPException(
                status_code=422,
                detail=f"Não é possível excluir turma com {alunos_count} alunos matriculados"
            )
        
        db.delete(db_turma)
        db.commit()
        
        return {"message": "Turma excluída com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

# === ENDPOINT DE MATRÍCULA ===

@app.post("/matriculas", response_model=dict)
async def realizar_matricula(matricula: MatriculaCreate, db: Session = Depends(get_db)):
    """Realizar matrícula de aluno em turma"""
    try:
        # Verificar se aluno existe
        aluno = db.query(Aluno).filter(Aluno.id == matricula.aluno_id).first()
        if not aluno:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
        # Verificar se turma existe
        turma = db.query(Turma).filter(Turma.id == matricula.turma_id).first()
        if not turma:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        
        # Verificar capacidade da turma
        alunos_na_turma = db.query(Aluno).filter(Aluno.turma_id == matricula.turma_id).count()
        if alunos_na_turma >= turma.capacidade:
            raise HTTPException(
                status_code=422,
                detail="Turma já atingiu a capacidade máxima"
            )
        
        # Verificar se aluno já está matriculado em outra turma
        if aluno.turma_id:
            raise HTTPException(
                status_code=422,
                detail="Aluno já está matriculado em outra turma"
            )
        
        # Realizar matrícula
        aluno.turma_id = matricula.turma_id
        aluno.status = "ativo"
        
        db.commit()
        db.refresh(aluno)
        
        return {
            "aluno_id": aluno.id,
            "aluno_nome": aluno.nome,
            "turma_id": turma.id,
            "turma_nome": turma.nome,
            "status": aluno.status,
            "message": "Matrícula realizada com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

# === ENDPOINTS DE ESTATÍSTICAS ===

@app.get("/estatisticas")
async def obter_estatisticas(db: Session = Depends(get_db)):
    """Obter estatísticas gerais do sistema"""
    try:
        total_alunos = db.query(Aluno).count()
        alunos_ativos = db.query(Aluno).filter(Aluno.status == "ativo").count()
        alunos_inativos = db.query(Aluno).filter(Aluno.status == "inativo").count()
        total_turmas = db.query(Turma).count()
        
        # Estatísticas por turma
        turmas_stats = []
        turmas = db.query(Turma).all()
        for turma in turmas:
            alunos_count = db.query(Aluno).filter(Aluno.turma_id == turma.id).count()
            turmas_stats.append({
                "turma_id": turma.id,
                "turma_nome": turma.nome,
                "capacidade": turma.capacidade,
                "ocupacao": alunos_count,
                "percentual_ocupacao": round((alunos_count / turma.capacidade) * 100, 1) if turma.capacidade > 0 else 0
            })
        
        return {
            "total_alunos": total_alunos,
            "alunos_ativos": alunos_ativos,
            "alunos_inativos": alunos_inativos,
            "total_turmas": total_turmas,
            "alunos_sem_turma": total_alunos - sum(ts["ocupacao"] for ts in turmas_stats),
            "turmas_estatisticas": turmas_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
