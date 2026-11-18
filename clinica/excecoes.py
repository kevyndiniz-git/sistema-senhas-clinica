# Exceções (erros) próprias do sistema.

class ErroClinica (Exception):
    #Classe base: todos os erros do sistema herdam dela.
    pass

class FilaVaziaError(ErroClinica):
    #Tentativa de retirar ou consultar um elemento de uma fila vazia.
    pass

class SemPacientesError(ErroClinica):
    #Não há pacientes aguardando na especialidade escoliha.
    pass

class EntradaInvalidaError (ErroClinica):
    #O Usuario não informou ou informou errado um dado (ex:especialidade).
    pass

class OperacaoInvalidaError(ErroClinica):
    #Operação incompatível com o estado atual (ex: passou do limite de senhas).
    pass