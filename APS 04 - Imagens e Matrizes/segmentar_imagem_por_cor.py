import cv2
import numpy as np


# Troque pelo caminho da imagem fornecida.
CAMINHO_IMAGEM = 'imagem.jpg'


# Escolha a cor que deseja encontrar:
#
# 'vermelho'
# 'verde'
# 'azul'
# 'amarelo'
# 'laranja'
COR = 'vermelho'


# Escolha o exemplo:
#
# 'preto_e_branco'
# 'hsv'
# 'somente_objeto'
# 'todos'
EXEMPLO = 'todos'


class SegmentarImagem:

    # ============================================================
    # SEGMENTAR UMA IMAGEM
    # ============================================================
    #
    # Segmentar significa separar os pixels de interesse
    # dos pixels do fundo.
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - encontrar uma determinada cor;
    # - criar uma máscara;
    # - separar objeto e fundo;
    # - localizar uma faixa de intensidade;
    # - selecionar os pixels de um objeto;
    # - preparar a imagem para contar objetos.
    #
    # A máscara possui:
    #
    # pixel 0:
    # fundo, mostrado em preto.
    #
    # pixel 255:
    # objeto de interesse, mostrado em branco.
    #
    # A principal função será:
    #
    # cv2.inRange(imagem, limite_inferior, limite_superior)

    def __init__(self):

        self.bgr = None
        self.hsv = None
        self.mascara = None
        self.selecao = None

    def carregar_imagem(self, caminho):

        self.bgr = cv2.imread(caminho)

        if self.bgr is None:

            raise FileNotFoundError(
                f'Não foi possível abrir: {caminho}'
            )

        print(f'Imagem carregada: {caminho}')

    # ============================================================
    # SEGMENTAÇÃO EM PRETO E BRANCO
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - encontrar regiões claras ou escuras;
    # - criar uma máscara usando intensidade;
    # - segmentar uma imagem em tons de cinza.
    #
    # Neste exemplo, serão selecionados pixels
    # com intensidade entre 0 e 80.
    #
    # Para encontrar pixels claros, use algo como:
    #
    # cv2.inRange(cinza, 200, 255)

    def segmentar_preto_e_branco(self):

        cinza = cv2.cvtColor(
            self.bgr,
            cv2.COLOR_BGR2GRAY
        )

        # Seleciona pixels escuros.
        limite_inferior = 0
        limite_superior = 80

        mascara = cv2.inRange(
            cinza,
            limite_inferior,
            limite_superior
        )

        print(
            f'Intervalo selecionado: '
            f'{limite_inferior} até {limite_superior}'
        )

        cv2.imshow(
            'Imagem em cinza',
            cinza
        )

        cv2.imshow(
            'Máscara preto e branco',
            mascara
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # ESCOLHER OS LIMITES HSV
    # ============================================================
    #
    # HSV separa:
    #
    # H:
    # cor.
    #
    # S:
    # saturação.
    #
    # V:
    # brilho.
    #
    # No OpenCV:
    #
    # H varia de 0 até 179.
    # S varia de 0 até 255.
    # V varia de 0 até 255.
    #
    # Na prova, os limites podem precisar de ajustes
    # dependendo da iluminação e da imagem.

    def obter_limites_hsv(self, cor):

        limites = {
            'verde': (
                np.array([35, 50, 50]),
                np.array([85, 255, 255])
            ),

            'azul': (
                np.array([90, 50, 50]),
                np.array([130, 255, 255])
            ),

            'amarelo': (
                np.array([20, 100, 100]),
                np.array([35, 255, 255])
            ),

            'laranja': (
                np.array([5, 100, 100]),
                np.array([20, 255, 255])
            )
        }

        if cor not in limites:

            raise ValueError(
                f'Não existem limites simples para: {cor}'
            )

        return limites[cor]

    # ============================================================
    # CRIAR MÁSCARA HSV
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - detectar uma cor;
    # - criar uma máscara colorida;
    # - encontrar pixels dentro de um intervalo HSV.
    #
    # O vermelho precisa de dois intervalos porque
    # fica dividido entre o começo e o final do canal H.

    def criar_mascara_hsv(self):

        # Converte BGR para HSV.
        self.hsv = cv2.cvtColor(
            self.bgr,
            cv2.COLOR_BGR2HSV
        )

        if COR == 'vermelho':

            # Primeiro intervalo do vermelho.
            limite_baixo_1 = np.array(
                [0, 100, 100]
            )

            limite_alto_1 = np.array(
                [10, 255, 255]
            )

            # Segundo intervalo do vermelho.
            limite_baixo_2 = np.array(
                [170, 100, 100]
            )

            limite_alto_2 = np.array(
                [179, 255, 255]
            )

            mascara_1 = cv2.inRange(
                self.hsv,
                limite_baixo_1,
                limite_alto_1
            )

            mascara_2 = cv2.inRange(
                self.hsv,
                limite_baixo_2,
                limite_alto_2
            )

            # Junta os dois intervalos.
            self.mascara = cv2.bitwise_or(
                mascara_1,
                mascara_2
            )

        else:

            limite_baixo, limite_alto = (
                self.obter_limites_hsv(COR)
            )

            self.mascara = cv2.inRange(
                self.hsv,
                limite_baixo,
                limite_alto
            )

        return self.mascara

    # ============================================================
    # MOSTRAR A MÁSCARA
    # ============================================================

    def mostrar_mascara(self):

        self.criar_mascara_hsv()

        # Conta os pixels brancos.
        quantidade_pixels = cv2.countNonZero(
            self.mascara
        )

        total_pixels = (
            self.mascara.shape[0]
            * self.mascara.shape[1]
        )

        porcentagem = (
            quantidade_pixels
            / total_pixels
            * 100
        )

        print(
            f'Pixels da cor {COR}: '
            f'{quantidade_pixels}'
        )

        print(
            f'Porcentagem da imagem: '
            f'{porcentagem:.2f}%'
        )

        cv2.imshow(
            'Imagem original',
            self.bgr
        )

        cv2.imshow(
            f'Máscara da cor {COR}',
            self.mascara
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # MOSTRAR SOMENTE O OBJETO SEGMENTADO
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - aplicar a máscara na imagem;
    # - apagar o fundo;
    # - mostrar apenas o objeto encontrado.
    #
    # bitwise_and mantém os pixels brancos da máscara
    # e deixa o restante preto.

    def mostrar_somente_objeto(self):

        self.criar_mascara_hsv()

        self.selecao = cv2.bitwise_and(
            self.bgr,
            self.bgr,
            mask=self.mascara
        )

        cv2.imshow(
            'Imagem original',
            self.bgr
        )

        cv2.imshow(
            'Máscara',
            self.mascara
        )

        cv2.imshow(
            f'Somente {COR}',
            self.selecao
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # MOSTRAR TODOS OS RESULTADOS
    # ============================================================

    def mostrar_todos(self):

        self.criar_mascara_hsv()

        self.selecao = cv2.bitwise_and(
            self.bgr,
            self.bgr,
            mask=self.mascara
        )

        quantidade_pixels = cv2.countNonZero(
            self.mascara
        )

        total_pixels = self.mascara.size

        porcentagem = (
            quantidade_pixels
            / total_pixels
            * 100
        )

        print(f'Cor procurada: {COR}')

        print(
            f'Pixels encontrados: {quantidade_pixels}'
        )

        print(
            f'Área ocupada na imagem: '
            f'{porcentagem:.2f}%'
        )

        cv2.imshow(
            'Imagem original',
            self.bgr
        )

        cv2.imshow(
            'Imagem HSV',
            self.hsv
        )

        cv2.imshow(
            'Máscara',
            self.mascara
        )

        cv2.imshow(
            'Objeto segmentado',
            self.selecao
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():

    processador = SegmentarImagem()

    processador.carregar_imagem(
        CAMINHO_IMAGEM
    )

    exemplos = {
        'preto_e_branco':
            processador.segmentar_preto_e_branco,

        'hsv':
            processador.mostrar_mascara,

        'somente_objeto':
            processador.mostrar_somente_objeto,

        'todos':
            processador.mostrar_todos
    }

    if EXEMPLO not in exemplos:

        raise ValueError(
            f'Exemplo inválido: {EXEMPLO}'
        )

    exemplos[EXEMPLO]()


if __name__ == '__main__':
    main()