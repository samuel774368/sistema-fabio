# Modelos SQLAlchemy e Pydantic para o Sistema de Gestão Escolar
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import date
import re

Base = declarative_base()

# === MODELOS SQLALCHEMY (BANCO DE DADOS) ===

class Turma(Base):
    __tablename__ = "turmas"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False, index=True)
    capacidade = Column(Integer, nullable=False)
    
    # Relacionamento com alunos
    alunos = relationship("Aluno", back_populates="turma")
    
    def __repr__(self):
        return f"<Turma(id={self.id}, nome='{self.nome}', capacidade={self.capacidade})>"

class Aluno(Base):
    __tablename__ = "alunos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(80), nullable=False, index=True)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    status = Column(String(20), nullable=False, default="inativo")  # ativo, inativo
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=True)
    
    # Relacionamento com turma
    turma = relationship("Turma", back_populates="alunos")
    
    def __repr__(self):
        return f"<Aluno(id={self.id}, nome='{self.nome}', status='{self.status}')>"

# === MODELOS PYDANTIC (VALIDAÇÃO DE DADOS) ===

class TurmaBase(BaseModel):
    nome: str
    capacidade: int

class TurmaCreate(TurmaBase):
    @validator('nome')
    def validar_nome(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Nome da turma deve ter pelo menos 2 caracteres')
        if len(v.strip()) > 100:
            raise ValueError('Nome da turma deve ter no máximo 100 caracteres')
        return v.strip()
    
    @validator('capacidade')
    def validar_capacidade(cls, v):
        if v < 1:
            raise ValueError('Capacidade deve ser pelo menos 1')
        if v > 50:
            raise ValueError('Capacidade não pode exceder 50 alunos')
        return v

class TurmaUpdate(BaseModel):
    nome: Optional[str] = None
    capacidade: Optional[int] = None
    
    @validator('nome')
    def validar_nome(cls, v):
        if v is not None:
            if not v or len(v.strip()) < 2:
                raise ValueError('Nome da turma deve ter pelo menos 2 caracteres')
            if len(v.strip()) > 100:
                raise ValueError('Nome da turma deve ter no máximo 100 caracteres')
            return v.strip()
        return v
    
    @validator('capacidade')
    def validar_capacidade(cls, v):
        if v is not None:
            if v < 1:
                raise ValueError('Capacidade deve ser pelo menos 1')
            if v > 50:
                raise ValueError('Capacidade não pode exceder 50 alunos')
        return v

class TurmaResponse(TurmaBase):
    id: int
    ocupacao: int
    disponivel: int
    
    class Config:
        from_attributes = True

class AlunoBase(BaseModel):
    nome: str
    data_nascimento: date
    email: Optional[str] = None
    status: str = "inativo"
    turma_id: Optional[int] = None

class AlunoCreate(AlunoBase):
    @validator('nome')
    def validar_nome(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Nome deve ter pelo menos 3 caracteres')
        if len(v.strip()) > 80:
            raise ValueError('Nome deve ter no máximo 80 caracteres')
        # Verificar se contém apenas letras, espaços e alguns caracteres especiais
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\'\-\.]+$', v.strip()):
            raise ValueError('Nome deve conter apenas letras, espaços, apóstrofos, hífens e pontos')
        return v.strip()
    
    @validator('data_nascimento')
    def validar_data_nascimento(cls, v):
        hoje = date.today()
        
        # Verificar se a data não é futura
        if v > hoje:
            raise ValueError('Data de nascimento não pode ser futura')
        
        # Calcular idade
        idade = hoje.year - v.year
        if hoje.month < v.month or (hoje.month == v.month and hoje.day < v.day):
            idade -= 1
        
        # Verificar idade mínima (5 anos) e máxima (25 anos)
        if idade < 5:
            raise ValueError('Aluno deve ter pelo menos 5 anos de idade')
        if idade > 25:
            raise ValueError('Idade não pode exceder 25 anos')
        
        return v
    
    @validator('email')
    def validar_email(cls, v):
        if v is not None and v.strip():
            v = v.strip().lower()
            # Validação básica de email
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Email inválido')
            if len(v) > 120:
                raise ValueError('Email deve ter no máximo 120 caracteres')
            return v
        return None
    
    @validator('status')
    def validar_status(cls, v):
        status_validos = ['ativo', 'inativo']
        if v not in status_validos:
            raise ValueError(f'Status deve ser um dos seguintes: {", ".join(status_validos)}')
        return v

class AlunoUpdate(BaseModel):
    nome: Optional[str] = None
    data_nascimento: Optional[date] = None
    email: Optional[str] = None
    status: Optional[str] = None
    turma_id: Optional[int] = None
    
    @validator('nome')
    def validar_nome(cls, v):
        if v is not None:
            if not v or len(v.strip()) < 3:
                raise ValueError('Nome deve ter pelo menos 3 caracteres')
            if len(v.strip()) > 80:
                raise ValueError('Nome deve ter no máximo 80 caracteres')
            if not re.match(r'^[a-zA-ZÀ-ÿ\s\'\-\.]+$', v.strip()):
                raise ValueError('Nome deve conter apenas letras, espaços, apóstrofos, hífens e pontos')
            return v.strip()
        return v
    
    @validator('data_nascimento')
    def validar_data_nascimento(cls, v):
        if v is not None:
            hoje = date.today()
            
            if v > hoje:
                raise ValueError('Data de nascimento não pode ser futura')
            
            idade = hoje.year - v.year
            if hoje.month < v.month or (hoje.month == v.month and hoje.day < v.day):
                idade -= 1
            
            if idade < 5:
                raise ValueError('Aluno deve ter pelo menos 5 anos de idade')
            if idade > 25:
                raise ValueError('Idade não pode exceder 25 anos')
        
        return v
    
    @validator('email')
    def validar_email(cls, v):
        if v is not None and v.strip():
            v = v.strip().lower()
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Email inválido')
            if len(v) > 120:
                raise ValueError('Email deve ter no máximo 120 caracteres')
            return v
        return None
    
    @validator('status')
    def validar_status(cls, v):
        if v is not None:
            status_validos = ['ativo', 'inativo']
            if v not in status_validos:
                raise ValueError(f'Status deve ser um dos seguintes: {", ".join(status_validos)}')
        return v

class AlunoResponse(AlunoBase):
    id: int
    turma_nome: Optional[str] = None
    
    class Config:
        from_attributes = True

class MatriculaCreate(BaseModel):
    aluno_id: int
    turma_id: int
    
    @validator('aluno_id')
    def validar_aluno_id(cls, v):
        if v <= 0:
            raise ValueError('ID do aluno deve ser um número positivo')
        return v
    
    @validator('turma_id')
    def validar_turma_id(cls, v):
        if v <= 0:
            raise ValueError('ID da turma deve ser um número positivo')
        return v

class MatriculaResponse(BaseModel):
    aluno_id: int
    aluno_nome: str
    turma_id: int
    turma_nome: str
    status: str
    message: str

# === MODELOS PARA RELATÓRIOS E ESTATÍSTICAS ===

class EstatisticasTurma(BaseModel):
    turma_id: int
    turma_nome: str
    capacidade: int
    ocupacao: int
    percentual_ocupacao: float

class EstatisticasGerais(BaseModel):
    total_alunos: int
    alunos_ativos: int
    alunos_inativos: int
    total_turmas: int
    alunos_sem_turma: int
    turmas_estatisticas: list[EstatisticasTurma]

# === ESQUEMAS DE RESPOSTA PADRÃO ===

class MensagemSucesso(BaseModel):
    message: str
    
class MensagemErro(BaseModel):
    detail: str

# === VALIDADORES PERSONALIZADOS ===

def validar_ano_escolar(ano: str) -> bool:
    """Validar se o ano escolar está no formato correto (ex: 1º Ano A, 2º Ano B)"""
    pattern = r'^[1-3]º Ano [A-Z]$'
    return bool(re.match(pattern, ano))

def calcular_idade(data_nascimento: date) -> int:
    """Calcular idade em anos"""
    hoje = date.today()
    idade = hoje.year - data_nascimento.year
    if hoje.month < data_nascimento.month or (hoje.month == data_nascimento.month and hoje.day < data_nascimento.day):
        idade -= 1
    return idade

def validar_capacidade_turma(capacidade: int, ocupacao_atual: int = 0) -> bool:
    """Validar se a capacidade da turma é adequada"""
    return capacidade >= ocupacao_atual and 1 <= capacidade <= 50

# === CONSTANTES ===

STATUS_ALUNO = ['ativo', 'inativo']
CAPACIDADE_MIN_TURMA = 1
CAPACIDADE_MAX_TURMA = 50
IDADE_MIN_ALUNO = 5
IDADE_MAX_ALUNO = 25
TAMANHO_MIN_NOME = 3
TAMANHO_MAX_NOME_ALUNO = 80
TAMANHO_MAX_NOME_TURMA = 100
TAMANHO_MAX_EMAIL = 120
