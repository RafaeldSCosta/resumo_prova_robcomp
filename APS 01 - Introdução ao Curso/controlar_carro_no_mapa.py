"""
CLASSES E CÓDIGO FORNECIDO PELO PROFESSOR

Este arquivo possui dois casos:

CASO 1:
O professor pede uma classe do zero.
Use uma classe normal e NÃO use super().__init__().

CASO 2:
O professor entrega uma classe pronta, como Mapa,
e pede que sua classe aproveite essa estrutura.
Nesse caso, use class Control(Mapa) e super().__init__().

IMPORTANTE:
Não copie tudo sem olhar o enunciado.
Escolha o caso que corresponde à questão.
"""


# ============================================================
# CASO 1 — O PROFESSOR PEDIU UMA CLASSE DO ZERO
# ============================================================

"""
USE ESTE MODELO QUANDO O ENUNCIADO DISSER:

- "Crie uma classe chamada..."
- "A classe deve possuir os atributos..."
- "Implemente os métodos..."
- E NÃO mencionar nenhuma classe pronta para utilizar.

Neste caso, NÃO precisa de super().__init__(),
porque não existe outra classe que precisa ser iniciada.
"""


class Robo:
    # ALTERE Robo para o nome pedido no enunciado.

    def __init__(self):
        """
        O __init__ executa quando fazemos:

            robo = Robo()

        Coloque aqui todas as informações iniciais que serão
        usadas por mais de uma função.
        """

        # Se ele pedir um estado inicial:
        self.estado = 'parado'

        # Se ele pedir velocidade inicial:
        self.velocidade = 0.0

        # Se ele pedir controlar quando terminou:
        self.finalizado = False

        # Se ele pedir alguma informação de sensor:
        self.obstaculo = False

    def andar(self):
        """
        Use se ele pedir uma ação para andar.

        Troque os valores e a lógica pelo que estiver
        escrito no enunciado.
        """

        self.estado = 'andando'
        self.velocidade = 0.2

    def parar(self):
        """
        Use se ele pedir uma ação para parar.
        """

        self.estado = 'parado'
        self.velocidade = 0.0

    def control(self):
        """
        Use o control para escolher qual ação executar.
        """

        # Se ele pedir para parar quando encontrar um obstáculo:
        if self.obstaculo:
            self.parar()

        # Se ele pedir para andar quando não houver obstáculo:
        else:
            self.andar()


# Exemplo de utilização:
#
# robo = Robo()
# robo.control()
#
# robo.obstaculo = True
# robo.control()


# ============================================================
# QUANDO USAR super().__init__()?
# ============================================================

"""
USE super().__init__() QUANDO:

1. Sua classe estiver utilizando outra classe.

   Exemplo:
       class Control(Mapa):

2. A classe fornecida possuir informações que você precisa.

   Exemplo:
       - mapa;
       - posição do carro;
       - tamanho do mapa;
       - obstáculos;
       - métodos prontos.

3. Sua classe for um nó da ROS 2.

   Exemplo:
       class MeuNo(Node):

NÃO USE super().__init__() QUANDO:

1. A classe foi criada do zero.

   Exemplo:
       class Robo:

2. Não existe uma classe dentro dos parênteses.

   Neste caso:
       class Robo:

   Não usamos:
       super().__init__()

RESUMO:

    class Robo:
        Não precisa de super.

    class Control(Mapa):
        Normalmente precisa de super.

    class MeuNo(Node):
        Precisa de super para iniciar o nó.
"""


# ============================================================
# CASO 2 — O PROFESSOR ENTREGOU UMA CLASSE PRONTA
# ============================================================

"""
USE ESTE MODELO QUANDO O ENUNCIADO DISSER:

- "A classe Control deve herdar de Mapa."
- "Utilize a classe Mapa fornecida."
- "Baseando-se na classe Mapa..."
- "Não altere o arquivo util.py."

ANTES DE PROGRAMAR:

1. Abra o arquivo fornecido pelo professor.
2. Procure:

       class Mapa:

3. Veja o que existe dentro do __init__.
4. Anote os nomes das informações criadas com self.
5. Procure as funções prontas, por exemplo:

       def atualizar_posicao(...):

6. Veja exatamente o que cada função recebe.
"""


