# 🗄️ Guia Completo: XAMPP + MySQL + Sistema Escola

## 📋 Passo 1: Baixar e Instalar o XAMPP

### 1.1 Download do XAMPP
1. Acesse: https://www.apachefriends.org/pt_br/index.html
2. Clique em "Download" para Windows
3. Baixe a versão mais recente (PHP 8.x)
4. **Arquivo será**: `xampp-windows-x64-8.x.x-installer.exe` (aprox. 150MB)

### 1.2 Instalação
1. **Execute o arquivo** baixado como **Administrador**
2. **Antivírus pode alertar**: Clique "Sim" ou "Permitir"
3. **Pasta de instalação**: Deixe `C:\xampp` (padrão)
4. **Componentes para instalar**:
   - ✅ Apache
   - ✅ MySQL
   - ✅ PHP
   - ✅ phpMyAdmin
   - ❌ Filezilla (pode desmarcar)
   - ❌ Mercury (pode desmarcar)
   - ❌ Tomcat (pode desmarcar)
5. Clique **"Next"** até finalizar
6. **NÃO** marque "Iniciar XAMPP agora" ainda

---

## 📋 Passo 2: Configurar e Iniciar o XAMPP

### 2.1 Abrir XAMPP Control Panel
1. **Procurar**: "XAMPP" no menu iniciar
2. **Executar como Administrador**: XAMPP Control Panel
3. **Interface do XAMPP** será aberta

### 2.2 Iniciar Serviços
1. **Apache**:
   - Clique no botão **"Start"** na linha Apache
   - Status deve ficar **verde** e mostrar "Running"
   - **Porta padrão**: 80 e 443

2. **MySQL**:
   - Clique no botão **"Start"** na linha MySQL
   - Status deve ficar **verde** e mostrar "Running"
   - **Porta padrão**: 3306

### 2.3 Verificar se Funcionou
1. **Abra o navegador**
2. **Digite**: `http://localhost`
3. **Deve aparecer**: Página de boas-vindas do XAMPP
4. **Digite**: `http://localhost/phpmyadmin`
5. **Deve aparecer**: Interface do phpMyAdmin

---

## 📋 Passo 3: Criar o Banco de Dados

### 3.1 Acessar phpMyAdmin
1. **Navegador**: `http://localhost/phpmyadmin`
2. **Login automático** (sem senha por padrão)

### 3.2 Criar Banco
1. **Clique** na aba **"Bancos de dados"** (Databases)
2. **Nome do banco**: `escola_db`
3. **Agrupamento**: `utf8mb4_general_ci`
4. **Clique**: **"Criar"**

### 3.3 Verificar Criação
- **Lista à esquerda** deve mostrar `escola_db`
- **Clique** no nome para abrir o banco
- Banco estará vazio (sem tabelas ainda)

---

## 📋 Passo 4: Instalar Python e Dependências

### 4.1 Verificar Python
1. **Abrir PowerShell**: Pressione `Win + X` → "Windows PowerShell (Admin)"
2. **Verificar Python**:
   ```powershell
   python --version
   ```
3. **Se não tiver**: Baixe de https://python.org

### 4.2 Navegar para Projeto
```powershell
cd "c:\Users\samue\OneDrive\Área de Trabalho\escola-sistema\backend"
```

### 4.3 Instalar Dependências
```powershell
pip install -r requirements.txt
```

**O que será instalado**:
- FastAPI (framework web)
- SQLAlchemy (ORM)
- PyMySQL (driver MySQL)
- Pydantic (validações)
- Uvicorn (servidor)

---

## 📋 Passo 5: Testar Conexão

### 5.1 Testar Conexão MySQL
```powershell
python -c "import pymysql; print('PyMySQL instalado com sucesso!')"
```

### 5.2 Criar e Popular Tabelas
```powershell
python seed.py
```

**Menu do seed**:
1. 🌱 Popular banco com dados de exemplo ← **Escolha esta opção**
2. 🗑️ Limpar todos os dados
3. 🔍 Verificar integridade dos dados
4. 📊 Mostrar estatísticas
5. 🔄 Resetar banco (limpar + popular)
6. ❌ Sair

