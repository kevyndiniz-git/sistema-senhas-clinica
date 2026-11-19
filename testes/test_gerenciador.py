import unittest

from clinica.excecoes import (EntradaInvalidaError, FilaVaziaError, OperacaoInvalidaError, SemPacientesError)
from clinica.fila import FilaFIFO
from clinica.gerenciador import GerenciadorSenhas


class TesteFilaFIFO(unittest.TestCase):
    def test_ordem_fifo(self):
        fila = FilaFIFO()
        for valor in ['a', 'b', 'c']:
            fila.enfileirar(valor)
        self.assertEqual(fila.desenfileirar(), 'a')
        self.assertEqual(fila.desenfileirar(), 'b')
        self.assertEqual(len(fila), 1)

    def test_desenfileirar_fila_vazia(self):
        with self.assertRaises(FilaVaziaError):
            FilaFIFO().desenfileirar()


class TesteGerenciador(unittest.TestCase):
    def setUp(self):
        self.g = GerenciadorSenhas()

    def test_numeracao_por_especialidade_e_categoria(self):
        self.assertEqual(self.g.emitir_senha('CG', 'N').codigo, 'CG-N001')
        self.assertEqual(self.g.emitir_senha('CG', 'N').codigo, 'CG-N002')
        self.assertEqual(self.g.emitir_senha('CG', 'P').codigo, 'CG-P001')
        self.assertEqual(self.g.emitir_senha('CA', 'N').codigo, 'CA-N001')

    def test_preferencial_chamado_antes_do_normal(self):
        self.g.emitir_senha('CG', 'N')
        self.g.emitir_senha('CG', 'N')
        self.g.emitir_senha('CG', 'P')
        ordem = [self.g.chamar_proxima('CG').codigo for _ in range(3)]
        self.assertEqual(ordem, ['CG-P001', 'CG-N001', 'CG-N002'])

    def test_fifo_dentro_de_cada_categoria(self):
        self.g.emitir_senha('OR', 'P')
        self.g.emitir_senha('OR', 'P')
        self.assertEqual(self.g.chamar_proxima('OR').codigo, 'OR-P001')
        self.assertEqual(self.g.chamar_proxima('OR').codigo, 'OR-P002')

    def test_filas_independentes_entre_especialidades(self):
        self.g.emitir_senha('CG', 'N')
        self.g.emitir_senha('CA', 'N')
        self.g.chamar_proxima('CG')
        self.assertEqual(self.g.quantidade_aguardando('CG'), 0)
        self.assertEqual(self.g.quantidade_aguardando('CA'), 1)

    def test_chamada_remove_da_fila_e_registra_historico(self):
        self.g.emitir_senha('CA', 'N')
        senha = self.g.chamar_proxima('CA')
        self.assertEqual(self.g.quantidade_aguardando(), 0)
        self.assertEqual(self.g.historico, [senha])
        self.assertEqual(self.g.ultima_chamada, senha)
        self.assertIsNotNone(senha.hora_chamada)

    def test_chamar_sem_pacientes(self):
        with self.assertRaises(SemPacientesError):
            self.g.chamar_proxima('CG')

    def test_entradas_invalidas(self):
        with self.assertRaises(EntradaInvalidaError):
            self.g.emitir_senha('XX', 'N')
        with self.assertRaises(EntradaInvalidaError):
            self.g.emitir_senha('CG', 'Z')
        with self.assertRaises(EntradaInvalidaError):
            self.g.emitir_senha('', '')

    def test_estimativa_de_espera(self):
        n1 = self.g.emitir_senha('CG', 'N')
        n2 = self.g.emitir_senha('CG', 'N')
        p1 = self.g.emitir_senha('CG', 'P')
        self.assertEqual(self.g.estimar_espera(p1), 0)
        self.assertEqual(self.g.estimar_espera(n1), 30)
        self.assertEqual(self.g.estimar_espera(n2), 60)
        self.g.chamar_proxima('CG')
        self.assertEqual(self.g.estimar_espera(n1), 0)

    def test_estimar_senha_ja_chamada(self):
        senha = self.g.emitir_senha('CG', 'N')
        self.g.chamar_proxima('CG')
        with self.assertRaises(OperacaoInvalidaError):
            self.g.estimar_espera(senha)

    def test_limite_de_numeracao(self):
        for _ in range(999):
            self.g.emitir_senha('CG', 'N')
        with self.assertRaises(OperacaoInvalidaError):
            self.g.emitir_senha('CG', 'N')


if __name__ == '__main__':
    unittest.main()