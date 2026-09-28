import cv2
import numpy as np


CAMINHO_IMAGEM = 'imagem.jpg'


# Escolha o exemplo:
#
# 'blur'
# 'gaussiano'
# 'nitidez'
# 'sobel'
# 'canny'
# 'todos'
EXEMPLO = 'todos'


# Valores usados pelo Canny.
#
# Se aparecerem bordas demais, aumente.
# Se aparecerem poucas bordas, diminua.
CANNY_MINIMO = 50
CANNY_MAXIMO = 150


class FiltrosEBordas:

    # ============================================================
    # FILTROS E DETECÇÃO DE BORDAS
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - suavizar uma imagem;
    # - remover ruídos;
    # - aumentar a nitidez;
    # - aplicar um kernel;
    # - encontrar bordas;
    # - preparar uma imagem para detectar linhas;
    # - usar Blur, Sobel ou Canny.
    #
    # Um kernel é uma pequena matriz que passa
    # por toda a imagem fazendo uma operação.

    def __init__(self):

        self.bgr = None
        self.cinza = None

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

    # ============================================================
    # BLUR — FILTRO DA MÉDIA
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - suavizar a imagem;
    # - reduzir pequenos ruídos;
    # - borrar a imagem.
    #
    # Quanto maior o kernel, mais borrada fica a imagem.

    def aplicar_blur(self):

        kernel = np.ones(
            (5, 5),
            dtype=np.float32
        ) / 25

        resultado = cv2.filter2D(
            self.bgr,
            -1,
            kernel
        )

        return resultado

    # ============================================================
    # GAUSSIAN BLUR
    # ============================================================
    #
    # Também suaviza, mas dá mais importância
    # aos pixels próximos do centro.
    #
    # É bastante usado antes do Canny.

    def aplicar_gaussiano(self):

        resultado = cv2.GaussianBlur(
            self.bgr,
            (5, 5),
            0
        )

        return resultado

    # ============================================================
    # AUMENTAR A NITIDEZ
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - destacar detalhes;
    # - deixar as bordas mais fortes;
    # - aplicar um filtro de sharpening.

    def aumentar_nitidez(self):

        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])

        resultado = cv2.filter2D(
            self.bgr,
            -1,
            kernel
        )

        return resultado

    # ============================================================
    # SOBEL
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - encontrar mudanças de intensidade;
    # - destacar bordas verticais e horizontais;
    # - calcular gradiente da imagem.
    #
    # Sobel X destaca principalmente bordas verticais.
    # Sobel Y destaca principalmente bordas horizontais.

    def aplicar_sobel(self):

        sobel_x = cv2.Sobel(
            self.cinza,
            cv2.CV_64F,
            1,
            0,
            ksize=3
        )

        sobel_y = cv2.Sobel(
            self.cinza,
            cv2.CV_64F,
            0,
            1,
            ksize=3
        )

        sobel_x = cv2.convertScaleAbs(
            sobel_x
        )

        sobel_y = cv2.convertScaleAbs(
            sobel_y
        )

        combinado = cv2.addWeighted(
            sobel_x,
            0.5,
            sobel_y,
            0.5,
            0
        )

        return sobel_x, sobel_y, combinado

    # ============================================================
    # CANNY
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - encontrar bordas;
    # - preparar uma imagem para Hough Lines;
    # - detectar o contorno geral das formas.
    #
    # Primeiro aplicamos Gaussian Blur para reduzir ruídos.
    # Depois aplicamos Canny.

    def aplicar_canny(self):

        suavizada = cv2.GaussianBlur(
            self.cinza,
            (5, 5),
            0
        )

        bordas = cv2.Canny(
            suavizada,
            CANNY_MINIMO,
            CANNY_MAXIMO
        )

        return bordas

    def executar(self):

        if EXEMPLO == 'blur':

            cv2.imshow(
                'Blur',
                self.aplicar_blur()
            )

        elif EXEMPLO == 'gaussiano':

            cv2.imshow(
                'Gaussian Blur',
                self.aplicar_gaussiano()
            )

        elif EXEMPLO == 'nitidez':

            cv2.imshow(
                'Nitidez',
                self.aumentar_nitidez()
            )

        elif EXEMPLO == 'sobel':

            sobel_x, sobel_y, combinado = (
                self.aplicar_sobel()
            )

            cv2.imshow('Sobel X', sobel_x)
            cv2.imshow('Sobel Y', sobel_y)
            cv2.imshow('Sobel combinado', combinado)

        elif EXEMPLO == 'canny':

            cv2.imshow(
                'Bordas Canny',
                self.aplicar_canny()
            )

        elif EXEMPLO == 'todos':

            sobel_x, sobel_y, sobel = (
                self.aplicar_sobel()
            )

            cv2.imshow('Original', self.bgr)
            cv2.imshow('Blur', self.aplicar_blur())
            cv2.imshow(
                'Gaussian Blur',
                self.aplicar_gaussiano()
            )
            cv2.imshow(
                'Nitidez',
                self.aumentar_nitidez()
            )
            cv2.imshow('Sobel X', sobel_x)
            cv2.imshow('Sobel Y', sobel_y)
            cv2.imshow('Sobel combinado', sobel)
            cv2.imshow('Canny', self.aplicar_canny())

        else:

            raise ValueError(
                f'Exemplo inválido: {EXEMPLO}'
            )

        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():

    processador = FiltrosEBordas()

    processador.carregar_imagem(
        CAMINHO_IMAGEM
    )

    processador.executar()


if __name__ == '__main__':
    main()