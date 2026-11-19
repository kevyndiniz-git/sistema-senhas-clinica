from clinica.excecoes import EntradaInvalidaError, FilaVaziaError

class No:
    def __init__(self,valor):
        self.valor = valor
        self.proximo = None

class FilaFIFO:
    #Fila First In, First Out implantada com lista encadeada.

    def __init__(self):
        self._inicio = None #Primeiro da fila (proximo a sair)
        self._fim = None
        self._tamanho = 0 

    def __len__(self):
        return self._tamanho

    def esta_vazia(self):
        return self._tamanho == 0

    def enfileirar (self, valor):
        #Coloca um valor no final da fila.
        novo = No(valor)
        if self._fim is None:
            self._inicio = novo 
        else: 
            self._fim.proximo = novo
        self._fim = novo
        self._tamanho += 1

    def desenfileirar(self):
        #Remove e devolve o valor que está no inicio da fila.
        if self.esta_vazia():
            raise FilaVaziaError('A fila está vazia.')
        removido = self._inicio
        self._inicio = removido.proximo
        if self._inicio is None:
            self._fim = None
        self._tamanho -= 1
        return removido.valor

    def primeiro(self):
        #Devolve o inicio da fila sem removê-lo.
        if self.esta_vazia():
            raise FilaVaziaError('A fila está vazia.')
        return self._inicio.valor

    def listar(self):
        #Devolve uma lista Python com os valores, do inicio ao fim.
        itens = []
        atual = self._inicio
        while atual is not None:
            itens.append(atual.valor)
            atual = atual.proximo
        return itens

class FilaPrioridade:
    # Conjunto de filas FIFO, uma por categoria, em ordem de prioridade.
    # A categoria que aparece primeiro na lista tem a maior prioridade.

    def __init__(self, categorias_em_ordem):
        self._ordem = list(categorias_em_ordem)
        self._filas = {categoria: FilaFIFO() for categoria in self._ordem}

    def _fila_da(self, categoria):
        if categoria not in self._filas:
            raise EntradaInvalidaError(f'Categoria desconhecida: {categoria}')
        return self._filas[categoria]

    def enfileirar(self, categoria, valor):
        self._fila_da(categoria).enfileirar(valor)

    def desenfileirar(self):
        # Retira da fila de maior prioridade que não esteja vazia.
        for categoria in self._ordem:
            fila = self._filas[categoria]
            if not fila.esta_vazia():
                return fila.desenfileirar()
        raise FilaVaziaError('Não há ninguém aguardando.')

    def esta_vazia(self):
        return self.tamanho() == 0

    def tamanho(self, categoria=None):
        if categoria is None:
            return sum(len(fila) for fila in self._filas.values())
        return len(self._fila_da(categoria))

    def listar(self):
        # Ordem real de chamada: primeiro toda a categoria prioritária, depois as demais.
        itens = []
        for categoria in self._ordem:
            itens.extend(self._filas[categoria].listar())
        return itens