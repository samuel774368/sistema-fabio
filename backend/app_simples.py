# Servidor Backend Simples - Sistema Escola
# Funciona diretamente com PyMySQL, sem SQLAlchemy
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pymysql
import uvicorn
from datetime import date, datetime
import json
from typing import Optional, List, Dict, Any
import re

app = FastAPI(
    title="Sistema de Gestão Escolar",
    description="API para gerenciamento de alunos e turmas escolares",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do banco
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'escola_db',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """Obter conexão com o banco"""
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão: {str(e)}")

def validar_email(email: str) -> bool:
    """Validar formato de email"""
    if not email:
        return True  # Email é opcional
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def calcular_idade(data_nascimento: str) -> int:
    """Calcular idade a partir da data de nascimento"""
    try:
        if isinstance(data_nascimento, str):
            nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
        else:
            nascimento = data_nascimento
        
        hoje = date.today()
        idade = hoje.year - nascimento.year
        if hoje.month < nascimento.month or (hoje.month == nascimento.month and hoje.day < nascimento.day):
            idade -= 1
        return idade
    except:
        return 0

# === ENDPOINTS ===

@app.get("/health")
def health_check():
    """Endpoint de saúde"""
    return {"status": "ok", "message": "Sistema Escola API funcionando!"}

@app.get("/alunos")
def listar_alunos(
    search: Optional[str] = None,
    turma_id: Optional[int] = None,
    status: Optional[str] = None
):
    """Listar alunos com filtros"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Query base
        sql = """
        SELECT a.*, t.nome as turma_nome 
        FROM alunos a 
        LEFT JOIN turmas t ON a.turma_id = t.id 
        WHERE 1=1
        """
        params = []
        
        # Aplicar filtros
        if search:
            sql += " AND (a.nome LIKE %s OR a.email LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        if turma_id:
            sql += " AND a.turma_id = %s"
            params.append(turma_id)
            
        if status:
            sql += " AND a.status = %s"
            params.append(status)
        
        sql += " ORDER BY a.nome"
        
        cursor.execute(sql, params)
        alunos = cursor.fetchall()
        
        # Converter datas para string
        for aluno in alunos:
            if aluno['data_nascimento']:
                aluno['data_nascimento'] = aluno['data_nascimento'].strftime('%Y-%m-%d')
                aluno['idade'] = calcular_idade(aluno['data_nascimento'])
        
        cursor.close()
        conn.close()
        
        return alunos
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/alunos")
def criar_aluno(aluno_data: dict):
    """Criar novo aluno"""
    try:
        # Validações
        nome = aluno_data.get('nome', '').strip()
        if not nome or len(nome) < 3 or len(nome) > 80:
            raise HTTPException(status_code=422, detail="Nome deve ter entre 3 e 80 caracteres")
        
        data_nascimento = aluno_data.get('data_nascimento')
        if not data_nascimento:
            raise HTTPException(status_code=422, detail="Data de nascimento é obrigatória")
        
        idade = calcular_idade(data_nascimento)
        if idade < 5:
            raise HTTPException(status_code=422, detail="Aluno deve ter pelo menos 5 anos")
        
        email = aluno_data.get('email', '').strip()
        if email and not validar_email(email):
            raise HTTPException(status_code=422, detail="Email inválido")
        
        status = aluno_data.get('status', 'inativo')
        if status not in ['ativo', 'inativo']:
            raise HTTPException(status_code=422, detail="Status deve ser 'ativo' ou 'inativo'")
        
        turma_id = aluno_data.get('turma_id')
        
        # Verificar turma se fornecida
        if turma_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Verificar se turma existe
            cursor.execute("SELECT capacidade FROM turmas WHERE id = %s", (turma_id,))
            turma = cursor.fetchone()
            if not turma:
                cursor.close()
                conn.close()
                raise HTTPException(status_code=404, detail="Turma não encontrada")
            
            # Verificar capacidade
            cursor.execute("SELECT COUNT(*) FROM alunos WHERE turma_id = %s", (turma_id,))
            ocupacao = cursor.fetchone()[0]
            if ocupacao >= turma[0]:
                cursor.close()
                conn.close()
                raise HTTPException(status_code=422, detail="Turma já está lotada")
            
            cursor.close()
            conn.close()
        
        # Inserir aluno
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """
        INSERT INTO alunos (nome, data_nascimento, email, status, turma_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql, (nome, data_nascimento, email or None, status, turma_id))
        aluno_id = cursor.lastrowid
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "id": aluno_id,
            "nome": nome,
            "data_nascimento": data_nascimento,
            "email": email,
            "status": status,
            "turma_id": turma_id,
            "message": "Aluno criado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/alunos/{aluno_id}")
