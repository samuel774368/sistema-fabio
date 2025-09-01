// Sistema de Gestão Escolar - JavaScript
class EscolaApp {
    constructor() {
        this.alunos = [];
        this.turmas = [];
        this.filtros = {
            search: '',
            turma_id: '',
            status: ''
        };
        this.ordenacao = {
            campo: 'nome',
            direcao: 'asc'
        };
        this.paginaAtual = 1;
        this.itensPorPagina = 10;
        
        this.init();
    }

    async init() {
        await this.carregarDados();
        this.configurarEventos();
        this.carregarOrdenacao();
        this.renderizar();
    }

    async carregarDados() {
        try {
            // Carregar dados da API
            const [turmasResponse, alunosResponse] = await Promise.all([
                fetch('http://localhost:8000/turmas'),
                fetch('http://localhost:8000/alunos')
            ]);

            if (turmasResponse.ok && alunosResponse.ok) {
                this.turmas = await turmasResponse.json();
                this.alunos = await alunosResponse.json();
                console.log('Dados carregados da API:', { turmas: this.turmas.length, alunos: this.alunos.length });
            } else {
                throw new Error('Erro ao carregar dados da API');
            }
        } catch (error) {
            console.error('Erro ao conectar com API:', error);
            this.showToast('Erro ao conectar com o servidor. Usando dados de exemplo.', 'error');
            
            // Fallback para dados mockados
            this.turmas = [
                { id: 1, nome: '1º Ano A', capacidade: 30 },
                { id: 2, nome: '1º Ano B', capacidade: 28 },
                { id: 3, nome: '2º Ano A', capacidade: 25 },
                { id: 4, nome: '2º Ano B', capacidade: 30 },
                { id: 5, nome: '3º Ano A', capacidade: 20 }
            ];

            this.alunos = [
                {
                    id: 1,
                    nome: 'Ana Silva Santos',
                    data_nascimento: '2008-03-15',
                    email: 'ana.silva@email.com',
                    status: 'ativo',
                    turma_id: 1
                },
                {
                    id: 2,
                    nome: 'Carlos Eduardo Oliveira',
                    data_nascimento: '2007-07-22',
                    email: 'carlos.eduardo@email.com',
                    status: 'ativo',
                    turma_id: 2
                },
                {
                    id: 3,
                    nome: 'Beatriz Costa Lima',
                    data_nascimento: '2009-01-10',
                    email: 'beatriz.costa@email.com',
                    status: 'inativo',
                    turma_id: null
                },
                {
                    id: 4,
                    nome: 'Diego Ferreira Santos',
                    data_nascimento: '2008-11-05',
                    email: 'diego.ferreira@email.com',
                    status: 'ativo',
                    turma_id: 1
                },
                {
                    id: 5,
                    nome: 'Eduarda Mendes Rocha',
                    data_nascimento: '2007-09-18',
                    email: 'eduarda.mendes@email.com',
                    status: 'ativo',
                    turma_id: 3
                }
            ];
        }

        this.carregarTurmasSelect();
        this.carregarStatusSelect();
    }

    carregarTurmasSelect() {
        const turmaFilter = document.getElementById('filterTurma');
        const alunoTurma = document.getElementById('alunoTurma');
        
        // Limpar opções existentes
        if (turmaFilter) {
            turmaFilter.innerHTML = '<option value="">Todas as turmas</option>';
            this.turmas.forEach(turma => {
                const option = document.createElement('option');
                option.value = turma.id;
                option.textContent = turma.nome;
                turmaFilter.appendChild(option);
            });
        }

        if (alunoTurma) {
            alunoTurma.innerHTML = '<option value="">Sem turma</option>';
            this.turmas.forEach(turma => {
                const option = document.createElement('option');
                option.value = turma.id;
                option.textContent = turma.nome;
                alunoTurma.appendChild(option);
            });
        }
    }

    carregarStatusSelect() {
        const statusFilter = document.getElementById('filterStatus');
        if (statusFilter) {
            statusFilter.innerHTML = `
                <option value="">Todos os status</option>
                <option value="ativo">Ativo</option>
                <option value="inativo">Inativo</option>
            `;
        }
    }

