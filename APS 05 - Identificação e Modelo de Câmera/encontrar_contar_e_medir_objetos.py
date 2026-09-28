import cv2
import numpy as np


CAMINHO_IMAGEM = 'imagem.jpg'


# Cor dos objetos que queremos encontrar.
COR = 'vermelho'


# Contornos menores que este valor serão ignorados.
#
# Aumente se estiver contando ruídos.
# Diminua se estiver ignorando objetos verdadeiros.
AREA_MINIMA = 500


class EncontrarObjetos:

    # ============================================================
    # ENCONTRAR, CONTAR E MEDIR OBJETOS
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - contar objetos;
    # - calcular a área de cada objeto;
    # - encontrar o maior objeto;
    # - encontrar o centro de um objeto;
    # - desenhar uma caixa ao redor do objeto;
    # - numerar os objetos encontrados;
    # - encontrar objetos usando uma máscara.
    #
    # ORDEM DO PROCESSAMENTO:
    #
    # 1. Ler a imagem.
    # 2. Converter para HSV.
    # 3. Criar a máscara.
    # 4. Melhorar a máscara.
    # 5. Encontrar os contornos.
    # 6. Filtrar pela área.
    # 7. Calcular medidas.
    # 8. Desenhar os resultados.

    def __init__(self):

        self.bgr = None
        self.hsv = None
        self.mascara = None

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

            self.mascara = cv2.bitwise_or(
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
                )
            }

            if COR not in limites:

                raise ValueError(
                    f'Cor inválida: {COR}'
                )

            limite_inferior, limite_superior = limites[COR]

            self.mascara = cv2.inRange(
                self.hsv,
                limite_inferior,
                limite_superior
            )

    def melhorar_mascara(self):

        # Remove pequenas manchas e fecha buracos.
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (5, 5)
        )

        self.mascara = cv2.morphologyEx(
            self.mascara,
            cv2.MORPH_OPEN,
            kernel
        )

        self.mascara = cv2.morphologyEx(
            self.mascara,
            cv2.MORPH_CLOSE,
            kernel
        )

    def encontrar_contornos(self):

        # RETR_EXTERNAL considera apenas os contornos externos.
        #
        # Isso ajuda a não contar buracos internos
        # como se fossem novos objetos.
        contornos, _ = cv2.findContours(
            self.mascara.copy(),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        return contornos

    def calcular_centro(self, contorno):

        # moments calcula informações do contorno.
        momentos = cv2.moments(contorno)

        # m00 corresponde à área.
        #
        # Se for zero, não podemos fazer a divisão.
        if momentos['m00'] == 0:
            return None

        centro_x = int(
            momentos['m10'] / momentos['m00']
        )

        centro_y = int(
            momentos['m01'] / momentos['m00']
        )

        return centro_x, centro_y

    def processar_objetos(self):

        self.criar_mascara()
        self.melhorar_mascara()

        contornos = self.encontrar_contornos()

        resultado = self.bgr.copy()

        # Guarda somente os contornos grandes o suficiente.
        objetos = []

        for contorno in contornos:

            area = cv2.contourArea(contorno)

            if area >= AREA_MINIMA:
                objetos.append(contorno)

        # Ordena do maior para o menor.
        objetos.sort(
            key=cv2.contourArea,
            reverse=True
        )

        quantidade = len(objetos)

        print(f'Quantidade de objetos: {quantidade}')

        maior_area = 0.0

        for indice, contorno in enumerate(
            objetos,
            start=1
        ):

            area = cv2.contourArea(contorno)
            perimetro = cv2.arcLength(
                contorno,
                True
            )

            if area > maior_area:
                maior_area = area

            # Menor retângulo que envolve o objeto.
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
                2
            )

            # Desenha a caixa delimitadora.
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
                    6,
                    (0, 0, 255),
                    -1
                )

            # Escreve número e área.
            cv2.putText(
                resultado,
                f'{indice}: area={area:.0f}',
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            print(
                f'Objeto {indice}: '
                f'área={area:.2f}, '
                f'perímetro={perimetro:.2f}, '
                f'caixa=({x}, {y}, {largura}, {altura}), '
                f'centro={centro}'
            )

        print(
            f'Área do maior objeto: {maior_area:.2f}'
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

        cv2.imshow(
            'Imagem original',
            self.bgr
        )

        cv2.imshow(
            'Máscara',
            self.mascara
        )

        cv2.imshow(
            'Objetos encontrados',
            resultado
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():

    processador = EncontrarObjetos()

    processador.carregar_imagem(
        CAMINHO_IMAGEM
    )

    processador.processar_objetos()


if __name__ == '__main__':
    main()