# Na questão real, descomente e ajuste o import:
#
# from util import Mapa


# ============================================================
# EXEMPLO DA CLASSE FORNECIDA
# ============================================================

"""
A classe abaixo é apenas um exemplo para explicar.

Na questão real, esta parte já estará no arquivo do professor.
Você NÃO deve recriá-la se ela já foi fornecida.
"""


class Mapa:

    def __init__(self):
        # Exemplo de mapa:
        # 0 = espaço livre
        # 1 = carro
        # 2 = obstáculo

        self.mapa = [
            [0, 0, 0, 0, 0],
            [0, 0, 2, 0, 0],
            [0, 0, 2, 0, 0],
            [0, 0, 1, 0, 0],
        ]

        # Posição no formato:
        # [linha, coluna]
        self.posicao = [3, 2]

    def atualizar_posicao(self, acao, nova_posicao):
        """
        EXEMPLO de função fornecida pelo professor.

        Neste exemplo, ela recebe:

        acao:
            Nome do movimento realizado.
            Exemplo: 'forward', 'left' ou 'right'.

        nova_posicao:
            Lista contendo [nova_linha, nova_coluna].

        Na questão real, confira a função fornecida.
        Os parâmetros podem ter outros nomes ou outra ordem.
        """

        linha_atual = self.posicao[0]
        coluna_atual = self.posicao[1]

        nova_linha = nova_posicao[0]
        nova_coluna = nova_posicao[1]

        # Remover o carro da posição antiga
        self.mapa[linha_atual][coluna_atual] = 0

        # Guardar a nova posição
        self.posicao = nova_posicao

        # Colocar o carro na nova posição
        self.mapa[nova_linha][nova_coluna] = 1

        print(f'Ação: {acao}')
        print(f'Nova posição: {nova_posicao}')


# ============================================================
# SUA CLASSE UTILIZANDO O QUE O PROFESSOR FORNECEU
# ============================================================