### 5.3 Verificar no phpMyAdmin
1. **Atualize** a página do phpMyAdmin
2. **Clique** em `escola_db`
3. **Deve mostrar**:
   - Tabela `alunos` (25 registros)
   - Tabela `turmas` (10 registros)

---

## 📋 Passo 6: Executar o Sistema

### 6.1 Iniciar Backend
```powershell
python app.py
```

**Saída esperada**:
```
✅ Conectado ao MySQL com sucesso!
✅ Tabelas criadas com sucesso!
🚀 Banco de dados inicializado com sucesso!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6.2 Abrir Frontend
1. **Nova aba PowerShell**:
   ```powershell
   cd "c:\Users\samue\OneDrive\Área de Trabalho\escola-sistema\frontend"
   python -m http.server 3000
   ```

2. **Ou simplesmente**:
   - Navegue até a pasta `frontend`
   - Duplo clique em `index.html`

### 6.3 Acessar Sistema
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs
- **phpMyAdmin**: http://localhost/phpmyadmin

---

## 🔧 Solução de Problemas

### Problema 1: Apache não inicia
**Erro**: "Port 80 in use by..."
**Solução**:
1. **XAMPP Control** → **Config** (Apache) → **httpd.conf**
2. **Procurar**: `Listen 80`
3. **Trocar para**: `Listen 8080`
4. **Salvar** e **reiniciar Apache**
5. **Acessar**: `http://localhost:8080`

### Problema 2: MySQL não inicia
**Erro**: "Port 3306 in use"
**Solução**:
1. **Verificar se não há outro MySQL rodando**
2. **Gerenciador de Tarefas** → **Serviços** → Parar outros MySQL
3. **Ou trocar porta** no arquivo `my.ini`

### Problema 3: Erro de conexão Python
**Erro**: "Can't connect to MySQL server"
**Verificar**:
1. ✅ XAMPP MySQL está rodando (verde)
2. ✅ Firewall não está bloqueando
3. ✅ Porta 3306 está aberta
4. ✅ Arquivo `database.py` tem configuração correta

### Problema 4: Banco não criado
**Se seed.py der erro**:
1. **Verificar conexão**:
   ```powershell
   python -c "
   import pymysql
   conn = pymysql.connect(host='localhost', user='root', password='', database='escola_db')
   print('Conexão OK!')
   conn.close()
   "
   ```

---

## 📊 Verificar se Tudo Funcionou

### ✅ Checklist Final
- [ ] XAMPP rodando (Apache + MySQL verdes)
- [ ] http://localhost funciona
- [ ] http://localhost/phpmyadmin funciona
- [ ] Banco `escola_db` existe
- [ ] Tabelas `alunos` e `turmas` existem
- [ ] Backend rodando em http://localhost:8000
- [ ] Frontend abre e conecta ao backend
- [ ] Consegue listar alunos
- [ ] Consegue cadastrar novo aluno

### 🎯 URLs Importantes
```
Frontend:          http://localhost:3000
Backend API:       http://localhost:8000
API Documentação:  http://localhost:8000/docs
phpMyAdmin:        http://localhost/phpmyadmin
XAMPP Dashboard:   http://localhost/dashboard
```

---

## 🔄 Comandos Rápidos

### Iniciar tudo:
```powershell
# Terminal 1 - Backend
cd "c:\Users\samue\OneDrive\Área de Trabalho\escola-sistema\backend"
python app.py

# Terminal 2 - Frontend  
cd "c:\Users\samue\OneDrive\Área de Trabalho\escola-sistema\frontend"
python -m http.server 3000
```

### Parar tudo:
- **Ctrl+C** nos terminais
- **XAMPP Control** → **Stop** Apache e MySQL

---

## 📞 Ajuda Extra

Se algo não funcionar:
1. **Verifique os logs** no XAMPP Control Panel
2. **Verifique se todas as portas estão livres**
3. **Reinicie o XAMPP** completamente
4. **Verifique se o Windows Firewall** não está bloqueando

**Lembre-se**: O sistema também funciona com SQLite se o MySQL der problema!
