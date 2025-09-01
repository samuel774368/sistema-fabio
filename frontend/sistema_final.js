class SistemaEscolar {
    constructor() {
        this.API_BASE = 'http://localhost:8000';
        this.alunos = [];
        this.turmas = [];
        this.matriculas = [];
        this.init();
    }

    async init() {
        console.log('🚀 Iniciando Sistema Escolar...');
        this.configurarEventos();
        await this.carregarDados();
        this.renderizar();
        console.log('✅ Sistema inicializado!');
    }

    configurarEventos() {
        // Tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.dataset.tab;
                this.trocarTab(tab);
            });
        });

        // Botões principais
        document.getElementById('newAlunoBtn').addEventListener('click', () => this.abrirModalAluno());
        document.getElementById('newTurmaBtn').addEventListener('click', () => this.abrirModalTurma());
        document.getElementById('newMatriculaBtn').addEventListener('click', () => this.abrirModalMatricula());

        // Formulários
        document.getElementById('alunoForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.salvarAluno();
        });

        document.getElementById('turmaForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.salvarTurma();
        });

        document.getElementById('matriculaForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.salvarMatricula();
        });

        // Botões fechar modais
        document.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this.fecharModal(modal.id);
            });
        });

        // Clique fora do modal
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.fecharModal(modal.id);
                }
            });
        });

        // Busca
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.filtrarAlunos(e.target.value);
        });
        
        // Configurar botões de exportação
        this.configurarBotoesExportacao();
    }
    
    configurarBotoesExportacao() {
        const csvBtn = document.getElementById('exportAlunosCSV');
        const jsonBtn = document.getElementById('exportAlunosJSON');
        
        if (csvBtn && !csvBtn.dataset.configured) {
            csvBtn.addEventListener('click', () => this.exportarCSV());
            csvBtn.dataset.configured = 'true';
        }
        
        if (jsonBtn && !jsonBtn.dataset.configured) {
            jsonBtn.addEventListener('click', () => this.exportarJSON());
            jsonBtn.dataset.configured = 'true';
        }
    }

    trocarTab(tabName) {
        console.log('🔄 Trocando para tab:', tabName);
        
        // Desativar todas as tabs
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

        // Ativar tab selecionada
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        if (tabName === 'relatorios') {
            document.getElementById('relatorios-panel').classList.add('active');
        } else if (tabName === 'turmas') {
            document.getElementById('turmas-panel').classList.add('active');
        } else if (tabName === 'alunos') {
            document.getElementById('alunos-panel').classList.add('active');
        } else {
            document.getElementById(tabName).classList.add('active');
        }

        // Renderizar conteúdo específico
        if (tabName === 'alunos') {
            this.renderizarAlunos();
        } else if (tabName === 'turmas') {
            this.renderizarTurmas();
        } else if (tabName === 'relatorios') {
            this.renderizarRelatorios();
        }
    }

    async carregarDados() {
        try {
            console.log('📡 Carregando dados...');
            
            const [alunosRes, turmasRes, matriculasRes] = await Promise.all([
                fetch(`${this.API_BASE}/alunos`),
                fetch(`${this.API_BASE}/turmas`),
                fetch(`${this.API_BASE}/matriculas`)
            ]);

            this.alunos = await alunosRes.json();
            this.turmas = await turmasRes.json();
            this.matriculas = await matriculasRes.json();

            console.log(`✅ Carregados: ${this.alunos.length} alunos, ${this.turmas.length} turmas`);
        } catch (error) {
            console.error('❌ Erro ao carregar dados:', error);
            this.showToast('Erro ao carregar dados', 'error');
        }
    }

    renderizar() {
        this.renderizarAlunos();
        this.atualizarEstatisticas();
        this.atualizarFiltros();
    }

    renderizarAlunos() {
        const container = document.getElementById('alunosList');
        if (!container) return;

        if (this.alunos.length === 0) {
            container.innerHTML = '<p class="no-data">Nenhum aluno cadastrado</p>';
            return;
        }

        container.innerHTML = this.alunos.map(aluno => {
            const turma = this.turmas.find(t => t.id === aluno.turma_id);
            const idade = this.calcularIdade(aluno.data_nascimento);
            
            return `
                <div class="aluno-card">
                    <h3>${aluno.nome}</h3>
                    <p><strong>Idade:</strong> ${idade} anos</p>
                    <p><strong>Email:</strong> ${aluno.email}</p>
                    <p><strong>Status:</strong> <span class="status ${aluno.status}">${aluno.status}</span></p>
                    <p><strong>Turma:</strong> ${turma ? turma.nome : 'Sem turma'}</p>
                    <div class="actions">
                        <button onclick="sistema.editarAluno(${aluno.id})" class="btn-edit">Editar</button>
                        <button onclick="sistema.excluirAluno(${aluno.id})" class="btn-delete">Excluir</button>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderizarTurmas() {
        const container = document.getElementById('turmasList');
        console.log('🏫 renderizarTurmas - container:', container);
        console.log('🏫 renderizarTurmas - turmas:', this.turmas);
        
        if (!container) return;

        if (this.turmas.length === 0) {
            container.innerHTML = '<p class="no-data">Nenhuma turma cadastrada</p>';
            return;
        }

        container.innerHTML = this.turmas.map(turma => {
            const alunosNaTurma = this.alunos.filter(a => a.turma_id === turma.id).length;
            
            return `
                <div class="turma-card">
                    <h3>${turma.nome}</h3>
                    <p><strong>Capacidade:</strong> ${turma.capacidade} alunos</p>
                    <p><strong>Matriculados:</strong> ${alunosNaTurma} alunos</p>
                    <p><strong>Vagas disponíveis:</strong> ${turma.capacidade - alunosNaTurma}</p>
                    <div class="actions">
                        <button onclick="sistema.editarTurma(${turma.id})" class="btn-edit">Editar</button>
                        <button onclick="sistema.excluirTurma(${turma.id})" class="btn-delete">Excluir</button>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderizarRelatorios() {
        const container = document.getElementById('relatoriosContent');
        if (!container) return;

        const totalAlunos = this.alunos.length;
        const alunosAtivos = this.alunos.filter(a => a.status === 'ativo').length;
        const totalTurmas = this.turmas.length;

            container.innerHTML = `
            <div class="relatorio-card">
                <h3>Estatísticas Gerais</h3>
                <p><strong>Total de Alunos:</strong> ${totalAlunos}</p>
                <p><strong>Alunos Ativos:</strong> ${alunosAtivos}</p>
                <p><strong>Total de Turmas:</strong> ${totalTurmas}</p>
            </div>
        `;
        
        // Configurar botões de exportação
        setTimeout(() => this.configurarBotoesExportacao(), 100);
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
        const select = document.getElementById('filtroTurma');
        if (!select) return;

        select.innerHTML = '<option value="">Todas as turmas</option>';
        this.turmas.forEach(turma => {
            select.innerHTML += `<option value="${turma.id}">${turma.nome}</option>`;
        });
    }

    // MODAL ALUNO
    abrirModalAluno(aluno = null) {
        const modal = document.getElementById('modalAluno');
        const form = document.getElementById('alunoForm');
        const title = document.getElementById('modalAlunoTitle');

        form.reset();
        
        if (aluno) {
            title.textContent = 'Editar Aluno';
            form.dataset.alunoId = aluno.id;
            form.nome.value = aluno.nome;
            form.data_nascimento.value = aluno.data_nascimento;
            form.email.value = aluno.email;
            form.status.value = aluno.status;
            form.turma_id.value = aluno.turma_id || '';
        } else {
            title.textContent = 'Novo Aluno';
            delete form.dataset.alunoId;
        }

        // Preencher select de turmas
        const selectTurma = form.turma_id;
        selectTurma.innerHTML = '<option value="">Selecione uma turma</option>';
        this.turmas.forEach(turma => {
            selectTurma.innerHTML += `<option value="${turma.id}">${turma.nome}</option>`;
        });

        modal.style.display = 'block';
    }

    // MODAL TURMA
    abrirModalTurma(turma = null) {
        const modal = document.getElementById('modalTurma');
        const form = document.getElementById('turmaForm');
        const title = document.getElementById('modalTurmaTitle');

        form.reset();
        
        if (turma) {
            title.textContent = 'Editar Turma';
            form.dataset.turmaId = turma.id;
            form.nome.value = turma.nome;
            form.capacidade.value = turma.capacidade;
        } else {
            title.textContent = 'Nova Turma';
            delete form.dataset.turmaId;
        }

        modal.style.display = 'block';
    }

    // MODAL MATRÍCULA
    abrirModalMatricula() {
        const modal = document.getElementById('modalMatricula');
        const form = document.getElementById('matriculaForm');

        form.reset();

        // Preencher selects
        const selectAluno = form.aluno_id;
        const selectTurma = form.turma_id;

        selectAluno.innerHTML = '<option value="">Selecione um aluno</option>';
        this.alunos.forEach(aluno => {
            selectAluno.innerHTML += `<option value="${aluno.id}">${aluno.nome}</option>`;
        });

        selectTurma.innerHTML = '<option value="">Selecione uma turma</option>';
        this.turmas.forEach(turma => {
            selectTurma.innerHTML += `<option value="${turma.id}">${turma.nome}</option>`;
        });

        modal.style.display = 'block';
    }

    fecharModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    // SALVAR ALUNO
    async salvarAluno() {
        const form = document.getElementById('alunoForm');
        const formData = new FormData(form);

        const aluno = {
            nome: formData.get('nome'),
            data_nascimento: formData.get('data_nascimento'),
            email: formData.get('email'),
            status: formData.get('status'),
            turma_id: formData.get('turma_id') ? parseInt(formData.get('turma_id')) : null
        };

        console.log('💾 Salvando aluno:', aluno);

        if (!aluno.nome.trim()) {
            this.showToast('Nome é obrigatório', 'error');
            return;
        }

        if (!aluno.email.trim()) {
            this.showToast('Email é obrigatório', 'error');
            return;
        }

        try {
            const alunoId = form.dataset.alunoId;
            let response;

            if (alunoId) {
                // Atualizar
                response = await fetch(`${this.API_BASE}/alunos/${alunoId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(aluno)
                });
            } else {
                // Criar
                response = await fetch(`${this.API_BASE}/alunos`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(aluno)
                });
            }

            if (response.ok) {
                this.showToast(alunoId ? 'Aluno atualizado!' : 'Aluno cadastrado!', 'success');
                this.fecharModal('modalAluno');
                await this.carregarDados();
                this.renderizar();
            } else {
                const error = await response.json();
                this.showToast('Erro: ' + error.detail, 'error');
            }
        } catch (error) {
            console.error('❌ Erro ao salvar aluno:', error);
            this.showToast('Erro ao conectar com servidor', 'error');
        }
    }

    // SALVAR TURMA
    async salvarTurma() {
        const form = document.getElementById('turmaForm');
        const formData = new FormData(form);

        const turma = {
            nome: formData.get('nome'),
            capacidade: parseInt(formData.get('capacidade'))
        };

        console.log('💾 Salvando turma:', turma);

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
                // Atualizar
                response = await fetch(`${this.API_BASE}/turmas/${turmaId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(turma)
                });
            } else {
                // Criar
                response = await fetch(`${this.API_BASE}/turmas`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(turma)
                });
            }

            if (response.ok) {
                this.showToast(turmaId ? 'Turma atualizada!' : 'Turma cadastrada!', 'success');
                this.fecharModal('modalTurma');
                await this.carregarDados();
                this.renderizar();
            } else {
                const error = await response.json();
                this.showToast('Erro: ' + error.detail, 'error');
            }
        } catch (error) {
            console.error('❌ Erro ao salvar turma:', error);
            this.showToast('Erro ao conectar com servidor', 'error');
        }
    }

    // SALVAR MATRÍCULA
    async salvarMatricula() {
        const form = document.getElementById('matriculaForm');
        const formData = new FormData(form);

        const matricula = {
            aluno_id: parseInt(formData.get('aluno_id')),
            turma_id: parseInt(formData.get('turma_id'))
        };

        console.log('💾 Salvando matrícula:', matricula);

        if (!matricula.aluno_id) {
            this.showToast('Selecione um aluno', 'error');
            return;
        }

        if (!matricula.turma_id) {
            this.showToast('Selecione uma turma', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.API_BASE}/matriculas`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(matricula)
            });

            if (response.ok) {
                this.showToast('Matrícula realizada!', 'success');
                this.fecharModal('modalMatricula');
                await this.carregarDados();
                this.renderizar();
            } else {
                const error = await response.json();
                this.showToast('Erro: ' + error.detail, 'error');
            }
        } catch (error) {
            console.error('❌ Erro ao salvar matrícula:', error);
            this.showToast('Erro ao conectar com servidor', 'error');
        }
    }

    // EDITAR/EXCLUIR
    editarAluno(id) {
        const aluno = this.alunos.find(a => a.id === id);
        if (aluno) {
            this.abrirModalAluno(aluno);
        }
    }

    async excluirAluno(id) {
        if (!confirm('Tem certeza que deseja excluir este aluno?')) return;

        try {
            const response = await fetch(`${this.API_BASE}/alunos/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Aluno excluído!', 'success');
                await this.carregarDados();
                this.renderizar();
            } else {
                this.showToast('Erro ao excluir aluno', 'error');
            }
        } catch (error) {
            console.error('❌ Erro ao excluir aluno:', error);
            this.showToast('Erro ao conectar com servidor', 'error');
        }
    }

    editarTurma(id) {
        const turma = this.turmas.find(t => t.id === id);
        if (turma) {
            this.abrirModalTurma(turma);
        }
    }

    async excluirTurma(id) {
        if (!confirm('Tem certeza que deseja excluir esta turma?')) return;

        try {
            const response = await fetch(`${this.API_BASE}/turmas/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Turma excluída!', 'success');
                await this.carregarDados();
                this.renderizar();
            } else {
                this.showToast('Erro ao excluir turma', 'error');
            }
        } catch (error) {
            console.error('❌ Erro ao excluir turma:', error);
            this.showToast('Erro ao conectar com servidor', 'error');
        }
    }

    // FILTROS
    filtrarAlunos(termo) {
        if (!termo || termo.trim() === '') {
            // Se não há termo de busca, mostrar todos os alunos
            this.renderizarAlunos();
            return;
        }
        
        const alunosFiltrados = this.alunos.filter(aluno => 
            aluno.nome.toLowerCase().includes(termo.toLowerCase()) ||
            (aluno.email && aluno.email.toLowerCase().includes(termo.toLowerCase()))
        );

        // Renderizar apenas os filtrados
        this.renderizarAlunosFiltrados(alunosFiltrados);
    }

    renderizarAlunosFiltrados(alunos) {
        const container = document.getElementById('alunosList');
        if (!container) return;

        container.innerHTML = alunos.map(aluno => {
            const turma = this.turmas.find(t => t.id === aluno.turma_id);
            const idade = this.calcularIdade(aluno.data_nascimento);
            
            return `
                <div class="aluno-card">
                    <h3>${aluno.nome}</h3>
                    <p><strong>Idade:</strong> ${idade} anos</p>
                    <p><strong>Email:</strong> ${aluno.email}</p>
                    <p><strong>Status:</strong> <span class="status ${aluno.status}">${aluno.status}</span></p>
                    <p><strong>Turma:</strong> ${turma ? turma.nome : 'Sem turma'}</p>
                    <div class="actions">
                        <button onclick="sistema.editarAluno(${aluno.id})" class="btn-edit">Editar</button>
                        <button onclick="sistema.excluirAluno(${aluno.id})" class="btn-delete">Excluir</button>
                    </div>
                </div>
            `;
        }).join('');
    }

    // EXPORTAR
    exportarCSV() {
        const csv = this.gerarCSV();
        this.downloadFile(csv, 'alunos.csv', 'text/csv');
        this.showToast('CSV exportado!', 'success');
    }

    exportarJSON() {
        const json = JSON.stringify(this.alunos, null, 2);
        this.downloadFile(json, 'alunos.json', 'application/json');
        this.showToast('JSON exportado!', 'success');
    }

    gerarCSV() {
        const headers = ['ID', 'Nome', 'Email', 'Data Nascimento', 'Status', 'Turma'];
        const rows = this.alunos.map(aluno => {
            const turma = this.turmas.find(t => t.id === aluno.turma_id);
            return [
                aluno.id,
                aluno.nome,
                aluno.email,
                aluno.data_nascimento,
                aluno.status,
                turma ? turma.nome : 'Sem turma'
            ];
        });

        const csvContent = [headers, ...rows]
            .map(row => row.map(field => `"${field}"`).join(','))
            .join('\n');

        return csvContent;
    }

    downloadFile(content, filename, type) {
        const blob = new Blob([content], { type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    // UTILITÁRIOS
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

    showToast(message, type = 'info') {
        // Remove toast anterior se existir
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            existingToast.remove();
        }

        // Cria novo toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;

        // Adiciona ao DOM
        document.body.appendChild(toast);

        // Remove após 3 segundos
        setTimeout(() => {
            toast.remove();
        }, 3000);

        console.log(`🔔 ${type.toUpperCase()}: ${message}`);
    }
}

// Inicializar sistema
let sistema;
document.addEventListener('DOMContentLoaded', () => {
    sistema = new SistemaEscolar();
});