    configurarAbas() {
        // Selecionar todos os botões de aba
        const tabButtons = document.querySelectorAll('.tab-btn');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');
                this.mostrarAba(targetTab);
            });
        });
    }

    mostrarAba(abaName) {
        // Desativar todas as abas
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
            btn.setAttribute('aria-selected', 'false');
        });

        // Esconder todos os painéis
        document.querySelectorAll('.tab-content').forEach(panel => {
            panel.classList.remove('active');
            panel.style.display = 'none';
        });

        // Ativar aba selecionada
        const activeButton = document.querySelector(`[data-tab="${abaName}"]`);
        const activePanel = document.getElementById(`${abaName}-panel`);

        if (activeButton && activePanel) {
            activeButton.classList.add('active');
            activeButton.setAttribute('aria-selected', 'true');
            
            activePanel.classList.add('active');
            activePanel.style.display = 'block';

            // Renderizar conteúdo específico da aba
            this.renderizarAba(abaName);
        }
    }

    renderizarAba(abaName) {
        switch (abaName) {
            case 'alunos':
                this.renderizarAlunos();
                this.atualizarPaginacao();
                break;
            case 'turmas':
                this.renderizarTurmas();
                break;
            case 'relatorios':
                this.renderizarRelatorios();
                break;
        }
    }

    configurarEventos() {
        // Navegação por abas
        this.configurarAbas();
        
        // Busca
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => {
            this.filtros.search = e.target.value;
            this.aplicarFiltros();
        });

        // Filtros
        const turmaFilter = document.getElementById('filterTurma');
        turmaFilter.addEventListener('change', (e) => {
            this.filtros.turma_id = e.target.value;
            this.aplicarFiltros();
        });

        const statusFilter = document.getElementById('filterStatus');
        statusFilter.addEventListener('change', (e) => {
            this.filtros.status = e.target.value;
            this.aplicarFiltros();
        });

        // Ordenação
        const sortSelect = document.getElementById('sortAlunos');
        sortSelect.addEventListener('change', (e) => {
            const [campo, direcao] = e.target.value.split('-');
            this.ordenacao = { campo, direcao };
            this.salvarOrdenacao();
            this.renderizar();
        });

        // Botões principais
        document.getElementById('newAlunoBtn').addEventListener('click', () => {
            this.abrirModalAluno();
        });

        document.getElementById('newTurmaBtn').addEventListener('click', () => {
            this.abrirModalTurma();
        });

        document.getElementById('newMatriculaBtn').addEventListener('click', () => {
            this.abrirModalMatricula();
        });

        // Modais
        this.configurarModais();

        // Atalhos de teclado
        document.addEventListener('keydown', (e) => {
            if (e.altKey && e.key === 'n') {
                e.preventDefault();
                this.abrirModalAluno();
            }
            if (e.altKey && e.key === 't') {
                e.preventDefault();
                this.abrirModalTurma();
            }
        });

        // Paginação
        document.getElementById('btnPrevPage').addEventListener('click', () => {
            if (this.paginaAtual > 1) {
                this.paginaAtual--;
                this.renderizar();
            }
        });

        document.getElementById('btnNextPage').addEventListener('click', () => {
            const totalPaginas = this.calcularTotalPaginas();
            if (this.paginaAtual < totalPaginas) {
                this.paginaAtual++;
                this.renderizar();
            }
        });
    }

    configurarModais() {
        // Modal Aluno
        const modalAluno = document.getElementById('modalAluno');
        const closeModalAluno = modalAluno.querySelector('.close-btn');
        const formAluno = document.getElementById('alunoForm');

        closeModalAluno.addEventListener('click', () => {
            this.fecharModalAluno();
        });

        modalAluno.addEventListener('click', (e) => {
            if (e.target === modalAluno) {
                this.fecharModalAluno();
            }
        });

        formAluno.addEventListener('submit', (e) => {
            e.preventDefault();
            this.salvarAluno();
        });

        // Modal Turma
        const modalTurma = document.getElementById('modalTurma');
        const closeModalTurma = modalTurma.querySelector('.close-btn');
        const formTurma = document.getElementById('turmaForm');

        closeModalTurma.addEventListener('click', () => {
            this.fecharModalTurma();
        });

        modalTurma.addEventListener('click', (e) => {
            if (e.target === modalTurma) {
                this.fecharModalTurma();
            }
        });

        formTurma.addEventListener('submit', (e) => {
            e.preventDefault();
            this.salvarTurma();
        });

        // Modal Matrícula
        const modalMatricula = document.getElementById('modalMatricula');
        const closeModalMatricula = modalMatricula.querySelector('.close-btn');

        closeModalMatricula.addEventListener('click', () => {
            this.fecharModalMatricula();
        });

        modalMatricula.addEventListener('click', (e) => {
            if (e.target === modalMatricula) {
                this.fecharModalMatricula();
            }
        });

        // Formulário Matrícula
        const formMatricula = document.getElementById('matriculaForm');
        formMatricula.addEventListener('submit', (e) => {
            e.preventDefault();
            this.salvarMatricula();
        });
    }

    abrirModalAluno(aluno = null) {
        const modal = document.getElementById('modalAluno');
        const form = document.getElementById('formAluno');
        const title = document.getElementById('modalAlunoTitle');
        
        if (aluno) {
            title.textContent = 'Editar Aluno';
            form.alunoId.value = aluno.id;
            form.nome.value = aluno.nome;
            form.data_nascimento.value = aluno.data_nascimento;
            form.email.value = aluno.email || '';
            form.status.value = aluno.status;
            form.turma_id.value = aluno.turma_id || '';
        } else {
            title.textContent = 'Novo Aluno';
            form.reset();
            form.alunoId.value = '';
        }

        this.popularSelectTurmas('turma_id');
        modal.style.display = 'block';
        form.nome.focus();
    }

    fecharModalAluno() {
        document.getElementById('modalAluno').style.display = 'none';
    }

    abrirModalTurma(turma = null) {
        const modal = document.getElementById('modalTurma');
        const form = document.getElementById('formTurma');
        const title = document.getElementById('modalTurmaTitle');
        
        if (turma) {
            title.textContent = 'Editar Turma';
            form.turmaId.value = turma.id;
            form.nomeTurma.value = turma.nome;
            form.capacidade.value = turma.capacidade;
        } else {
            title.textContent = 'Nova Turma';
            form.reset();
            form.turmaId.value = '';
        }

        modal.style.display = 'block';
        form.nomeTurma.focus();
    }

    fecharModalTurma() {
        document.getElementById('modalTurma').style.display = 'none';
    }

    abrirModalMatricula() {
        const modal = document.getElementById('modalMatricula');
        const form = document.getElementById('matriculaForm');
        const title = document.getElementById('modalMatriculaTitle');
        
        // Limpar formulário
        if (form) form.reset();
        
        // Configurar modal
        title.textContent = 'Nova Matrícula';
        
        // Carregar alunos sem turma no select
        this.carregarAlunosSelect();
        
        // Carregar turmas no select
        this.carregarTurmasMatriculaSelect();
        
        modal.style.display = 'block';
        modal.setAttribute('aria-hidden', 'false');
        
        // Focar no primeiro campo
        const firstSelect = document.getElementById('matriculaAluno');
        if (firstSelect) firstSelect.focus();
    }

    fecharModalMatricula() {
        const modal = document.getElementById('modalMatricula');
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
    }

    carregarAlunosSelect() {
        const alunoSelect = document.getElementById('matriculaAluno');
        if (alunoSelect) {
            alunoSelect.innerHTML = '<option value="">Selecione o aluno</option>';
            
            // Carregar apenas alunos sem turma (turma_id é null)
            const alunosSemTurma = this.alunos.filter(aluno => !aluno.turma_id && aluno.status === 'ativo');
            
            alunosSemTurma.forEach(aluno => {
                const option = document.createElement('option');
                option.value = aluno.id;
                option.textContent = aluno.nome;
                alunoSelect.appendChild(option);
            });
        }
    }

    carregarTurmasMatriculaSelect() {
        const turmaSelect = document.getElementById('matriculaTurma');
        if (turmaSelect) {
            turmaSelect.innerHTML = '<option value="">Selecione a turma</option>';
            
            this.turmas.forEach(turma => {
                const alunosNaTurma = this.alunos.filter(a => a.turma_id === turma.id).length;
                const vagas = turma.capacidade - alunosNaTurma;
                
                const option = document.createElement('option');
                option.value = turma.id;
                option.textContent = `${turma.nome} (${vagas} vagas)`;
                
                // Desabilitar se não houver vagas
                if (vagas <= 0) {
                    option.disabled = true;
                    option.textContent += ' - LOTADA';
                }
                
                turmaSelect.appendChild(option);
            });
        }
    }

    limparFiltros() {
        // Resetar filtros
        this.filtros = {
            search: '',
            turma_id: '',
            status: ''
        };

        // Limpar campos do formulário
        document.getElementById('searchInput').value = '';
        document.getElementById('filterTurma').value = '';
        document.getElementById('filterStatus').value = '';

        // Aplicar filtros (vai mostrar todos os dados)
        this.aplicarFiltros();
    }

    popularSelectTurmas(selectId) {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Selecione uma turma</option>';
        
        this.turmas.forEach(turma => {
            const alunosNaTurma = this.alunos.filter(a => a.turma_id === turma.id).length;
            const option = document.createElement('option');
            option.value = turma.id;
            option.textContent = `${turma.nome} (${alunosNaTurma}/${turma.capacidade})`;
            
            if (alunosNaTurma >= turma.capacidade) {
                option.disabled = true;
                option.textContent += ' - Lotada';
            }
            
            select.appendChild(option);
        });
    }

    // Função removida - usando versão async com API calls

    // Função removida - usando versão async com API calls

    async salvarMatricula() {
        const form = document.getElementById('matriculaForm');
        const formData = new FormData(form);
        
        const alunoId = parseInt(formData.get('aluno_id'));
        const turmaId = parseInt(formData.get('turma_id'));
        
        // Validação
        if (!alunoId || !turmaId) {
            this.showToast('Selecione aluno e turma', 'error');
            return;
        }

        const aluno = this.alunos.find(a => a.id === alunoId);
        const turma = this.turmas.find(t => t.id === turmaId);
        
        if (!aluno || !turma) {
            this.showToast('Aluno ou turma não encontrados', 'error');
            return;
        }

        // Verificar se o aluno já tem turma
        if (aluno.turma_id) {
            this.showToast('Aluno já está matriculado em uma turma', 'error');
            return;
        }

        // Verificar capacidade da turma
        const alunosNaTurma = this.alunos.filter(a => a.turma_id === turmaId).length;
        if (alunosNaTurma >= turma.capacidade) {
            this.showToast('Turma está lotada', 'error');
            return;
        }

        try {
            // Atualizar aluno com a turma via API
            const alunoAtualizado = {
                nome: aluno.nome,
                data_nascimento: aluno.data_nascimento,
                email: aluno.email,
                status: aluno.status,
                turma_id: turmaId
            };

            const response = await fetch(`http://localhost:8000/alunos/${alunoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(alunoAtualizado)
            });

            if (response.ok) {
                this.showToast(`${aluno.nome} matriculado na ${turma.nome}!`, 'success');
                this.fecharModalMatricula();
                await this.carregarDados();
                this.renderizar();
            } else {
                const error = await response.json();
                this.showToast('Erro ao matricular: ' + (error.detail || 'Erro desconhecido'), 'error');
            }
        } catch (error) {
            console.error('Erro:', error);
            this.showToast('Erro ao conectar com o servidor', 'error');
        }
    }

    validarAluno(aluno) {
        // Validar nome
        if (!aluno.nome || aluno.nome.length < 3 || aluno.nome.length > 80) {
            this.showToast('Nome deve ter entre 3 e 80 caracteres!', 'error');
            return false;
        }

        // Validar data de nascimento
        const nascimento = new Date(aluno.data_nascimento);
        const hoje = new Date();
        const idade = hoje.getFullYear() - nascimento.getFullYear();
        
        if (idade < 5) {
            this.showToast('Aluno deve ter pelo menos 5 anos!', 'error');
            return false;
        }

        // Validar email
        if (aluno.email && !this.validarEmail(aluno.email)) {
            this.showToast('Email inválido!', 'error');
            return false;
        }

        return true;
    }

    validarTurma(turma) {
        // Validar nome
        if (!turma.nome || turma.nome.length < 2) {
            this.showToast('Nome da turma deve ter pelo menos 2 caracteres!', 'error');
            return false;
        }

        // Validar capacidade
        if (!turma.capacidade || turma.capacidade < 1 || turma.capacidade > 50) {
            this.showToast('Capacidade deve ser entre 1 e 50 alunos!', 'error');
            return false;
        }

        return true;
    }

    validarEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    excluirAluno(id) {
        if (confirm('Tem certeza que deseja excluir este aluno?')) {
            this.alunos = this.alunos.filter(a => a.id !== id);
            this.renderizar();
            this.atualizarEstatisticas();
            this.showToast('Aluno excluído com sucesso!', 'success');
        }
    }

    excluirTurma(id) {
        const alunosNaTurma = this.alunos.filter(a => a.turma_id === id);
        
        if (alunosNaTurma.length > 0) {
            this.showToast('Não é possível excluir turma com alunos matriculados!', 'error');
            return;
        }

        if (confirm('Tem certeza que deseja excluir esta turma?')) {
            this.turmas = this.turmas.filter(t => t.id !== id);
            this.renderizarTurmas();
            this.atualizarFiltros();
            this.showToast('Turma excluída com sucesso!', 'success');
        }
    }

    aplicarFiltros() {
        this.paginaAtual = 1;
        this.renderizar();
    }

    obterAlunosFiltrados() {
        let alunosFiltrados = [...this.alunos];

        // Filtro de busca
        if (this.filtros.search) {
            const search = this.filtros.search.toLowerCase();
            alunosFiltrados = alunosFiltrados.filter(aluno =>
                aluno.nome.toLowerCase().includes(search) ||
                (aluno.email && aluno.email.toLowerCase().includes(search))
            );
        }

        // Filtro por turma
        if (this.filtros.turma_id) {
            alunosFiltrados = alunosFiltrados.filter(aluno =>
                aluno.turma_id == this.filtros.turma_id
            );
        }

        // Filtro por status
        if (this.filtros.status) {
            alunosFiltrados = alunosFiltrados.filter(aluno =>
                aluno.status === this.filtros.status
            );
        }

        // Ordenação
        alunosFiltrados.sort((a, b) => {
            let valorA, valorB;

            if (this.ordenacao.campo === 'nome') {
                valorA = a.nome.toLowerCase();
                valorB = b.nome.toLowerCase();
            } else if (this.ordenacao.campo === 'idade') {
                valorA = new Date(a.data_nascimento);
                valorB = new Date(b.data_nascimento);
            }

            if (this.ordenacao.direcao === 'desc') {
                return valorA < valorB ? 1 : -1;
            } else {
                return valorA > valorB ? 1 : -1;
            }
        });

        return alunosFiltrados;
    }

    calcularTotalPaginas() {
        const alunosFiltrados = this.obterAlunosFiltrados();
        return Math.ceil(alunosFiltrados.length / this.itensPorPagina);
    }

    obterAlunosPaginados() {
        const alunosFiltrados = this.obterAlunosFiltrados();
        const inicio = (this.paginaAtual - 1) * this.itensPorPagina;
        const fim = inicio + this.itensPorPagina;
        return alunosFiltrados.slice(inicio, fim);
    }

    atualizarEstatisticas() {
        const totalAlunos = this.alunos.length;
        const alunosAtivos = this.alunos.filter(aluno => aluno.status === 'ativo').length;
        const totalTurmas = this.turmas.length;

        // Atualizar elementos no DOM
        const totalAlunosElement = document.getElementById('totalAlunos');
        const alunosAtivosElement = document.getElementById('alunosAtivos');
        const totalTurmasElement = document.getElementById('totalTurmas');

        if (totalAlunosElement) totalAlunosElement.textContent = totalAlunos;
        if (alunosAtivosElement) alunosAtivosElement.textContent = alunosAtivos;
        if (totalTurmasElement) totalTurmasElement.textContent = totalTurmas;
    }

    renderizar() {
        this.renderizarAlunos();
        this.renderizarTurmas();
        this.atualizarEstatisticas();
        this.atualizarFiltros();
        this.atualizarPaginacao();
        
        // Garantir que a aba correta esteja ativa
        const abaAtiva = document.querySelector('.tab-btn.active');
        if (abaAtiva) {
            const tab = abaAtiva.getAttribute('data-tab');
            this.renderizarAba(tab);
        } else {
            // Se nenhuma aba está ativa, ativar a primeira (alunos)
            this.mostrarAba('alunos');
        }
    }

    renderizarAlunos() {
        const container = document.getElementById('alunosList');
        const alunosPaginados = this.obterAlunosPaginados();

        if (alunosPaginados.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>Nenhum aluno encontrado</p>
                </div>
            `;
            return;
        }

        container.innerHTML = alunosPaginados.map(aluno => {
            const turma = this.turmas.find(t => t.id === aluno.turma_id);
            const idade = this.calcularIdade(aluno.data_nascimento);

            return `
                <div class="aluno-card" tabindex="0">
                    <div class="aluno-info">
                        <h3>${aluno.nome}</h3>
                        <p><strong>Idade:</strong> ${idade} anos</p>
                        <p><strong>Email:</strong> ${aluno.email || 'Não informado'}</p>
                        <p><strong>Status:</strong> 
                            <span class="status ${aluno.status}">${aluno.status}</span>
                        </p>
                        <p><strong>Turma:</strong> ${turma ? turma.nome : 'Não matriculado'}</p>
                    </div>
                    <div class="aluno-actions">
                        <button onclick="app.abrirModalAluno(${JSON.stringify(aluno).replace(/"/g, '&quot;')})" 
                                aria-label="Editar aluno ${aluno.nome}">
                            Editar
                        </button>
                        ${!aluno.turma_id ? `
                            <button onclick="app.abrirModalMatricula(${aluno.id})" 
                                    class="btn-matricular"
                                    aria-label="Matricular aluno ${aluno.nome}">
                                Matricular
                            </button>
                        ` : ''}
                        <button onclick="app.excluirAluno(${aluno.id})" 
                                class="btn-delete"
                                aria-label="Excluir aluno ${aluno.nome}">
                            Excluir
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderizarTurmas() {
        const container = document.getElementById('turmasList');
        
        container.innerHTML = this.turmas.map(turma => {
            const alunosNaTurma = this.alunos.filter(a => a.turma_id === turma.id);
            const ocupacao = alunosNaTurma.length;
            const percentual = (ocupacao / turma.capacidade * 100).toFixed(1);

            return `
                <div class="turma-card" tabindex="0">
                    <div class="turma-info">
                        <h3>${turma.nome}</h3>
                        <p><strong>Capacidade:</strong> ${turma.capacidade} alunos</p>
                        <p><strong>Ocupação:</strong> ${ocupacao}/${turma.capacidade} (${percentual}%)</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${percentual}%"></div>
                        </div>
                    </div>
                    <div class="turma-actions">
                        <button onclick="app.abrirModalTurma(${JSON.stringify(turma).replace(/"/g, '&quot;')})"
                                aria-label="Editar turma ${turma.nome}">
                            Editar
                        </button>
                        <button onclick="app.excluirTurma(${turma.id})" 
                                class="btn-delete"
                                aria-label="Excluir turma ${turma.nome}">
                            Excluir
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderizarRelatorios() {
        // Esta função é chamada quando a aba de relatórios é ativada
        // Os botões de exportação já estão configurados no HTML
        console.log('Aba de relatórios ativada');
    }

    exportarAlunosCSV() {
        const alunos = this.alunos;
        
        let csv = 'ID,Nome,Data Nascimento,Idade,Email,Status,Turma\n';
        
        alunos.forEach(aluno => {
            const turma = this.turmas.find(t => t.id === aluno.turma_id);
            const idade = this.calcularIdade(aluno.data_nascimento);
            
            csv += `${aluno.id},"${aluno.nome}","${aluno.data_nascimento}",${idade},"${aluno.email || ''}","${aluno.status}","${turma ? turma.nome : 'Sem turma'}"\n`;
        });

        this.downloadFile(csv, 'alunos.csv', 'text/csv');
        this.showToast('CSV de alunos exportado com sucesso!', 'success');
    }

    exportarAlunosJSON() {
        const dados = {
            alunos: this.alunos.map(aluno => ({
                ...aluno,
                turma: this.turmas.find(t => t.id === aluno.turma_id)?.nome || 'Sem turma',
                idade: this.calcularIdade(aluno.data_nascimento)
            })),
            exportadoEm: new Date().toISOString(),
            totalAlunos: this.alunos.length
        };

        const json = JSON.stringify(dados, null, 2);
        this.downloadFile(json, 'alunos.json', 'application/json');
        this.showToast('JSON de alunos exportado com sucesso!', 'success');
    }

    exportarMatriculasCSV() {
        const matriculas = this.alunos.filter(aluno => aluno.turma_id);
        
        let csv = 'ID Aluno,Nome Aluno,ID Turma,Nome Turma,Data Matricula,Status\n';
        
        matriculas.forEach(aluno => {
            const turma = this.turmas.find(t => t.id === aluno.turma_id);
            
            csv += `${aluno.id},"${aluno.nome}",${aluno.turma_id},"${turma ? turma.nome : 'Turma não encontrada'}","${new Date().toISOString().split('T')[0]}","${aluno.status}"\n`;
        });

        this.downloadFile(csv, 'matriculas.csv', 'text/csv');
        this.showToast('CSV de matrículas exportado com sucesso!', 'success');
    }

    exportarMatriculasJSON() {
        const dados = {
            matriculas: this.alunos.filter(aluno => aluno.turma_id).map(aluno => ({
                alunoId: aluno.id,
                nomeAluno: aluno.nome,
                turmaId: aluno.turma_id,
                nomeTurma: this.turmas.find(t => t.id === aluno.turma_id)?.nome || 'Turma não encontrada',
                dataMatricula: new Date().toISOString().split('T')[0],
                status: aluno.status
            })),
            exportadoEm: new Date().toISOString(),
            totalMatriculas: this.alunos.filter(aluno => aluno.turma_id).length
        };

        const json = JSON.stringify(dados, null, 2);
        this.downloadFile(json, 'matriculas.json', 'application/json');
        this.showToast('JSON de matrículas exportado com sucesso!', 'success');
    }

    atualizarEstatisticas() {
        const totalAlunos = this.alunos.length;
        const alunosAtivos = this.alunos.filter(a => a.status === 'ativo').length;
        const totalTurmas = this.turmas.length;

        document.getElementById('totalAlunos').textContent = totalAlunos;
        document.getElementById('alunosAtivos').textContent = alunosAtivos;
        document.getElementById('totalTurmas').textContent = totalTurmas;
    }

    atualizarFiltros() {
        const turmaFilter = document.getElementById('filterTurma');
        const currentValue = turmaFilter?.value;
        
        if (turmaFilter) {
            turmaFilter.innerHTML = '<option value="">Todas as turmas</option>';
            this.turmas.forEach(turma => {
                const option = document.createElement('option');
                option.value = turma.id;
                option.textContent = turma.nome;
                turmaFilter.appendChild(option);
            });
            
            if (currentValue) turmaFilter.value = currentValue;
        }
    }

    atualizarPaginacao() {
        const totalPaginas = this.calcularTotalPaginas();
        const pageInfo = document.getElementById('pageInfo');
        const btnPrev = document.getElementById('btnPrevPage');
        const btnNext = document.getElementById('btnNextPage');

        pageInfo.textContent = `Página ${this.paginaAtual} de ${totalPaginas}`;
        btnPrev.disabled = this.paginaAtual === 1;
        btnNext.disabled = this.paginaAtual === totalPaginas || totalPaginas === 0;
    }

    calcularIdade(dataNascimento) {
        const hoje = new Date();
        const nascimento = new Date(dataNascimento);
        let idade = hoje.getFullYear() - nascimento.getFullYear();
        
        const mesAtual = hoje.getMonth();
        const mesNascimento = nascimento.getMonth();
        
        if (mesAtual < mesNascimento || (mesAtual === mesNascimento && hoje.getDate() < nascimento.getDate())) {
            idade--;
        }
        
        return idade;
    }

    salvarOrdenacao() {
        localStorage.setItem('escola_ordenacao', JSON.stringify(this.ordenacao));
    }

    carregarOrdenacao() {
        const ordenacaoSalva = localStorage.getItem('escola_ordenacao');
        if (ordenacaoSalva) {
            this.ordenacao = JSON.parse(ordenacaoSalva);
            document.getElementById('sortSelect').value = `${this.ordenacao.campo}-${this.ordenacao.direcao}`;
        }
    }

    // Funções dos Modais
    configurarModais() {
        // Modal Aluno
        const modalAluno = document.getElementById('modalAluno');
        const closeModalAluno = modalAluno.querySelector('.close-btn');
        
        closeModalAluno.addEventListener('click', () => {
            this.fecharModalAluno();
        });
        
        modalAluno.addEventListener('click', (e) => {
            if (e.target === modalAluno) {
                this.fecharModalAluno();
            }
        });

        // Modal Turma
        const modalTurma = document.getElementById('modalTurma');
        const closeModalTurma = modalTurma.querySelector('.close-btn');
        
        closeModalTurma.addEventListener('click', () => {
            this.fecharModalTurma();
        });
        
        modalTurma.addEventListener('click', (e) => {
            if (e.target === modalTurma) {
                this.fecharModalTurma();
            }
        });

        // Event listeners já configurados na seção principal

        // Botão limpar filtros
        document.getElementById('clearFilters').addEventListener('click', () => {
            this.limparFiltros();
        });

        // Botões de exportação
        this.configurarBotoesExportacao();
    }

    configurarBotoesExportacao() {
        // Eventos dos botões de exportação
        document.getElementById('exportAlunosCSV').addEventListener('click', () => {
            this.exportarAlunosCSV();
        });

        document.getElementById('exportAlunosJSON').addEventListener('click', () => {
            this.exportarAlunosJSON();
        });

        document.getElementById('exportMatriculasCSV').addEventListener('click', () => {
            this.exportarMatriculasCSV();
        });

        document.getElementById('exportMatriculasJSON').addEventListener('click', () => {
            this.exportarMatriculasJSON();
        });
    }

    abrirModalAluno(aluno = null) {
        const modal = document.getElementById('modalAluno');
        const form = document.getElementById('alunoForm');
        const title = document.getElementById('modalAlunoTitle');
        
        // Limpar formulário
        form.reset();
        
        if (aluno) {
            // Editando aluno existente
            title.textContent = 'Editar Aluno';
            form.dataset.alunoId = aluno.id;
            document.getElementById('alunoNome').value = aluno.nome;
            document.getElementById('alunoDataNascimento').value = aluno.data_nascimento;
            document.getElementById('alunoEmail').value = aluno.email || '';
            document.getElementById('alunoStatus').value = aluno.status;
            document.getElementById('alunoTurma').value = aluno.turma_id || '';
        } else {
            // Novo aluno
            title.textContent = 'Novo Aluno';
            form.dataset.alunoId = '';
            document.getElementById('alunoStatus').value = 'ativo';
        }
        
        // Carregar turmas no select
        this.carregarTurmasSelect();
        
        modal.style.display = 'block';
        modal.setAttribute('aria-hidden', 'false');
        document.getElementById('alunoNome').focus();
    }

    fecharModalAluno() {
        const modal = document.getElementById('modalAluno');
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
    }

    abrirModalTurma(turma = null) {
        const modal = document.getElementById('modalTurma');
        const form = document.getElementById('turmaForm');
        const title = document.getElementById('modalTurmaTitle');
        
        // Limpar formulário
        form.reset();
        
        if (turma) {
            // Editando turma existente
            title.textContent = 'Editar Turma';
            form.dataset.turmaId = turma.id;
            document.getElementById('turmaNome').value = turma.nome;
            document.getElementById('turmaCapacidade').value = turma.capacidade;
        } else {
            // Nova turma
            title.textContent = 'Nova Turma';
            form.dataset.turmaId = '';
            document.getElementById('turmaCapacidade').value = '30';
        }
        
        modal.style.display = 'block';
        modal.setAttribute('aria-hidden', 'false');
        document.getElementById('turmaNome').focus();
    }

    fecharModalTurma() {
        const modal = document.getElementById('modalTurma');
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
    }

    abrirModalMatricula() {
        const modal = document.getElementById('modalMatricula');
        const form = document.getElementById('matriculaForm');
        const title = document.getElementById('modalMatriculaTitle');
        
        // Limpar formulário
        if (form) form.reset();
        
        // Configurar modal
        title.textContent = 'Nova Matrícula';
        
        modal.style.display = 'block';
        modal.setAttribute('aria-hidden', 'false');
        
        // Focar no primeiro campo se existir
        const firstInput = form?.querySelector('input, select');
        if (firstInput) firstInput.focus();
    }

    fecharModalMatricula() {
        const modal = document.getElementById('modalMatricula');
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
    }

    async salvarAluno() {
        console.log('🚀 salvarAluno() chamada!');
        const form = document.getElementById('alunoForm');
        const formData = new FormData(form);
        
        const aluno = {
            nome: formData.get('nome'),
            data_nascimento: formData.get('data_nascimento'),
            email: formData.get('email'),
            status: formData.get('status'),
            turma_id: formData.get('turma_id') ? parseInt(formData.get('turma_id')) : null
        };
        
        console.log('📊 Dados do aluno:', aluno);

        // Validação
        if (!aluno.nome.trim()) {
            this.showToast('Nome é obrigatório', 'error');
            return;
        }

        if (!aluno.data_nascimento) {
            this.showToast('Data de nascimento é obrigatória', 'error');
            return;
        }

        try {
            const alunoId = form.dataset.alunoId;
            let response;
            
            console.log('📡 Enviando requisição para API...');

            if (alunoId) {
                // Atualizar aluno existente
                console.log('✏️ Atualizando aluno ID:', alunoId);
                response = await fetch(`http://localhost:8000/alunos/${alunoId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(aluno)
                });
            } else {
                // Criar novo aluno
                console.log('➕ Criando novo aluno');
                response = await fetch('http://localhost:8000/alunos', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(aluno)
                });
            }
            
            console.log('📨 Response status:', response.status);

            if (response.ok) {
                this.showToast(alunoId ? 'Aluno atualizado!' : 'Aluno cadastrado!', 'success');
                this.fecharModalAluno();
                await this.carregarDados();
                this.renderizar();
            } else {
                const error = await response.json();
                this.showToast('Erro ao salvar aluno: ' + (error.detail || 'Erro desconhecido'), 'error');
            }
        } catch (error) {
            console.error('Erro:', error);
            this.showToast('Erro ao conectar com o servidor', 'error');
        }
    }

    async salvarTurma() {
        const form = document.getElementById('turmaForm');
        const formData = new FormData(form);
        
        const turma = {
            nome: formData.get('nome'),
            capacidade: parseInt(formData.get('capacidade'))
        };

        // Validação
        if (!turma.nome.trim()) {
            this.showToast('Nome da turma é obrigatório', 'error');
            return;
        }

        if (!turma.capacidade || turma.capacidade < 1) {
            this.showToast('Capacidade deve ser maior que zero', 'error');
            return;
        }

        try {
            const turmaId = form.dataset.turmaId;
            let response;

            if (turmaId) {
                // Atualizar turma existente
                response = await fetch(`http://localhost:8000/turmas/${turmaId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(turma)
                });
            } else {
                // Criar nova turma
                response = await fetch('http://localhost:8000/turmas', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(turma)
                });
            }

            if (response.ok) {
                this.showToast(turmaId ? 'Turma atualizada!' : 'Turma cadastrada!', 'success');
                this.fecharModalTurma();
                await this.carregarDados();
                this.renderizar();
            } else {
                const error = await response.json();
                this.showToast('Erro ao salvar turma: ' + (error.detail || 'Erro desconhecido'), 'error');
            }
        } catch (error) {
            console.error('Erro:', error);
            this.showToast('Erro ao conectar com o servidor', 'error');
        }
    }

    exportarCSV() {
        const alunosFiltrados = this.obterAlunosFiltrados();
        
        let csv = 'Nome,Data Nascimento,Idade,Email,Status,Turma\n';
        
        alunosFiltrados.forEach(aluno => {
            const turma = this.turmas.find(t => t.id === aluno.turma_id);
            const idade = this.calcularIdade(aluno.data_nascimento);
            
            csv += `"${aluno.nome}","${aluno.data_nascimento}","${idade}","${aluno.email || ''}","${aluno.status}","${turma ? turma.nome : ''}"\n`;
        });

        this.downloadFile(csv, 'alunos.csv', 'text/csv');
        this.showToast('CSV exportado com sucesso!', 'success');
    }

    exportarJSON() {
        const alunosFiltrados = this.obterAlunosFiltrados();
        const dados = {
            alunos: alunosFiltrados,
            turmas: this.turmas,
            exportadoEm: new Date().toISOString()
        };

        const json = JSON.stringify(dados, null, 2);
        this.downloadFile(json, 'alunos.json', 'application/json');
        this.showToast('JSON exportado com sucesso!', 'success');
    }

    downloadFile(content, filename, contentType) {
        const blob = new Blob([content], { type: contentType });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    showToast(message, type = 'info') {
        // Criar elemento do toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span>${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
        `;

        // Adicionar ao container de toasts
        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        container.appendChild(toast);

        // Remover automaticamente após 5 segundos
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);

        // Anunciar para screen readers
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            announcement.remove();
        }, 1000);
    }
}

// Inicializar aplicação quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    window.app = new EscolaApp();
});

// Função para alternar entre seções
function showSection(sectionName) {
    // Esconder todas as seções
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });

    // Mostrar seção selecionada
    document.getElementById(sectionName).style.display = 'block';

    // Atualizar navegação ativa
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[onclick="showSection('${sectionName}')"]`).classList.add('active');

    // Renderizar dados se necessário
    if (window.app) {
        if (sectionName === 'alunos') {
            window.app.renderizarAlunos();
            window.app.atualizarPaginacao();
        } else if (sectionName === 'turmas') {
            window.app.renderizarTurmas();
        }
    }
}