class Control(Mapa):
    """
    Control utiliza tudo que já existe dentro de Mapa.

    Se o enunciado pedir outro nome, troque Control.
    """

    def __init__(self):
        """
        O super executa o __init__ de Mapa.

        Neste exemplo, ele cria:

            self.mapa
            self.posicao

        Sem o super, essas informações não seriam iniciadas.
        """

        super().__init__()

        # Se ele pedir um estado inicial:
        self.robot_state = 'forward'

        # Se ele pedir controlar quando o programa terminou:
        self.finalizado = False

        # Se ele pedir máquina de estados:
        self.state_machine = {
            'forward': self.forward,
            'left': self.left,
            'right': self.right,
            'stop': self.stop,
        }

    # ========================================================
    # VERIFICAR O QUE EXISTE AO REDOR DO CARRO
    # ========================================================

    def frente_livre(self):
        """
        Use se ele pedir para verificar a posição acima.

        Retorna:
            True  -> posição livre;
            False -> obstáculo ou fim do mapa.
        """

        linha = self.posicao[0]
        coluna = self.posicao[1]

        # Se já chegou na primeira linha, não existe linha acima
        if linha == 0:
            return False

        # linha - 1 representa a posição acima
        valor_na_frente = self.mapa[linha - 1][coluna]

        # Neste exemplo, 0 significa espaço livre
        return valor_na_frente == 0

    def esquerda_livre(self):
        """
        Use se ele pedir para verificar o lado esquerdo.
        """

        linha = self.posicao[0]
        coluna = self.posicao[1]

        # Se coluna for 0, o carro já está no limite esquerdo
        if coluna == 0:
            return False

        valor_na_esquerda = self.mapa[linha][coluna - 1]

        return valor_na_esquerda == 0

    def direita_livre(self):
        """
        Use se ele pedir para verificar o lado direito.
        """

        linha = self.posicao[0]
        coluna = self.posicao[1]

        quantidade_de_colunas = len(self.mapa[0])

        # Última coluna:
        # quantidade_de_colunas - 1
        if coluna == quantidade_de_colunas - 1:
            return False

        valor_na_direita = self.mapa[linha][coluna + 1]

        return valor_na_direita == 0

    # ========================================================
    # AÇÕES
    # ========================================================

    def forward(self):
        """
        Use se ele pedir para mover o carro para frente.

        Como o objetivo está na parte de cima do mapa,
        andar para frente significa diminuir a linha.
        """

        linha = self.posicao[0]
        coluna = self.posicao[1]

        nova_posicao = [
            linha - 1,
            coluna
        ]

        # A função atualizar_posicao já veio de Mapa.
        # Por isso, apenas chamamos a função.
        self.atualizar_posicao(
            'forward',
            nova_posicao
        )

    def left(self):
        """
        Use se ele pedir para mover o carro para a esquerda.

        Ir para esquerda significa diminuir a coluna.
        """

        linha = self.posicao[0]
        coluna = self.posicao[1]

        nova_posicao = [
            linha,
            coluna - 1
        ]

        self.atualizar_posicao(
            'left',
            nova_posicao
        )

    def right(self):
        """
        Use se ele pedir para mover o carro para a direita.

        Ir para direita significa aumentar a coluna.
        """

        linha = self.posicao[0]
        coluna = self.posicao[1]

        nova_posicao = [
            linha,
            coluna + 1
        ]

        self.atualizar_posicao(
            'right',
            nova_posicao
        )

    def stop(self):
        """
        Use se ele pedir para finalizar o programa.
        """

        self.finalizado = True

        print('O carro parou.')

    # ========================================================
    # ESCOLHER A PRÓXIMA AÇÃO
    # ========================================================

    def control(self):
        """
        O mapa NÃO precisa ser colocado como parâmetro.

        Certo:
            def control(self):

        O mapa já está disponível como:
            self.mapa

        Isso acontece porque usamos:
            super().__init__()
        """

        linha = self.posicao[0]

        # ----------------------------------------------------
        # SE ELE PEDIR PARA PARAR NA PRIMEIRA LINHA
        # ----------------------------------------------------

        if linha == 0:
            self.robot_state = 'stop'

        # ----------------------------------------------------
        # SE ELE PEDIR PARA SEGUIR QUANDO A FRENTE ESTIVER LIVRE
        # ----------------------------------------------------

        elif self.frente_livre():
            self.robot_state = 'forward'

        # ----------------------------------------------------
        # SE ELE PEDIR PARA TENTAR A ESQUERDA
        # ----------------------------------------------------

        elif self.esquerda_livre():
            self.robot_state = 'left'

        # ----------------------------------------------------
        # SE ELE PEDIR PARA TENTAR A DIREITA
        # ----------------------------------------------------

        elif self.direita_livre():
            self.robot_state = 'right'

        # ----------------------------------------------------
        # SE ELE PEDIR PARA PARAR QUANDO NÃO HOUVER SAÍDA
        # ----------------------------------------------------

        else:
            self.robot_state = 'stop'

        # ----------------------------------------------------
        # SE ELE PEDIR PARA EXECUTAR A AÇÃO PELO DICIONÁRIO
        # ----------------------------------------------------

        self.state_machine[self.robot_state]()


# ============================================================
# QUANDO CRIAR OU NÃO CRIAR atualizar_posicao?
# ============================================================

"""
SE O PROFESSOR JÁ FORNECEU:

    def atualizar_posicao(...):

NÃO crie novamente.

Apenas chame:

    self.atualizar_posicao(acao, nova_posicao)


SE O PROFESSOR PEDIR PARA VOCÊ IMPLEMENTAR:

Confira quais valores a função deve receber.

O formato pode ser:

    def atualizar_posicao(self, acao, nova_posicao):

Nesse exemplo:

    acao:
        String com o nome do movimento.

    nova_posicao:
        Lista [linha, coluna].


COMO DESCOBRIR O QUE UMA FUNÇÃO RECEBE?

Abra o arquivo fornecido e procure a definição:

    def atualizar_posicao(self, acao, nova_posicao):

Tudo que aparece depois de self precisa ser enviado quando
você chama a função:

    self.atualizar_posicao('forward', [linha - 1, coluna])
"""


# ============================================================
# TESTE DO EXEMPLO
# ============================================================

def main():
    controle = Control()

    # Executar alguns passos sem usar um loop infinito
    for passo in range(20):
        if controle.finalizado:
            break

        print(f'\nPasso: {passo + 1}')
        print(f'Posição atual: {controle.posicao}')

        controle.control()


if __name__ == '__main__':
    main()