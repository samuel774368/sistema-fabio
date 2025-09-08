# 🎓 Sistema Escolar Moderno

Um sistema completo de gestão escolar com interface moderna, autenticação JWT e controle de acesso baseado em funções.

## ✨ Principais Melhorias Implementadas

### 🎨 Design Moderno e Colorido
- **Cards com Gradientes**: Cada card de aluno possui um gradiente colorido único
- **Animações Suaves**: Efeitos hover com transições elegantes
- **Barra Arco-íris**: Animação colorida no topo de cada card
- **Layout Responsivo**: Adapta-se perfeitamente a diferentes telas

### 👥 Separação de Interfaces
- **Interface Administrativa**: Página completa para administradores com todas as funcionalidades
- **Portal do Usuário**: Interface simplificada para usuários comuns (apenas visualização)
- **Redirecionamento Automático**: Sistema identifica o tipo de usuário e direciona para a página correta

### 🔐 Sistema de Autenticação Robusto
- **JWT Token**: Autenticação segura com tokens
- **Controle de Acesso**: Permissões baseadas no tipo de usuário
- **Sessões Persistentes**: Login mantido entre sessões

## 🚀 Como Usar

### 1. Iniciar o Sistema
```bash
# Navegar para o backend
cd backend

# Instalar dependências (se necessário)
pip install fastapi uvicorn pymysql pyjwt python-multipart

# Iniciar servidor
uvicorn app_final:app --host 0.0.0.0 --port 8001 --reload
```

### 2. Credenciais de Teste

#### 👑 Administrador
- **Usuário:** admin
- **Senha:** admin123
- **Acesso:** Interface administrativa completa com gestão de alunos e turmas

#### 👤 Usuário Comum
- **Usuário:** usuario
- **Senha:** user123
- **Acesso:** Portal de visualização (apenas consulta)

### 3. Acessar o Sistema
1. Abra `frontend/demo.html` para ver uma prévia das funcionalidades
2. Abra `frontend/login.html` para fazer login
3. O sistema irá redirecionar automaticamente:
   - Admins → `index.html` (Interface completa)
   - Usuários → `usuario.html` (Portal de consulta)

## 🎯 Funcionalidades por Tipo de Usuário

### 👑 Administrador (`index.html`)
- ✅ Visualizar, criar, editar e excluir alunos
- ✅ Visualizar, criar, editar e excluir turmas
- ✅ Realizar matrículas
- ✅ Exportar dados em CSV/JSON
- ✅ Relatórios e estatísticas
- ✅ Interface com todos os controles

### 👤 Usuário Comum (`usuario.html`)
- ✅ Visualizar lista de alunos
- ✅ Consultar informações de turmas
- ✅ Filtrar por nome, turma ou status
- ✅ Ver estatísticas básicas
- ❌ Sem permissões de edição
- ❌ Sem acesso a controles administrativos

## 🎨 Características Visuais

### Cards dos Alunos
- **Cores Variadas**: Gradientes únicos para cada card
- **Informações Organizadas**: Layout em grid com ícones
- **Animação Arco-íris**: Barra colorida animada no topo
- **Efeitos Hover**: Cards se elevam e ganham sombra ao passar o mouse
- **Botões Modernos**: Estilo glassmorphism para ações

### Interface Administrativa
- **Header Distinguível**: "👑 Admin - Gestão Escolar"
- **Controles Completos**: Botões para todas as operações CRUD
- **Tabs Organizadas**: Separação clara entre Alunos, Turmas e Relatórios

### Portal do Usuário
- **Design Limpo**: Interface simplificada e intuitiva
- **Cards Estatísticos**: Visão geral dos dados
- **Filtros de Busca**: Funcionalidade completa de pesquisa
- **Sem Poluição Visual**: Ausência de botões de edição

## 📁 Estrutura dos Arquivos

```
frontend/
├── demo.html          # Página de apresentação das funcionalidades
├── login.html         # Página de autenticação
├── index.html         # Interface administrativa (admins)
├── usuario.html       # Portal do usuário (usuários comuns)
├── sistema_final.js   # JavaScript da interface administrativa
├── usuario.js         # JavaScript do portal do usuário
└── styles.css         # Estilos CSS com o novo design

backend/
├── app_final.py       # API FastAPI com autenticação
├── database.py        # Configurações do banco de dados
└── requirements.txt   # Dependências Python
```

## 🔧 Configuração do Banco de Dados

O sistema inicializa automaticamente:
- Cria a tabela de usuários
- Insere o usuário administrador padrão
- Configura as permissões necessárias

## 🌟 Destaques Técnicos

- **Autenticação JWT**: Tokens seguros com expiração
- **Middleware CORS**: Configurado para desenvolvimento local
- **Validação Pydantic**: Modelos de dados consistentes
- **Separação de Responsabilidades**: Frontend e backend bem definidos
- **Design Responsivo**: Funciona em desktop, tablet e mobile
- **Acessibilidade**: Componentes com ARIA labels apropriados

## 📱 Responsividade

O sistema é totalmente responsivo:
- **Desktop**: Layout completo com sidebar
- **Tablet**: Adaptação com grid flexível
- **Mobile**: Interface empilhada com navegação otimizada

---

🎉 **Sistema pronto para uso com design moderno e funcionalidades completas!**