def atualizar_aluno(aluno_id: int, aluno_data: dict):
    """Atualizar aluno"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se aluno existe
        cursor.execute("SELECT * FROM alunos WHERE id = %s", (aluno_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
        # Validações
        nome = aluno_data.get('nome', '').strip()
        if nome and (len(nome) < 3 or len(nome) > 80):
            raise HTTPException(status_code=422, detail="Nome deve ter entre 3 e 80 caracteres")
        
        data_nascimento = aluno_data.get('data_nascimento')
        if data_nascimento:
            idade = calcular_idade(data_nascimento)
            if idade < 5:
                raise HTTPException(status_code=422, detail="Aluno deve ter pelo menos 5 anos")
        
        email = aluno_data.get('email', '').strip()
        if email and not validar_email(email):
            raise HTTPException(status_code=422, detail="Email inválido")
        
        # Construir SQL de update
        campos = []
        valores = []
        
        if nome:
            campos.append("nome = %s")
            valores.append(nome)
        
        if data_nascimento:
            campos.append("data_nascimento = %s")
            valores.append(data_nascimento)
        
        if 'email' in aluno_data:
            campos.append("email = %s")
            valores.append(email or None)
        
        if 'status' in aluno_data:
            status = aluno_data['status']
            if status in ['ativo', 'inativo']:
                campos.append("status = %s")
                valores.append(status)
        
        if 'turma_id' in aluno_data:
            turma_id = aluno_data['turma_id']
            if turma_id:
                # Verificar turma
                cursor.execute("SELECT capacidade FROM turmas WHERE id = %s", (turma_id,))
                turma = cursor.fetchone()
                if not turma:
                    cursor.close()
                    conn.close()
                    raise HTTPException(status_code=404, detail="Turma não encontrada")
                
                # Verificar capacidade (excluindo aluno atual)
                cursor.execute("SELECT COUNT(*) FROM alunos WHERE turma_id = %s AND id != %s", (turma_id, aluno_id))
                ocupacao = cursor.fetchone()[0]
                if ocupacao >= turma[0]:
                    cursor.close()
                    conn.close()
                    raise HTTPException(status_code=422, detail="Turma já está lotada")
            
            campos.append("turma_id = %s")
            valores.append(turma_id)
        
        if campos:
            sql = f"UPDATE alunos SET {', '.join(campos)} WHERE id = %s"
            valores.append(aluno_id)
            cursor.execute(sql, valores)
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return {"message": "Aluno atualizado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/alunos/{aluno_id}")
def excluir_aluno(aluno_id: int):
    """Excluir aluno"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se aluno existe
        cursor.execute("SELECT * FROM alunos WHERE id = %s", (aluno_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
        # Excluir
        cursor.execute("DELETE FROM alunos WHERE id = %s", (aluno_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {"message": "Aluno excluído com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/turmas")
def listar_turmas():
    """Listar turmas com ocupação"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        sql = """
        SELECT t.*, COUNT(a.id) as ocupacao
        FROM turmas t
        LEFT JOIN alunos a ON t.id = a.turma_id
        GROUP BY t.id, t.nome, t.capacidade
        ORDER BY t.nome
        """
        
        cursor.execute(sql)
        turmas = cursor.fetchall()
        
        # Adicionar campo disponível
        for turma in turmas:
            turma['disponivel'] = turma['capacidade'] - turma['ocupacao']
        
        cursor.close()
        conn.close()
        
        return turmas
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/turmas")
def criar_turma(turma_data: dict):
    """Criar nova turma"""
    try:
        nome = turma_data.get('nome', '').strip()
        if not nome or len(nome) < 2:
            raise HTTPException(status_code=422, detail="Nome da turma deve ter pelo menos 2 caracteres")
        
        capacidade = turma_data.get('capacidade')
        if not capacidade or capacidade < 1 or capacidade > 50:
            raise HTTPException(status_code=422, detail="Capacidade deve ser entre 1 e 50")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se já existe
        cursor.execute("SELECT id FROM turmas WHERE nome = %s", (nome,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=422, detail="Já existe uma turma com este nome")
        
        # Inserir
        sql = "INSERT INTO turmas (nome, capacidade) VALUES (%s, %s)"
        cursor.execute(sql, (nome, capacidade))
        turma_id = cursor.lastrowid
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "id": turma_id,
            "nome": nome,
            "capacidade": capacidade,
            "ocupacao": 0,
            "disponivel": capacidade,
            "message": "Turma criada com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/turmas/{turma_id}")
def atualizar_turma(turma_id: int, turma_data: dict):
    """Atualizar turma"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se turma existe
        cursor.execute("SELECT * FROM turmas WHERE id = %s", (turma_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        
        nome = turma_data.get('nome', '').strip()
        capacidade = turma_data.get('capacidade')
        
        # Validações
        if nome and len(nome) < 2:
            raise HTTPException(status_code=422, detail="Nome deve ter pelo menos 2 caracteres")
        
        if capacidade and (capacidade < 1 or capacidade > 50):
            raise HTTPException(status_code=422, detail="Capacidade deve ser entre 1 e 50")
        
        # Verificar capacidade vs ocupação atual
        if capacidade:
            cursor.execute("SELECT COUNT(*) FROM alunos WHERE turma_id = %s", (turma_id,))
            ocupacao = cursor.fetchone()[0]
            if capacidade < ocupacao:
                cursor.close()
                conn.close()
                raise HTTPException(status_code=422, detail=f"Capacidade não pode ser menor que {ocupacao} (ocupação atual)")
        
        # Construir update
        campos = []
        valores = []
        
        if nome:
            campos.append("nome = %s")
            valores.append(nome)
        
        if capacidade:
            campos.append("capacidade = %s")
            valores.append(capacidade)
        
        if campos:
            sql = f"UPDATE turmas SET {', '.join(campos)} WHERE id = %s"
            valores.append(turma_id)
            cursor.execute(sql, valores)
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return {"message": "Turma atualizada com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/turmas/{turma_id}")
def excluir_turma(turma_id: int):
    """Excluir turma"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se turma existe
        cursor.execute("SELECT * FROM turmas WHERE id = %s", (turma_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        
        # Verificar se há alunos
        cursor.execute("SELECT COUNT(*) FROM alunos WHERE turma_id = %s", (turma_id,))
        alunos_count = cursor.fetchone()[0]
        if alunos_count > 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=422, detail=f"Não é possível excluir turma com {alunos_count} alunos")
        
        # Excluir
        cursor.execute("DELETE FROM turmas WHERE id = %s", (turma_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {"message": "Turma excluída com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/matriculas")
def realizar_matricula(matricula_data: dict):
    """Realizar matrícula"""
    try:
        aluno_id = matricula_data.get('aluno_id')
        turma_id = matricula_data.get('turma_id')
        
        if not aluno_id or not turma_id:
            raise HTTPException(status_code=422, detail="aluno_id e turma_id são obrigatórios")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar aluno
        cursor.execute("SELECT nome, turma_id FROM alunos WHERE id = %s", (aluno_id,))
        aluno = cursor.fetchone()
        if not aluno:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
        if aluno[1]:  # já tem turma
            cursor.close()
            conn.close()
            raise HTTPException(status_code=422, detail="Aluno já está matriculado em uma turma")
        
        # Verificar turma
        cursor.execute("SELECT nome, capacidade FROM turmas WHERE id = %s", (turma_id,))
        turma = cursor.fetchone()
        if not turma:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        
        # Verificar capacidade
        cursor.execute("SELECT COUNT(*) FROM alunos WHERE turma_id = %s", (turma_id,))
        ocupacao = cursor.fetchone()[0]
        if ocupacao >= turma[1]:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=422, detail="Turma já está lotada")
        
        # Realizar matrícula
        cursor.execute("UPDATE alunos SET turma_id = %s, status = 'ativo' WHERE id = %s", (turma_id, aluno_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "aluno_id": aluno_id,
            "aluno_nome": aluno[0],
            "turma_id": turma_id,
            "turma_nome": turma[0],
            "status": "ativo",
            "message": "Matrícula realizada com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/estatisticas")
def obter_estatisticas():
    """Obter estatísticas gerais"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Estatísticas básicas
        cursor.execute("SELECT COUNT(*) FROM alunos")
        total_alunos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alunos WHERE status = 'ativo'")
        alunos_ativos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alunos WHERE status = 'inativo'")
        alunos_inativos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM turmas")
        total_turmas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alunos WHERE turma_id IS NULL")
        alunos_sem_turma = cursor.fetchone()[0]
        
        # Estatísticas por turma
        cursor.execute("""
            SELECT t.id, t.nome, t.capacidade, COUNT(a.id) as ocupacao
            FROM turmas t
            LEFT JOIN alunos a ON t.id = a.turma_id
            GROUP BY t.id, t.nome, t.capacidade
            ORDER BY t.nome
        """)
        
        turmas_stats = []
        for turma in cursor.fetchall():
            tid, nome, capacidade, ocupacao = turma
            percentual = (ocupacao / capacidade) * 100 if capacidade > 0 else 0
            turmas_stats.append({
                "turma_id": tid,
                "turma_nome": nome,
                "capacidade": capacidade,
                "ocupacao": ocupacao,
                "percentual_ocupacao": round(percentual, 1)
            })
        
        cursor.close()
        conn.close()
        
        return {
            "total_alunos": total_alunos,
            "alunos_ativos": alunos_ativos,
            "alunos_inativos": alunos_inativos,
            "total_turmas": total_turmas,
            "alunos_sem_turma": alunos_sem_turma,
            "turmas_estatisticas": turmas_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Iniciando Sistema de Gestão Escolar...")
    print("📊 Banco: MySQL (escola_db)")
    print("🌐 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
