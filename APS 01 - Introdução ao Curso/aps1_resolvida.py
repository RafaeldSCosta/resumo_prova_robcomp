"""
APS 1 — RESOLUÇÃO DO EXERCÍCIO DO MAPA

Mapa:
- 0 = posição livre;
- 1 = posição atual do carro;
- 2 = obstáculo.

Objetivo:
- chegar à primeira linha;
- andar para frente quando estiver livre;
- desviar para esquerda ou direita quando houver obstáculo;
- nunca ultrapassar as laterais;
- entrar no estado stop ao chegar ao objetivo.
"""

import numpy as np

# Classe fornecida pelo professor no arquivo util.py
from util import Mapa


class Control(Mapa):

    def __init__(self):
        # Inicia o mapa e tudo que foi criado pelo professor
        super().__init__()

        # Estado inicial do carro
        self.robot_state = 'forward'

        # Relaciona cada estado à sua ação
        self.state_machine = {
            'forward': self.forward,
            'left': self.left,
            'right': self.right,
            'stop': self.stop,
        }

    def encontrar_carro(self):
        """
        Procura no mapa o valor 1.

        Retorna:
            linha, coluna
        """

        # Funciona se self.mapa for lista ou array NumPy
        mapa = np.asarray(self.mapa)

        posicoes = np.argwhere(mapa == 1)

        # A primeira posição encontrada contém [linha, coluna]
        linha = int(posicoes[0][0])
        coluna = int(posicoes[0][1])

        return linha, coluna

    def forward(self):
        """Move o carro uma linha para cima."""

        linha, coluna = self.encontrar_carro()

        # Para subir no mapa, diminuímos a linha
        nova_posicao = [
            linha - 1,
            coluna
        ]

        # Função fornecida pela classe Mapa
        self.atualizar_posicao(
            'forward',
            nova_posicao
        )

    def left(self):
        """Move o carro uma coluna para a esquerda."""

        linha, coluna = self.encontrar_carro()

        # Para ir à esquerda, diminuímos a coluna
        nova_posicao = [
            linha,
            coluna - 1
        ]

        self.atualizar_posicao(
            'left',
            nova_posicao
        )

    def right(self):
        """Move o carro uma coluna para a direita."""

        linha, coluna = self.encontrar_carro()

        # Para ir à direita, aumentamos a coluna
        nova_posicao = [
            linha,
            coluna + 1
        ]

        self.atualizar_posicao(
            'right',
            nova_posicao
        )

    def stop(self):
        """Mantém o carro parado ao chegar ao objetivo."""

        print('O carro chegou ao objetivo.')

    def control(self):
        """
        Escolhe a próxima ação e executa pelo dicionário.

        Prioridade:
        1. Se chegou à primeira linha, parar.
        2. Se a frente está livre, seguir.
        3. Se a esquerda está livre, ir para esquerda.
        4. Se a direita está livre, ir para direita.
        5. Se não existe saída, parar.
        """

        linha, coluna = self.encontrar_carro()

        quantidade_de_colunas = len(self.mapa[0])

        # Chegou à primeira linha
        if linha == 0:
            self.robot_state = 'stop'

        # A posição acima está livre
        elif self.mapa[linha - 1][coluna] == 0:
            self.robot_state = 'forward'

        # Existe obstáculo à frente e a esquerda está livre
        elif (
            coluna > 0
            and self.mapa[linha][coluna - 1] == 0
        ):
            self.robot_state = 'left'

        # Frente e esquerda bloqueadas, mas a direita está livre
        elif (
            coluna < quantidade_de_colunas - 1
            and self.mapa[linha][coluna + 1] == 0
        ):
            self.robot_state = 'right'

        # Não existe movimento possível
        else:
            self.robot_state = 'stop'

        print(f'Estado atual: {self.robot_state}')

        # Executar a ação correspondente ao estado escolhido
        self.state_machine[self.robot_state]()


def main():
    # Criar o controle e iniciar o mapa
    controle = Control()

    # Executar até chegar ao estado stop
    while controle.robot_state != 'stop':
        controle.control()

    # Executar stop uma última vez
    controle.control()


if __name__ == '__main__':
    main()