import cv2
import numpy as np


CAMINHO_IMAGEM = 'imagem.jpg'


# Cor usada para criar a máscara inicial.
#
# Opções:
# 'vermelho'
# 'verde'
# 'azul'
# 'amarelo'
# 'violeta'
COR = 'vermelho'


# Operação que será mostrada:
#
# 'erosao'
# 'dilatacao'
# 'abertura'
# 'fechamento'
# 'refinar'
# 'todas'
OPERACAO = 'todas'


# Tamanho do kernel.
#
# Valores comuns:
#
# 3
# 5
# 7
#
# Quanto maior, mais forte será a alteração.
TAMANHO_KERNEL = 5


class MelhorarMascara:

    # ============================================================
    # MELHORAR UMA MÁSCARA
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - remover ruídos de uma máscara;
    # - apagar pequenas manchas brancas;
    # - preencher pequenos buracos pretos;
    # - melhorar uma segmentação;
    # - aplicar erosão ou dilatação;
    # - aplicar abertura ou fechamento.
    #
    # EROSÃO:
    #
    # Encolhe as regiões brancas.
    # É útil para remover pequenas manchas brancas.
    #
    # DILATAÇÃO:
    #
    # Aumenta as regiões brancas.
    # É útil para preencher pequenos espaços.
    #
    # ABERTURA:
    #
    # Primeiro faz erosão e depois dilatação.
    # É boa para remover ilhas brancas.
    #
    # FECHAMENTO:
    #
    # Primeiro faz dilatação e depois erosão.
    # É bom para preencher buracos pretos.
    #
    # REFINAMENTO:
    #
    # Normalmente usamos abertura e depois fechamento.

    def __init__(self):

        self.bgr = None
        self.hsv = None
        self.mascara_original = None
        self.kernel = None

    def carregar_imagem(self, caminho):

        self.bgr = cv2.imread(caminho)

        if self.bgr is None:

            raise FileNotFoundError(
                f'Não foi possível abrir: {caminho}'
            )

        self.hsv = cv2.cvtColor(
            self.bgr,
            cv2.COLOR_BGR2HSV
        )

    def criar_mascara(self):

        # O vermelho precisa de dois intervalos.
        if COR == 'vermelho':

            mascara_1 = cv2.inRange(
                self.hsv,
                np.array([0, 100, 100]),
                np.array([10, 255, 255])
            )

            mascara_2 = cv2.inRange(
                self.hsv,
                np.array([170, 100, 100]),
                np.array([179, 255, 255])
            )

            self.mascara_original = cv2.bitwise_or(
                mascara_1,
                mascara_2
            )

        else:

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

                'violeta': (
                    np.array([130, 50, 50]),
                    np.array([150, 255, 255])
                )
            }

            if COR not in limites:

                raise ValueError(
                    f'Cor inválida: {COR}'
                )

            limite_inferior, limite_superior = limites[COR]

            self.mascara_original = cv2.inRange(
                self.hsv,
                limite_inferior,
                limite_superior
            )

        return self.mascara_original

    def criar_kernel(self):

        # MORPH_ELLIPSE cria um kernel arredondado.
        #
        # Outras opções:
        #
        # cv2.MORPH_RECT
        # cv2.MORPH_CROSS
        self.kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (TAMANHO_KERNEL, TAMANHO_KERNEL)
        )

    def aplicar_erosao(self):

        # Remove pequenas regiões brancas.
        return cv2.morphologyEx(
            self.mascara_original,
            cv2.MORPH_ERODE,
            self.kernel
        )

    def aplicar_dilatacao(self):

        # Expande as regiões brancas.
        return cv2.morphologyEx(
            self.mascara_original,
            cv2.MORPH_DILATE,
            self.kernel
        )

    def aplicar_abertura(self):

        # Remove pequenas ilhas brancas.
        return cv2.morphologyEx(
            self.mascara_original,
            cv2.MORPH_OPEN,
            self.kernel
        )

    def aplicar_fechamento(self):

        # Preenche pequenos buracos pretos.
        return cv2.morphologyEx(
            self.mascara_original,
            cv2.MORPH_CLOSE,
            self.kernel
        )

    def refinar_mascara(self):

        # Primeiro remove as pequenas manchas.
        refinada = cv2.morphologyEx(
            self.mascara_original,
            cv2.MORPH_OPEN,
            self.kernel
        )

        # Depois preenche pequenos buracos.
        refinada = cv2.morphologyEx(
            refinada,
            cv2.MORPH_CLOSE,
            self.kernel
        )

        return refinada

    def executar(self):

        self.criar_mascara()
        self.criar_kernel()

        operacoes = {
            'erosao': self.aplicar_erosao,
            'dilatacao': self.aplicar_dilatacao,
            'abertura': self.aplicar_abertura,
            'fechamento': self.aplicar_fechamento,
            'refinar': self.refinar_mascara
        }

        if OPERACAO == 'todas':

            erosao = self.aplicar_erosao()
            dilatacao = self.aplicar_dilatacao()
            abertura = self.aplicar_abertura()
            fechamento = self.aplicar_fechamento()
            refinada = self.refinar_mascara()

            cv2.imshow(
                'Imagem original',
                self.bgr
            )

            cv2.imshow(
                'Máscara original',
                self.mascara_original
            )

            cv2.imshow(
                'Erosão',
                erosao
            )

            cv2.imshow(
                'Dilatação',
                dilatacao
            )

            cv2.imshow(
                'Abertura',
                abertura
            )

            cv2.imshow(
                'Fechamento',
                fechamento
            )

            cv2.imshow(
                'Máscara refinada',
                refinada
            )

        else:

            if OPERACAO not in operacoes:

                raise ValueError(
                    f'Operação inválida: {OPERACAO}'
                )

            resultado = operacoes[OPERACAO]()

            cv2.imshow(
                'Imagem original',
                self.bgr
            )

            cv2.imshow(
                'Máscara original',
                self.mascara_original
            )

            cv2.imshow(
                f'Resultado: {OPERACAO}',
                resultado
            )

        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():

    processador = MelhorarMascara()

    processador.carregar_imagem(
        CAMINHO_IMAGEM
    )

    processador.executar()


if __name__ == '__main__':
    main()