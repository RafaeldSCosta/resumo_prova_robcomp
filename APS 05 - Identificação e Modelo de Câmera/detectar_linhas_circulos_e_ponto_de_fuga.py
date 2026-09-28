import math
import cv2
import numpy as np


CAMINHO_IMAGEM = 'imagem.jpg'


# Escolha o exemplo:
#
# 'linhas'
# 'circulos'
# 'ponto_de_fuga'
EXEMPLO = 'linhas'


# Parâmetros das linhas.
LIMIAR_HOUGH = 60
COMPRIMENTO_MINIMO = 50
ESPACO_MAXIMO = 20


class DetectarFormas:

    # ============================================================
    # LINHAS, CÍRCULOS E PONTO DE FUGA
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - encontrar linhas;
    # - detectar faixas ou bordas retas;
    # - encontrar círculos;
    # - encontrar o ponto onde duas linhas se cruzam;
    # - estimar o ponto de fuga de uma pista.
    #
    # Normalmente fazemos:
    #
    # imagem → cinza → blur → Canny → Hough

    def __init__(self):

        self.bgr = None
        self.cinza = None
        self.bordas = None

    def carregar_imagem(self, caminho):

        self.bgr = cv2.imread(caminho)

        if self.bgr is None:

            raise FileNotFoundError(
                f'Não foi possível abrir: {caminho}'
            )

        self.cinza = cv2.cvtColor(
            self.bgr,
            cv2.COLOR_BGR2GRAY
        )

    def encontrar_bordas(self):

        suavizada = cv2.GaussianBlur(
            self.cinza,
            (5, 5),
            0
        )

        self.bordas = cv2.Canny(
            suavizada,
            50,
            150
        )

        return self.bordas

    # ============================================================
    # DETECTAR LINHAS
    # ============================================================
    #
    # HoughLinesP devolve os pontos inicial e final:
    #
    # x1, y1, x2, y2
    #
    # Ajustes principais:
    #
    # LIMIAR_HOUGH:
    # quantidade mínima de votos.
    #
    # COMPRIMENTO_MINIMO:
    # tamanho mínimo aceito.
    #
    # ESPACO_MAXIMO:
    # distância máxima entre partes da mesma linha.

    def detectar_linhas(self):

        self.encontrar_bordas()

        linhas = cv2.HoughLinesP(
            self.bordas,
            rho=1,
            theta=np.pi / 180,
            threshold=LIMIAR_HOUGH,
            minLineLength=COMPRIMENTO_MINIMO,
            maxLineGap=ESPACO_MAXIMO
        )

        resultado = self.bgr.copy()

        quantidade = 0

        if linhas is not None:

            for linha in linhas:

                x1, y1, x2, y2 = linha[0]

                cv2.line(
                    resultado,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    3
                )

                quantidade += 1

        print(f'Linhas encontradas: {quantidade}')

        cv2.imshow('Bordas', self.bordas)
        cv2.imshow('Linhas', resultado)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # DETECTAR CÍRCULOS
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - encontrar círculos;
    # - marcar rodas, bolas ou padrões circulares;
    # - obter centro e raio.
    #
    # Os parâmetros do HoughCircles normalmente
    # precisam ser ajustados para cada imagem.

    def detectar_circulos(self):

        suavizada = cv2.GaussianBlur(
            self.cinza,
            (9, 9),
            2
        )

        circulos = cv2.HoughCircles(
            suavizada,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=30,
            param1=100,
            param2=30,
            minRadius=5,
            maxRadius=200
        )

        resultado = self.bgr.copy()

        quantidade = 0

        if circulos is not None:

            circulos = np.round(
                circulos[0]
            ).astype(int)

            for x, y, raio in circulos:

                # Desenha a circunferência.
                cv2.circle(
                    resultado,
                    (x, y),
                    raio,
                    (0, 255, 0),
                    3
                )

                # Desenha o centro.
                cv2.circle(
                    resultado,
                    (x, y),
                    5,
                    (0, 0, 255),
                    -1
                )

                quantidade += 1

        print(f'Círculos encontrados: {quantidade}')

        cv2.imshow('Círculos', resultado)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def calcular_inclinacao(self, linha):

        x1, y1, x2, y2 = linha

        # Linha vertical possui divisão por zero.
        if x2 == x1:
            return None

        return (y2 - y1) / (x2 - x1)

    def encontrar_intersecao(self, linha_1, linha_2):

        # Cada linha é formada por:
        #
        # x1, y1, x2, y2
        x1, y1, x2, y2 = linha_1
        x3, y3, x4, y4 = linha_2

        denominador = (
            (x1 - x2) * (y3 - y4)
            - (y1 - y2) * (x3 - x4)
        )

        # Denominador zero significa linhas paralelas.
        if abs(denominador) < 1e-6:
            return None

        determinante_1 = x1 * y2 - y1 * x2
        determinante_2 = x3 * y4 - y3 * x4

        x = (
            determinante_1 * (x3 - x4)
            - (x1 - x2) * determinante_2
        ) / denominador

        y = (
            determinante_1 * (y3 - y4)
            - (y1 - y2) * determinante_2
        ) / denominador

        return int(x), int(y)

    # ============================================================
    # ENCONTRAR PONTO DE FUGA
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - detectar a direção da pista;
    # - encontrar onde as linhas convergem;
    # - calcular o vanishing point.
    #
    # Este exemplo:
    #
    # 1. Detecta linhas.
    # 2. Separa linhas inclinadas para cada lado.
    # 3. Calcula as interseções.
    # 4. Usa a mediana das interseções como ponto de fuga.

    def detectar_ponto_de_fuga(self):

        self.encontrar_bordas()

        linhas_hough = cv2.HoughLinesP(
            self.bordas,
            rho=1,
            theta=np.pi / 180,
            threshold=LIMIAR_HOUGH,
            minLineLength=COMPRIMENTO_MINIMO,
            maxLineGap=ESPACO_MAXIMO
        )

        resultado = self.bgr.copy()

        if linhas_hough is None:

            print('Nenhuma linha encontrada')
            return

        linhas_esquerda = []
        linhas_direita = []

        for linha_hough in linhas_hough:

            linha = linha_hough[0]
            inclinacao = self.calcular_inclinacao(
                linha
            )

            if inclinacao is None:
                continue

            # Ignora linhas quase horizontais.
            if abs(inclinacao) < 0.3:
                continue

            if inclinacao < 0:
                linhas_esquerda.append(linha)

            else:
                linhas_direita.append(linha)

            x1, y1, x2, y2 = linha

            cv2.line(
                resultado,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                2
            )

        intersecoes = []

        for linha_esquerda in linhas_esquerda:

            for linha_direita in linhas_direita:

                ponto = self.encontrar_intersecao(
                    linha_esquerda,
                    linha_direita
                )

                if ponto is None:
                    continue

                x, y = ponto

                altura, largura = self.bgr.shape[:2]

                # Ignora pontos extremamente distantes.
                if (
                    -largura <= x <= 2 * largura
                    and -altura <= y <= 2 * altura
                ):
                    intersecoes.append(
                        (x, y)
                    )

        if len(intersecoes) == 0:

            print(
                'Não foi possível encontrar o ponto de fuga'
            )

        else:

            pontos = np.array(intersecoes)

            ponto_x = int(
                np.median(pontos[:, 0])
            )

            ponto_y = int(
                np.median(pontos[:, 1])
            )

            cv2.circle(
                resultado,
                (ponto_x, ponto_y),
                12,
                (0, 0, 255),
                -1
            )

            cv2.putText(
                resultado,
                f'Ponto de fuga: ({ponto_x}, {ponto_y})',
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

            print(
                f'Ponto de fuga: '
                f'({ponto_x}, {ponto_y})'
            )

        cv2.imshow('Bordas', self.bordas)
        cv2.imshow('Ponto de fuga', resultado)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def executar(self):

        exemplos = {
            'linhas': self.detectar_linhas,
            'circulos': self.detectar_circulos,
            'ponto_de_fuga':
                self.detectar_ponto_de_fuga
        }

        if EXEMPLO not in exemplos:

            raise ValueError(
                f'Exemplo inválido: {EXEMPLO}'
            )

        exemplos[EXEMPLO]()


def main():

    detector = DetectarFormas()

    detector.carregar_imagem(
        CAMINHO_IMAGEM
    )

    detector.executar()


if __name__ == '__main__':
    main()