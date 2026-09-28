import cv2
import numpy as np


# Coloque aqui as imagens que serão testadas.
#
# Se tiver apenas uma imagem, deixe somente um caminho.
CAMINHOS_IMAGENS = [
    'latinhas1.jpg',
    'latinhas2.jpg',
    'latinhas3.jpg'
]


# Área mínima para considerar que um contorno
# representa uma latinha.
AREA_MINIMA = 1000


class IdentificarLatinhas:

    # ============================================================
    # IDENTIFICAR LATINHAS
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - identificar objetos vermelhos;
    # - identificar latinhas;
    # - contar objetos em uma imagem;
    # - encontrar contornos;
    # - calcular área e centro;
    # - marcar os objetos encontrados.
    #
    # COMO FUNCIONA:
    #
    # 1. Lê a imagem.
    # 2. Converte BGR para HSV.
    # 3. Segmenta as regiões vermelhas.
    # 4. Junta os dois intervalos do vermelho.
    # 5. Melhora a máscara.
    # 6. Encontra os contornos.
    # 7. Ignora contornos pequenos.
    # 8. Marca e conta as latinhas.

    def criar_mascara_vermelha(self, imagem):

        hsv = cv2.cvtColor(
            imagem,
            cv2.COLOR_BGR2HSV
        )

        # O vermelho aparece no começo e no final
        # do canal H no HSV do OpenCV.

        # Região próxima de H = 180.
        mascara_1 = cv2.inRange(
            hsv,
            np.array([172, 50, 50]),
            np.array([179, 255, 255])
        )

        # Região próxima de H = 0.
        mascara_2 = cv2.inRange(
            hsv,
            np.array([0, 50, 50]),
            np.array([8, 255, 255])
        )

        mascara = cv2.bitwise_or(
            mascara_1,
            mascara_2
        )

        return mascara

    def melhorar_mascara(self, mascara):

        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (5, 5)
        )

        # Remove pequenas manchas brancas.
        mascara = cv2.morphologyEx(
            mascara,
            cv2.MORPH_OPEN,
            kernel
        )

        # Preenche pequenos buracos.
        mascara = cv2.morphologyEx(
            mascara,
            cv2.MORPH_CLOSE,
            kernel
        )

        return mascara

    def calcular_centro(self, contorno):

        momentos = cv2.moments(contorno)

        if momentos['m00'] == 0:
            return None

        centro_x = int(
            momentos['m10'] / momentos['m00']
        )

        centro_y = int(
            momentos['m01'] / momentos['m00']
        )

        return centro_x, centro_y

    def processar_imagem(self, caminho):

        imagem = cv2.imread(caminho)

        if imagem is None:

            print(
                f'Imagem não encontrada: {caminho}'
            )

            return

        mascara = self.criar_mascara_vermelha(
            imagem
        )

        mascara = self.melhorar_mascara(
            mascara
        )

        contornos, _ = cv2.findContours(
            mascara.copy(),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        resultado = imagem.copy()

        latinhas = []

        # Filtra os contornos pela área.
        for contorno in contornos:

            area = cv2.contourArea(contorno)

            if area >= AREA_MINIMA:
                latinhas.append(contorno)

        # Organiza as latinhas da esquerda para a direita.
        latinhas.sort(
            key=lambda contorno:
                cv2.boundingRect(contorno)[0]
        )

        quantidade = len(latinhas)

        for numero, contorno in enumerate(
            latinhas,
            start=1
        ):

            area = cv2.contourArea(contorno)

            x, y, largura, altura = cv2.boundingRect(
                contorno
            )

            centro = self.calcular_centro(
                contorno
            )

            # Desenha o contorno.
            cv2.drawContours(
                resultado,
                [contorno],
                -1,
                (255, 0, 0),
                3
            )

            # Desenha a caixa da latinha.
            cv2.rectangle(
                resultado,
                (x, y),
                (x + largura, y + altura),
                (0, 255, 0),
                2
            )

            if centro is not None:

                centro_x, centro_y = centro

                cv2.circle(
                    resultado,
                    (centro_x, centro_y),
                    7,
                    (0, 255, 255),
                    -1
                )

            cv2.putText(
                resultado,
                f'Latinha {numero}',
                (x, max(y - 30, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            cv2.putText(
                resultado,
                f'Area: {area:.0f}',
                (x, max(y - 8, 40)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

            print(
                f'Latinha {numero}: '
                f'área={area:.2f}, '
                f'centro={centro}'
            )

        cv2.putText(
            resultado,
            f'Quantidade: {quantidade}',
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        print(
            f'{caminho}: '
            f'{quantidade} latinhas encontradas'
        )

        cv2.imshow(
            f'Original — {caminho}',
            imagem
        )

        cv2.imshow(
            f'Máscara — {caminho}',
            mascara
        )

        cv2.imshow(
            f'Latinhas — {caminho}',
            resultado
        )

        # Pressione uma tecla para ir para
        # a próxima imagem.
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def executar(self):

        for caminho in CAMINHOS_IMAGENS:

            self.processar_imagem(
                caminho
            )


def main():

    identificador = IdentificarLatinhas()

    identificador.executar()


if __name__ == '__main__':
    main()