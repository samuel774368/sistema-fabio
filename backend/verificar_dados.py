import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Conectar ao banco
conn = sqlite3.connect('escola.db')
cursor = conn.cursor()

print("=== DADOS DO SISTEMA ===")

# Ver usuários
cursor.execute('SELECT id, username, tipo_usuario FROM usuarios')
users = cursor.fetchall()
print(f"Usuários ({len(users)}):")
for user in users:
    print(f"  {user[0]} - {user[1]} ({user[2]})")

# Ver alunos  
cursor.execute('SELECT id, nome FROM alunos')
alunos = cursor.fetchall()
print(f"\nAlunos ({len(alunos)}):")
for aluno in alunos:
    print(f"  {aluno[0]} - {aluno[1]}")

# Ver professores
cursor.execute('SELECT id, nome, especialidade FROM professores')
professores = cursor.fetchall()
print(f"\nProfessores ({len(professores)}):")
for prof in professores:
    print(f"  {prof[0]} - {prof[1]} ({prof[2]})")

# Ver vinculações
cursor.execute('''
    SELECT v.id, u.username, a.nome, v.tipo_vinculo 
    FROM vinculacoes v
    JOIN usuarios u ON v.usuario_id = u.id
    JOIN alunos a ON v.aluno_id = a.id
''')
vinculos = cursor.fetchall()
print(f"\nVinculações ({len(vinculos)}):")
for v in vinculos:
    print(f"  {v[1]} -> {v[2]} ({v[3]})")

# Criar vinculação se não existir
if len(users) >= 2 and len(alunos) >= 1:
    try:
        # Vincular usuário 'pai_ana' ao aluno 'Ana Silva'  
        cursor.execute('''
            INSERT OR IGNORE INTO vinculacoes (usuario_id, aluno_id, tipo_vinculo) 
            SELECT u.id, a.id, 'pai'
            FROM usuarios u, alunos a 
            WHERE u.username = 'pai_ana' AND a.nome = 'Ana Silva'
        ''')
        
        cursor.execute('''
            INSERT OR IGNORE INTO vinculacoes (usuario_id, aluno_id, tipo_vinculo) 
            SELECT u.id, a.id, 'mae'
            FROM usuarios u, alunos a 
            WHERE u.username = 'mae_bruno' AND a.nome = 'Bruno Santos'
        ''')
        
        conn.commit()
        print("\n✅ Vinculações verificadas/criadas!")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")

conn.close()
print("\n=== FIM ===")
