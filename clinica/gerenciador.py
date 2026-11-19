from datetime import datetime

from clinica.constantes import (
    CATEGORIAS,
    ESPECIALIDADES,
    LIMITE_NUMERACAO,
    NORMAL,
    PREFERENCIAL,
    TEMPO_MEDIO_ATENDIMENTO,
)
from clinica.excecoes import (
    EntradaInvalidaError,
    OperacaoInvalidaError,
    SemPacientesError,
)
from clinica.fila import FilaPrioridade
from clinica.senha import Senha


class GerenciadorSenhas:
    # Controla emissão, chamada e consulta de senhas de toda a clínica.

    def __init__(self):
        # Uma fila de prioridade por especialidade: P é atendida antes de N.
        self._filas = {
            codigo: FilaPrioridade([PREFERENCIAL, NORMAL])
            for codigo in ESPECIALIDADES
        }
        # Último número emitido para cada par (especialidade, categoria).
        self._contadores = {
            (esp, cat): 0 for esp in ESPECIALIDADES for cat in CATEGORIAS
        }
        self._historico = []
        self._ultima_chamada = None

    # ---------- validações ----------
    def _validar_especialidade(self, especialidade):
        if especialidade not in ESPECIALIDADES:
            raise EntradaInvalidaError('Selecione uma especialidade válida.')

    def _validar_categoria(self, categoria):
        if categoria not in CATEGORIAS:
            raise EntradaInvalidaError(
                'Selecione a categoria de atendimento: Normal ou Preferencial.'
            )

    # ---------- operações principais ----------
    def emitir_senha(self, especialidade, categoria):
        # Cria uma nova senha e a coloca no final da fila da sua categoria.
        self._validar_especialidade(especialidade)
        self._validar_categoria(categoria)

        chave = (especialidade, categoria)
        if self._contadores[chave] >= LIMITE_NUMERACAO:
            raise OperacaoInvalidaError(
                'Limite de senhas atingido para esta especialidade e categoria.'
            )

        self._contadores[chave] += 1
        senha = Senha(especialidade, categoria, self._contadores[chave])
        self._filas[especialidade].enfileirar(categoria, senha)
        return senha

    def chamar_proxima(self, especialidade):
        # Chama a próxima senha da especialidade, respeitando a prioridade.
        self._validar_especialidade(especialidade)
        fila = self._filas[especialidade]
        if fila.esta_vazia():
            nome = ESPECIALIDADES[especialidade]
            raise SemPacientesError(f'Não há pacientes aguardando em {nome}.')

        senha = fila.desenfileirar()
        senha.hora_chamada = datetime.now()
        self._historico.append(senha)
        self._ultima_chamada = senha
        return senha

    # ---------- consultas ----------
    def listar_espera(self, especialidade):
        # Senhas aguardando, na ordem em que serão chamadas.
        self._validar_especialidade(especialidade)
        return self._filas[especialidade].listar()

    def quantidade_aguardando(self, especialidade=None, categoria=None):
        # Sem argumentos: total da clínica. Com especialidade: total dela.
        # Com especialidade e categoria: total daquela fila.
        if especialidade is None:
            return sum(fila.tamanho() for fila in self._filas.values())
        self._validar_especialidade(especialidade)
        return self._filas[especialidade].tamanho(categoria)

    def estimar_espera(self, senha):
        # Minutos = pacientes à frente na ordem de chamada x tempo médio.
        fila_ordenada = self.listar_espera(senha.especialidade)
        for posicao, item in enumerate(fila_ordenada):
            if item.codigo == senha.codigo:
                return posicao * TEMPO_MEDIO_ATENDIMENTO
        raise OperacaoInvalidaError(
            f'A senha {senha.codigo} não está mais na fila de espera.'
        )

    @property
    def historico(self):
        return list(self._historico)

    @property
    def ultima_chamada(self):
        return self._ultima_chamada