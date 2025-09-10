class PortalUsuario {
    constructor() {
        this.API_BASE = window.API_BASE || 'http://localhost:8002';
        this.alunos = [];
        this.turmas = [];
        this.solicitacoes = [];
        this.currentUser = null;
        this.token = null;
        this.init();
    }

    async init() {
        console.log('🚀 Iniciando Portal do Usuário...');
        
        // Verificar autenticação
        if (!this.verificarAutenticacao()) {
            window.location.href = 'login.html';
            return;
        }

        await this.carregarUsuario();
        this.configurarEventos();
        await this.carregarDados();
        this.renderizar();
        console.log('✅ Portal inicializado!');
    }

    verificarAutenticacao() {
        this.token = localStorage.getItem('token');
        const user = localStorage.getItem('user');
        
        if (!this.token || !user) {
            return false;
        }

        try {
            this.currentUser = JSON.parse(user);
            return true;
        } catch (error) {
            console.error('Erro ao parsear dados do usuário:', error);
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            return false;
        }
    }

    async carregarUsuario() {
        try {
            const response = await this.fazerRequisicao('/me');
            if (response.ok) {
                const userData = await response.json();
                this.currentUser = userData;
                localStorage.setItem('user', JSON.stringify(userData));
                this.atualizarInterfaceUsuario();
            } else {
                throw new Error('Falha ao carregar dados do usuário');
            }
        } catch (error) {
            console.error('Erro ao carregar usuário:', error);
            this.logout();
        }
    }

    atualizarInterfaceUsuario() {
        const userWelcome = document.getElementById('userWelcome');
        if (userWelcome && this.currentUser) {
            userWelcome.textContent = `👋 Olá, ${this.currentUser.username}!`;
        }
    }

    fazerRequisicao(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            }
        };

        return fetch(`${this.API_BASE}${endpoint}`, {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        });
    }

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    }

    configurarEventos() {
        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => {
            if (confirm('Deseja realmente sair do sistema?')) {
                this.logout();
            }
        });

        // Perfil
        document.getElementById('perfilBtn').addEventListener('click', () => {
            this.abrirModalPerfil();
        });

        // Solicitar Matrícula
        document.getElementById('solicitarMatriculaBtn').addEventListener('click', () => {
            this.abrirModalSolicitacao();
        });

        // Fechar modal de perfil
        const closeBtn = document.querySelector('#modalPerfil .close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                document.getElementById('modalPerfil').style.display = 'none';
            });
        }

        // Clique fora do modal
        const modal = document.getElementById('modalPerfil');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }

        // Busca
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.filtrarAlunos(e.target.value);
        });

        // Filtro por turma
        document.getElementById('filtroTurma').addEventListener('change', (e) => {
            this.filtrarPorTurma(e.target.value);
        });

        // Filtro por status
        document.getElementById('filtroStatus').addEventListener('change', (e) => {
            this.filtrarPorStatus(e.target.value);
        });
    }

    async carregarDados() {
        try {
            console.log('📡 Carregando dados...');
            
            // Para usuários comuns, carregar apenas seus alunos
            const alunosEndpoint = this.currentUser.tipo_usuario === 'admin' ? '/alunos' : '/meus-alunos';
            
            const [alunosRes, turmasRes, solicitacoesRes] = await Promise.all([
                this.fazerRequisicao(alunosEndpoint),
                this.fazerRequisicao('/turmas'),
                this.fazerRequisicao('/solicitacoes-matricula')
            ]);

            if (alunosRes.ok) {
                this.alunos = await alunosRes.json();
            } else {
                console.error('Erro ao carregar alunos:', alunosRes.status);
                this.alunos = [];
            }

            if (turmasRes.ok) {
                this.turmas = await turmasRes.json();
            } else {
                console.error('Erro ao carregar turmas:', turmasRes.status);
                this.turmas = [];
            }

            if (solicitacoesRes.ok) {
                this.solicitacoes = await solicitacoesRes.json();
            } else {
                console.error('Erro ao carregar solicitações:', solicitacoesRes.status);
                this.solicitacoes = [];
            }

            console.log(`✅ Carregados: ${this.alunos.length} alunos, ${this.turmas.length} turmas, ${this.solicitacoes.length} solicitações`);
        } catch (error) {
            console.error('❌ Erro ao carregar dados:', error);
            this.showToast('Erro ao carregar dados', 'error');
        }
    }

    renderizar() {
        this.renderizarAlunos();
        this.renderizarSolicitacoes();
        this.atualizarEstatisticas();
        this.atualizarFiltros();
    }

    renderizarAlunos() {
        const container = document.getElementById('alunosList');
        if (!container) return;

        if (this.alunos.length === 0) {
            container.innerHTML = `
                <div class="no-permissions">
                    <div class="icon">📚</div>
                    <h3>Nenhum aluno cadastrado</h3>
                    <p>Ainda não há alunos no sistema.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.alunos.map(aluno => {
            const turma = this.turmas.find(t => t.id === aluno.turma_id);
            const idade = this.calcularIdade(aluno.data_nascimento);
            
            return `
                <div class="aluno-card">
                    <h3>${aluno.nome}</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="label">🎂 Idade</span>
                            <span class="value">${idade} anos</span>
                        </div>
                        <div class="info-item">
                            <span class="label">📧 Email</span>
                            <span class="value">${aluno.email || 'Não informado'}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">📊 Status</span>
                            <span class="value status ${aluno.status}">${aluno.status}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">🏫 Turma</span>
                            <span class="value">${turma ? turma.nome : 'Sem turma'}</span>
                        </div>
                    </div>
                    <!-- Usuários comuns não têm botões de ação -->
                </div>
            `;
        }).join('');
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

        select.innerHTML = '<option value="">📋 Todas as turmas</option>';
        this.turmas.forEach(turma => {
            select.innerHTML += `<option value="${turma.id}">🏫 ${turma.nome}</option>`;
        });
    }

    filtrarAlunos(termo) {
        if (!termo || termo.trim() === '') {
            this.renderizarAlunos();
            return;
        }
        
        const alunosFiltrados = this.alunos.filter(aluno => 
            aluno.nome.toLowerCase().includes(termo.toLowerCase()) ||
            (aluno.email && aluno.email.toLowerCase().includes(termo.toLowerCase()))
        );

        this.renderizarAlunosFiltrados(alunosFiltrados);
    }

    filtrarPorTurma(turmaId) {
        if (!turmaId) {
            this.renderizarAlunos();
            return;
        }

        const alunosFiltrados = this.alunos.filter(aluno => 
            aluno.turma_id === parseInt(turmaId)
        );

        this.renderizarAlunosFiltrados(alunosFiltrados);
    }

    filtrarPorStatus(status) {
        if (!status) {
            this.renderizarAlunos();
            return;
        }

        const alunosFiltrados = this.alunos.filter(aluno => 
            aluno.status === status
        );

        this.renderizarAlunosFiltrados(alunosFiltrados);
    }

    renderizarAlunosFiltrados(alunos) {
        const container = document.getElementById('alunosList');
        if (!container) return;

        if (alunos.length === 0) {
            container.innerHTML = `
                <div class="no-permissions">
                    <div class="icon">🔍</div>
                    <h3>Nenhum resultado encontrado</h3>
                    <p>Tente ajustar os filtros de busca.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = alunos.map(aluno => {
            const turma = this.turmas.find(t => t.id === aluno.turma_id);
            const idade = this.calcularIdade(aluno.data_nascimento);
            
            return `
                <div class="aluno-card">
                    <h3>${aluno.nome}</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="label">🎂 Idade</span>
                            <span class="value">${idade} anos</span>
                        </div>
                        <div class="info-item">
                            <span class="label">📧 Email</span>
                            <span class="value">${aluno.email || 'Não informado'}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">📊 Status</span>
                            <span class="value status ${aluno.status}">${aluno.status}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">🏫 Turma</span>
                            <span class="value">${turma ? turma.nome : 'Sem turma'}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
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

    // MODAL DE PERFIL
    async abrirModalPerfil() {
        const modal = document.getElementById('modalPerfil');
        const content = document.getElementById('perfilContent');
        
        modal.style.display = 'flex';
        content.innerHTML = '<div style="text-align: center; padding: 2rem; color: #667eea;">🔄 Carregando informações do perfil...</div>';

        try {
            const response = await this.fazerRequisicao('/perfil');
            
            if (response.ok) {
                const perfil = await response.json();
                this.renderizarPerfilUsuario(perfil);
            } else {
                content.innerHTML = '<div style="text-align: center; padding: 2rem; color: #dc3545;">❌ Erro ao carregar perfil</div>';
            }
        } catch (error) {
            console.error('Erro ao carregar perfil:', error);
            content.innerHTML = '<div style="text-align: center; padding: 2rem; color: #dc3545;">❌ Erro de conexão</div>';
        }
    }

    renderizarPerfilUsuario(perfil) {
        const content = document.getElementById('perfilContent');
        
        content.innerHTML = `
            <div style="display: flex; align-items: center; gap: 1rem; padding: 1.5rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; border-radius: 15px; margin-bottom: 1.5rem; text-align: center;">
                <div style="width: 80px; height: 80px; border-radius: 50%; background: rgba(255, 255, 255, 0.2); display: flex; align-items: center; justify-content: center; font-size: 2rem; border: 3px solid rgba(255, 255, 255, 0.3);">
                    👤
                </div>
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 0.5rem 0; font-size: 1.5rem; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">${perfil.username}</h3>
                    <div style="background: rgba(255, 255, 255, 0.2); padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; display: inline-block;">
                        Usuário
                    </div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
                <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: none; border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
                    <div style="font-size: 1.2rem; font-weight: bold; color: #667eea; margin: 0.5rem 0;">Apenas Consulta</div>
                    <div style="font-size: 0.9rem; color: #6c757d; font-weight: 500;">Modo de Acesso</div>
                </div>
                <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: none; border-radius: 15px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⏱️</div>
                    <div style="font-size: 1.2rem; font-weight: bold; color: #667eea; margin: 0.5rem 0;">${perfil.tempo_login_atual}</div>
                    <div style="font-size: 0.9rem; color: #6c757d; font-weight: 500;">Tempo da Sessão</div>
                </div>
            </div>

            <div style="background: #f8f9fa; border-radius: 15px; padding: 1.5rem; border: 1px solid #e9ecef;">
                <h4 style="color: #495057; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">📊 Detalhes da Conta</h4>
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.8rem 0; border-bottom: 1px solid #e9ecef;">
                    <span style="font-weight: 500; color: #495057; display: flex; align-items: center; gap: 0.5rem;">📧 Email:</span>
                    <span style="color: #667eea; font-weight: 600;">${perfil.email}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.8rem 0; border-bottom: 1px solid #e9ecef;">
                    <span style="font-weight: 500; color: #495057; display: flex; align-items: center; gap: 0.5rem;">📅 Conta criada em:</span>
                    <span style="color: #667eea; font-weight: 600;">${perfil.data_criacao}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.8rem 0; border-bottom: 1px solid #e9ecef;">
                    <span style="font-weight: 500; color: #495057; display: flex; align-items: center; gap: 0.5rem;">🕐 Último login:</span>
                    <span style="color: #667eea; font-weight: 600;">${perfil.ultimo_login}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.8rem 0;">
                    <span style="font-weight: 500; color: #495057; display: flex; align-items: center; gap: 0.5rem;">🆔 ID do usuário:</span>
                    <span style="color: #667eea; font-weight: 600;">#${perfil.id}</span>
                </div>
                
                <div style="margin-top: 1.5rem; padding: 1rem; background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">ℹ️</div>
                    <p style="margin: 0; color: #555; font-size: 0.9rem;">
                        <strong>Modo Usuário:</strong> Você tem acesso apenas para visualização de dados. 
                        Para editar informações, entre em contato com um administrador.
                    </p>
                </div>
            </div>
        `;
    }

    // ==================== FUNÇÕES DE SOLICITAÇÕES DE MATRÍCULA ====================

    renderizarSolicitacoes() {
        const container = document.getElementById('solicitacoesList');
        if (!container) return;

        if (this.solicitacoes.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem; color: #666;">
                    <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.5;">📝</div>
                    <h3>Nenhuma solicitação de matrícula</h3>
                    <p>Você ainda não fez nenhuma solicitação de matrícula.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.solicitacoes.map(solicitacao => {
            const statusIcon = {
                'pendente': '⏳',
                'aprovada': '✅',
                'rejeitada': '❌'
            }[solicitacao.status] || '❓';

            const statusColor = {
                'pendente': '#ffa500',
                'aprovada': '#28a745',
                'rejeitada': '#dc3545'
            }[solicitacao.status] || '#6c757d';

            return `
                <div style="background: white; border-radius: 15px; padding: 1.5rem; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); margin-bottom: 1rem; border-left: 4px solid ${statusColor};">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                        <div>
                            <h3 style="margin: 0 0 0.5rem 0; color: #333; display: flex; align-items: center; gap: 0.5rem;">
                                ${statusIcon} ${solicitacao.nome_aluno}
                            </h3>
                            <p style="margin: 0; color: #666; font-size: 0.9rem;">
                                Solicitado em: ${new Date(solicitacao.data_solicitacao).toLocaleDateString('pt-BR')}
                            </p>
                        </div>
                        <span style="background: ${statusColor}; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; font-weight: 500; text-transform: uppercase;">
                            ${solicitacao.status}
                        </span>
                    </div>

                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                        <div>
                            <strong style="color: #495057;">📅 Data de Nascimento:</strong><br>
                            <span style="color: #667eea;">${new Date(solicitacao.data_nascimento).toLocaleDateString('pt-BR')}</span>
                        </div>
                        ${solicitacao.email_aluno ? `
                            <div>
                                <strong style="color: #495057;">📧 Email:</strong><br>
                                <span style="color: #667eea;">${solicitacao.email_aluno}</span>
                            </div>
                        ` : ''}
                        ${solicitacao.turma_solicitada ? `
                            <div>
                                <strong style="color: #495057;">🏫 Turma Solicitada:</strong><br>
                                <span style="color: #667eea;">${solicitacao.turma_solicitada}</span>
                            </div>
                        ` : ''}
                    </div>

                    ${solicitacao.observacoes ? `
                        <div style="margin-bottom: 1rem;">
                            <strong style="color: #495057;">📝 Observações:</strong><br>
                            <span style="color: #666;">${solicitacao.observacoes}</span>
                        </div>
                    ` : ''}

                    ${solicitacao.resposta_admin ? `
                        <div style="background: #f8f9fa; border-radius: 10px; padding: 1rem; margin-top: 1rem; border-left: 3px solid ${statusColor};">
                            <strong style="color: #495057;">💬 Resposta do Administrador:</strong><br>
                            <span style="color: #333;">${solicitacao.resposta_admin}</span>
                            ${solicitacao.data_resposta ? `
                                <br><small style="color: #666;">Respondido em: ${new Date(solicitacao.data_resposta).toLocaleDateString('pt-BR')}</small>
                            ` : ''}
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
    }

    abrirModalSolicitacao() {
        const modal = document.getElementById('modalSolicitacao');
        const form = document.getElementById('solicitacaoForm');
        
        // Resetar formulário
        form.reset();
        
        // Preencher select de turmas
        const selectTurma = document.getElementById('turmaSolicitada');
        selectTurma.innerHTML = '<option value="">Selecione uma turma (opcional)</option>';
        this.turmas.forEach(turma => {
            selectTurma.innerHTML += `<option value="${turma.nome}">${turma.nome}</option>`;
        });

        // Configurar evento de submit
        form.onsubmit = (e) => this.enviarSolicitacao(e);
        
        modal.style.display = 'flex';
    }

    async enviarSolicitacao(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const solicitacao = {
            nome_aluno: formData.get('nome_aluno'),
            data_nascimento: formData.get('data_nascimento'),
            email_aluno: formData.get('email_aluno') || null,
            turma_solicitada: formData.get('turma_solicitada') || null,
            observacoes: formData.get('observacoes') || null
        };

        try {
            const response = await this.fazerRequisicao('/solicitacoes-matricula', {
                method: 'POST',
                body: JSON.stringify(solicitacao)
            });

            if (response.ok) {
                const result = await response.json();
                alert('✅ ' + result.message);
                this.fecharModalSolicitacao();
                await this.carregarDados();
                this.renderizar();
            } else {
                const error = await response.json();
                alert('❌ Erro: ' + error.detail);
            }
        } catch (error) {
            console.error('Erro ao enviar solicitação:', error);
            alert('❌ Erro ao conectar com o servidor');
        }
    }

    fecharModalSolicitacao() {
        document.getElementById('modalSolicitacao').style.display = 'none';
    }
}

// Funções globais para os botões
function fecharModalSolicitacao() {
    document.getElementById('modalSolicitacao').style.display = 'none';
}

// Inicializar portal
let portal;
document.addEventListener('DOMContentLoaded', () => {
    portal = new PortalUsuario();
});
