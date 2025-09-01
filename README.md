# 🏫 Sistema de Gestão Escolar

Sistema web completo para gerenciamento de alunos e turmas escolares, desenvolvido com HTML5, CSS3, JavaScript no frontend e FastAPI + SQLite no backend.

## 📋 Funcionalidades

### 👥 Gestão de Alunos
- ✅ Cadastro de novos alunos
- ✅ Edição de dados dos alunos
- ✅ Exclusão de alunos
- ✅ Busca por nome ou email
- ✅ Filtros por turma e status
- ✅ Validação de idade (mínimo 5 anos)
- ✅ Validação de email

### 📚 Gestão de Turmas
- ✅ Cadastro de turmas
- ✅ Edição de turmas
- ✅ Exclusão de turmas (apenas sem alunos)
- ✅ Controle de capacidade
- ✅ Visualização de ocupação

### 🎓 Sistema de Matrículas
- ✅ Matrícula de alunos em turmas
- ✅ Verificação de capacidade
- ✅ Atualização automática de status
- ✅ Prevenção de superlotação

### 📊 Relatórios e Exportação
- ✅ Exportação em CSV
- ✅ Exportação em JSON
- ✅ Estatísticas em tempo real
- ✅ Filtros avançados

### 🔍 Funcionalidades Especiais
- ✅ Paginação de resultados
- ✅ Ordenação persistente
- ✅ Busca em tempo real
- ✅ Acessibilidade completa
- ✅ Feedback visual com toasts

## 🛠️ Tecnologias Utilizadas

### Frontend
- **HTML5**: Estrutura semântica
- **CSS3**: Estilização com Grid e Flexbox
- **JavaScript ES6+**: Funcionalidades interativas
- **Sem frameworks**: Código vanilla puro

### Backend
- **Python 3.8+**: Linguagem principal
- **FastAPI**: Framework web moderno
- **SQLAlchemy**: ORM para banco de dados
- **SQLite**: Banco de dados leve
- **Pydantic**: Validação de dados

### Ferramentas
- **VS Code**: Editor de código
- **Git**: Controle de versão
- **GitHub**: Repositório remoto

## 📁 Estrutura do Projeto

```
escola-sistema/
├── frontend/
│   ├── index.html          # Página principal
│   ├── styles.css          # Estilos CSS
│   └── scripts.js          # JavaScript
├── backend/
│   ├── app.py              # FastAPI principal
│   ├── models.py           # Modelos SQLAlchemy/Pydantic
│   ├── database.py         # Configuração do banco
│   ├── seed.py             # Script de dados
│   └── requirements.txt    # Dependências Python
├── README.md               # Documentação
├── REPORT.md              # Relatório técnico
└── ChatIA.md              # Conversas com IA
```

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8 ou superior
- Navegador web moderno
- Git (opcional)

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/dw2-samuel-escola.git
cd dw2-samuel-escola
```

### 2. Configurar o Backend

#### Instalar Dependências
```bash
cd backend
pip install -r requirements.txt
```

#### Inicializar o Banco de Dados
```bash
python seed.py
```
Escolha a opção "1" para popular com dados de exemplo.

#### Executar o Servidor
```bash
python app.py
```
ou
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

O backend estará disponível em: `http://localhost:8000`

### 3. Executar o Frontend

Abra o arquivo `frontend/index.html` em um navegador web ou use um servidor local:

```bash
cd frontend
python -m http.server 3000
```

O frontend estará disponível em: `http://localhost:3000`

## 📖 API Documentation

A documentação interativa da API está disponível em:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Principais Endpoints

#### Alunos
- `GET /alunos` - Listar alunos (com filtros)
- `POST /alunos` - Criar novo aluno
- `PUT /alunos/{id}` - Atualizar aluno
- `DELETE /alunos/{id}` - Excluir aluno

#### Turmas
- `GET /turmas` - Listar turmas
- `POST /turmas` - Criar nova turma
- `PUT /turmas/{id}` - Atualizar turma
- `DELETE /turmas/{id}` - Excluir turma

#### Matrículas
- `POST /matriculas` - Realizar matrícula

#### Utilitários
- `GET /health` - Status da API
- `GET /estatisticas` - Estatísticas gerais

## 🎨 Identidade Visual

### Cores
- **Primária**: #2563EB (azul)
- **Secundária**: #10B981 (verde)
- **Acento**: #F97316 (laranja)
- **Fundo**: #F1F5F9 (cinza claro)
- **Texto**: #0B1220 (escuro)

### Tipografia
- **Fonte**: Roboto ou Inter (fallback sans-serif)
- **Tamanhos**: Hierarquia clara e legível

## ♿ Acessibilidade

O sistema implementa práticas de acessibilidade:

- ✅ **Navegação por teclado**: Todos os elementos são acessíveis via Tab
- ✅ **ARIA labels**: Botões e campos têm descrições claras
- ✅ **Contraste**: Mínimo 4.5:1 em todos os textos
- ✅ **Foco visível**: Indicação clara do elemento ativo
- ✅ **Screen readers**: Anúncios de feedback e operações
- ✅ **Atalhos**: Alt+N (novo aluno), Alt+T (nova turma)

## 🔧 Validações

### Frontend
- ✅ Campos obrigatórios
- ✅ Formato de email
- ✅ Limites de caracteres
- ✅ Validação de idade
- ✅ Prevenção de dados duplicados

### Backend
- ✅ Validação com Pydantic
- ✅ Regras de negócio
- ✅ Verificação de integridade
- ✅ Tratamento de erros
- ✅ Códigos HTTP apropriados

## 📱 Responsividade

O sistema é totalmente responsivo:
- 📱 **Mobile**: Otimizado para celulares
- 📟 **Tablet**: Layout adaptado para tablets
- 💻 **Desktop**: Experiência completa

## 🧪 Testes

### Testando a API
Use o arquivo de coleção incluído ou teste manualmente:

```bash
# Listar alunos
curl -X GET "http://localhost:8000/alunos"

# Criar aluno
curl -X POST "http://localhost:8000/alunos" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "data_nascimento": "2008-01-15",
    "email": "joao@email.com",
    "status": "ativo"
  }'
```

## 🐛 Solução de Problemas

### Erro: Módulo não encontrado
```bash
pip install -r requirements.txt
```

### Erro: Banco de dados bloqueado
```bash
python seed.py
# Escolher opção 2 para limpar e depois 1 para popular
```

### Erro: CORS
Certifique-se de que o backend está rodando na porta 8000.

## 🤝 Contribuição

Este é um projeto acadêmico individual. Para melhorias:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é desenvolvido para fins educacionais como parte do curso de Desenvolvimento Web.

## 👨‍💻 Autor

**Samuel Xavier Mubarac**
- 🎓 Projeto: Sistema de Gestão Escolar
- 📚 Disciplina: Desenvolvimento Web 2
- 🏫 Instituição: [Nome da Instituição]

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação acima
2. Consulte os logs do console
3. Verifique as issues no GitHub
4. Entre em contato com o desenvolvedor

---

⭐ **Este projeto faz parte do portfólio acadêmico e demonstra competências em desenvolvimento web full-stack.**
