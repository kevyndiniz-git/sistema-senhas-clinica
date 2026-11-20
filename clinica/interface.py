import tkinter as tk
from tkinter import messagebox, ttk

from clinica.constantes import CATEGORIAS, ESPECIALIDADES, NORMAL, PREFERENCIAL
from clinica.excecoes import ErroClinica
from clinica.gerenciador import GerenciadorSenhas

# Nome mostrado na tela -> código usado pelo sistema (ex.: 'Cardiologia' -> 'CA').
NOME_PARA_CODIGO = {nome: codigo for codigo, nome in ESPECIALIDADES.items()}


def formatar_hora(momento):
    return momento.strftime('%H:%M:%S') if momento else '-'


def formatar_espera(minutos):
    if minutos == 0:
        return 'Próximo a ser chamado'
    return f'{minutos} min'


class AplicacaoClinica(tk.Tk):
    # Janela principal do sistema de senhas.

    def __init__(self):
        super().__init__()
        self.title('Clínica Médica - Gerenciamento de Senhas')
        self.geometry('980x720')
        self.minsize(900, 680)

        self.gerenciador = GerenciadorSenhas()
        self.var_especialidade = tk.StringVar()
        self.var_categoria = tk.StringVar()
        self.var_mensagem = tk.StringVar(
            value='Selecione a especialidade e a categoria para emitir uma senha.'
        )

        self._criar_topo()
        self._criar_emissao()
        self._criar_painel()
        self._criar_tabelas()
        self._atualizar_tela()

    # ---------- construção da tela ----------
    def _criar_topo(self):
        quadro = ttk.LabelFrame(self, text='Especialidade')
        quadro.pack(fill='x', padx=10, pady=(10, 5))
        ttk.Label(quadro, text='Escolha a especialidade:').pack(
            side='left', padx=8, pady=8
        )
        self.combo = ttk.Combobox(
            quadro,
            textvariable=self.var_especialidade,
            values=list(NOME_PARA_CODIGO),
            state='readonly',
            width=25,
        )
        self.combo.pack(side='left', padx=8)
        self.combo.bind('<<ComboboxSelected>>', lambda evento: self._atualizar_tela())

    def _criar_emissao(self):
        # Cria também o quadro que abriga emissão (esquerda) e painel (direita).
        self.frame_meio = ttk.Frame(self)
        self.frame_meio.pack(fill='x', padx=10, pady=5)

        quadro = ttk.LabelFrame(self.frame_meio, text='Emissão de senha')
        quadro.pack(side='left', fill='both', expand=True, padx=(0, 5))
        ttk.Label(quadro, text='Categoria de atendimento:').pack(
            anchor='w', padx=8, pady=(8, 2)
        )
        for codigo, nome in CATEGORIAS.items():
            ttk.Radiobutton(
                quadro, text=nome, value=codigo, variable=self.var_categoria
            ).pack(anchor='w', padx=20)
        ttk.Button(quadro, text='Emitir senha', command=self._emitir).pack(pady=8)
        ttk.Label(
            quadro, textvariable=self.var_mensagem, wraplength=380, justify='left'
        ).pack(anchor='w', padx=8, pady=(0, 8))

    def _criar_painel(self):
        quadro = ttk.LabelFrame(self.frame_meio, text='Painel de atendimento')
        quadro.pack(side='left', fill='both', expand=True, padx=(5, 0))
        ttk.Label(quadro, text='Última senha chamada').pack(pady=(8, 0))
        self.lbl_senha = ttk.Label(quadro, text='---', font=('Arial', 36, 'bold'))
        self.lbl_senha.pack()
        self.lbl_detalhes = ttk.Label(quadro, text='Nenhuma senha chamada ainda.')
        self.lbl_detalhes.pack()
        self.lbl_aguardando = ttk.Label(quadro, text='', justify='center')
        self.lbl_aguardando.pack(pady=(8, 0))
        ttk.Button(
            quadro, text='Chamar próxima senha', command=self._chamar
        ).pack(pady=8)

    def _criar_tabelas(self):
        quadro = ttk.LabelFrame(self, text='Senhas em espera (ordem de chamada)')
        quadro.pack(fill='both', expand=True, padx=10, pady=5)
        self.tab_espera = self._criar_tabela(
            quadro,
            [
                ('posicao', 'Ordem', 60),
                ('senha', 'Senha', 110),
                ('categoria', 'Categoria', 130),
                ('emissao', 'Emitida às', 110),
                ('espera', 'Espera estimada', 220),
            ],
        )

        quadro_hist = ttk.LabelFrame(self, text='Histórico de atendimentos')
        quadro_hist.pack(fill='both', expand=True, padx=10, pady=(5, 10))
        self.tab_historico = self._criar_tabela(
            quadro_hist,
            [
                ('senha', 'Senha', 110),
                ('especialidade', 'Especialidade', 180),
                ('categoria', 'Categoria', 130),
                ('emissao', 'Emitida às', 110),
                ('chamada', 'Chamada às', 110),
            ],
        )

    def _criar_tabela(self, pai, colunas):
        tabela = ttk.Treeview(
            pai, columns=[c[0] for c in colunas], show='headings', height=5
        )
        for chave, titulo, largura in colunas:
            tabela.heading(chave, text=titulo)
            tabela.column(chave, width=largura, anchor='center')
        barra = ttk.Scrollbar(pai, orient='vertical', command=tabela.yview)
        tabela.configure(yscrollcommand=barra.set)
        tabela.pack(side='left', fill='both', expand=True)
        barra.pack(side='right', fill='y')
        return tabela

    # ---------- ações dos botões ----------
    def _codigo_especialidade(self):
        # Devolve o código (ex.: 'CG') ou None se nada foi escolhido.
        return NOME_PARA_CODIGO.get(self.var_especialidade.get())

    def _emitir(self):
        try:
            senha = self.gerenciador.emitir_senha(
                self._codigo_especialidade(), self.var_categoria.get()
            )
            espera = self.gerenciador.estimar_espera(senha)
        except ErroClinica as erro:
            messagebox.showwarning('Atenção', str(erro))
            return
        self.var_mensagem.set(
            f'Senha emitida: {senha.codigo}\nEspera estimada: {formatar_espera(espera)}'
        )
        self._atualizar_tela()

    def _chamar(self):
        try:
            self.gerenciador.chamar_proxima(self._codigo_especialidade())
        except ErroClinica as erro:
            messagebox.showwarning('Atenção', str(erro))
            return
        self._atualizar_tela()

    # ---------- atualização da tela ----------
    def _atualizar_tela(self):
        codigo = self._codigo_especialidade()
        self._atualizar_painel(codigo)
        self._atualizar_tabela_espera(codigo)
        self._atualizar_tabela_historico()

    def _atualizar_painel(self, codigo):
        ultima = self.gerenciador.ultima_chamada
        if ultima is None:
            self.lbl_senha.config(text='---')
            self.lbl_detalhes.config(text='Nenhuma senha chamada ainda.')
        else:
            self.lbl_senha.config(text=ultima.codigo)
            self.lbl_detalhes.config(
                text=(
                    f'Especialidade: {ESPECIALIDADES[ultima.especialidade]}'
                    f'  |  Categoria: {CATEGORIAS[ultima.categoria]}'
                )
            )

        total = self.gerenciador.quantidade_aguardando()
        if codigo is None:
            texto = f'Total aguardando na clínica: {total}'
        else:
            pref = self.gerenciador.quantidade_aguardando(codigo, PREFERENCIAL)
            norm = self.gerenciador.quantidade_aguardando(codigo, NORMAL)
            texto = (
                f'Aguardando em {ESPECIALIDADES[codigo]}: {pref + norm} '
                f'(Preferencial: {pref} | Normal: {norm})\n'
                f'Total aguardando na clínica: {total}'
            )
        self.lbl_aguardando.config(text=texto)

    def _atualizar_tabela_espera(self, codigo):
        self.tab_espera.delete(*self.tab_espera.get_children())
        if codigo is None:
            return
        senhas = self.gerenciador.listar_espera(codigo)
        for posicao, senha in enumerate(senhas, start=1):
            espera = self.gerenciador.estimar_espera(senha)
            self.tab_espera.insert(
                '',
                'end',
                values=(
                    posicao,
                    senha.codigo,
                    CATEGORIAS[senha.categoria],
                    formatar_hora(senha.hora_emissao),
                    formatar_espera(espera),
                ),
            )

    def _atualizar_tabela_historico(self):
        self.tab_historico.delete(*self.tab_historico.get_children())
        # Mais recente primeiro.
        for senha in reversed(self.gerenciador.historico):
            self.tab_historico.insert(
                '',
                'end',
                values=(
                    senha.codigo,
                    ESPECIALIDADES[senha.especialidade],
                    CATEGORIAS[senha.categoria],
                    formatar_hora(senha.hora_emissao),
                    formatar_hora(senha.hora_chamada),
                ),
            )