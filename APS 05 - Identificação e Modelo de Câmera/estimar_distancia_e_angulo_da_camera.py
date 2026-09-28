import math
import cv2
import numpy as np


# Imagem usada para calibrar a câmera.
IMAGEM_CALIBRACAO = 'calib01.jpg'


# Imagem em que queremos estimar distância e ângulo.
IMAGEM_TESTE = 'angulo01.jpg'


# Distância conhecida entre a câmera e a folha
# na imagem de calibração.
#
# Use a mesma unidade em D e H.
DISTANCIA_CALIBRACAO = 0.80


# Distância real entre os centros dos círculos.
DISTANCIA_REAL_CIRCULOS = 0.127


class EstimarPose:

    # ============================================================
    # ESTIMAR DISTÂNCIA E ÂNGULO DA FOLHA
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - calcular a distância focal da câmera;
    # - estimar a distância até um objeto;
    # - usar o modelo pinhole;
    # - encontrar dois círculos coloridos;
    # - calcular a distância entre dois centros;
    # - calcular a inclinação da folha.
    #
    # FÓRMULAS:
    #
    # Encontrar distância focal:
    #
    # f = D × h / H
    #
    # Encontrar a distância até o objeto:
    #
    # D = f × H / h
    #
    # D:
    # distância real da câmera ao objeto.
    #
    # H:
    # distância real entre os círculos.
    #
    # h:
    # distância em pixels entre os círculos.
    #
    # f:
    # distância focal em pixels.

    def __init__(self):

        self.f = 0.0

        # Limites HSV do círculo ciano.
        self.ciano = {
            'lower': np.array([80, 80, 80]),
            'upper': np.array([100, 255, 255])
        }

        # Limites HSV do círculo magenta.
        self.magenta = {
            'lower': np.array([140, 80, 80]),
            'upper': np.array([175, 255, 255])
        }

        self.kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (5, 5)
        )

    # ============================================================
    # ENCONTRAR DISTÂNCIA FOCAL
    # ============================================================

    def encontrar_foco(self, D, H, h):

        if H <= 0 or h <= 0:
            return -1

        f = D * h / H

        return f

    def encontrar_maior_contorno(self, mascara):

        contornos, _ = cv2.findContours(
            mascara,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if len(contornos) == 0:
            return None

        return max(
            contornos,
            key=cv2.contourArea
        )

    def centro_do_contorno(self, contorno):

        if contorno is None:
            return None

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

    # ============================================================
    # ENCONTRAR OS DOIS CÍRCULOS
    # ============================================================
    #
    # USE QUANDO PRECISAR:
    #
    # - encontrar o centro do círculo ciano;
    # - encontrar o centro do círculo magenta;
    # - localizar marcadores coloridos.

    def encontrar_centros(self, bgr):

        hsv = cv2.cvtColor(
            bgr,
            cv2.COLOR_BGR2HSV
        )

        mascara_ciano = cv2.inRange(
            hsv,
            self.ciano['lower'],
            self.ciano['upper']
        )

        mascara_magenta = cv2.inRange(
            hsv,
            self.magenta['lower'],
            self.magenta['upper']
        )

        # Remove pequenas manchas.
        mascara_ciano = cv2.morphologyEx(
            mascara_ciano,
            cv2.MORPH_OPEN,
            self.kernel
        )

        mascara_magenta = cv2.morphologyEx(
            mascara_magenta,
            cv2.MORPH_OPEN,
            self.kernel
        )

        contorno_ciano = self.encontrar_maior_contorno(
            mascara_ciano
        )

        contorno_magenta = self.encontrar_maior_contorno(
            mascara_magenta
        )

        centro_ciano = self.centro_do_contorno(
            contorno_ciano
        )

        centro_magenta = self.centro_do_contorno(
            contorno_magenta
        )

        return centro_ciano, centro_magenta

    # ============================================================
    # CALCULAR DISTÂNCIA EM PIXELS
    # ============================================================

    def calcular_h(
        self,
        centro_ciano,
        centro_magenta
    ):

        if (
            centro_ciano is None
            or centro_magenta is None
        ):
            return -1

        x1, y1 = centro_ciano
        x2, y2 = centro_magenta

        distancia = math.sqrt(
            (x1 - x2) ** 2
            + (y1 - y2) ** 2
        )

        return distancia

    # ============================================================
    # ESTIMAR A DISTÂNCIA REAL
    # ============================================================

    def encontrar_D(self, f, H, h):

        if f <= 0 or H <= 0 or h <= 0:
            return -1

        D = f * H / h

        return D

    # ============================================================
    # CALCULAR O ÂNGULO COM A VERTICAL
    # ============================================================
    #
    # O vetor vai do círculo ciano até o magenta.
    #
    # atan2 permite descobrir o ângulo mantendo
    # o sinal e o quadrante correto.
    #
    # Se o sinal ficar contrário ao esperado na sua
    # imagem, troque a ordem dos centros.

    def calcular_theta(
        self,
        centro_ciano,
        centro_magenta
    ):

        if (
            centro_ciano is None
            or centro_magenta is None
        ):
            return -1

        x_ciano, y_ciano = centro_ciano
        x_magenta, y_magenta = centro_magenta

        diferenca_x = x_magenta - x_ciano
        diferenca_y = y_magenta - y_ciano

        # Ângulo em relação à vertical apontando para cima.
        angulo = math.degrees(
            math.atan2(
                diferenca_x,
                -diferenca_y
            )
        )

        return angulo

    def escrever_texto(
        self,
        bgr,
        distancia,
        angulo
    ):

        resultado = bgr.copy()

        cv2.putText(
            resultado,
            f'Distancia: {distancia:.2f} m',
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            resultado,
            f'Angulo: {angulo:.2f} graus',
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        return resultado

    # ============================================================
    # CALIBRAR A CÂMERA
    # ============================================================
    #
    # Na calibração, D e H são conhecidos.
    #
    # O programa mede h na imagem.
    #
    # Depois calcula:
    #
    # f = D × h / H

    def calibrar(self, bgr, D, H):

        centro_ciano, centro_magenta = (
            self.encontrar_centros(bgr)
        )

        h = self.calcular_h(
            centro_ciano,
            centro_magenta
        )

        if h <= 0:

            print(
                'Não foi possível encontrar os círculos'
            )

            return -1

        self.f = self.encontrar_foco(
            D,
            H,
            h
        )

        print(f'h da calibração: {h:.2f} px')
        print(f'Distância focal: {self.f:.2f} px')

        return self.f

    # ============================================================
    # PROCESSAR UMA IMAGEM
    # ============================================================

    def run(self, bgr):

        resultado = bgr.copy()

        centro_ciano, centro_magenta = (
            self.encontrar_centros(bgr)
        )

        # Se algum círculo não foi encontrado,
        # devolve -1 sem quebrar o programa.
        if (
            centro_ciano is None
            or centro_magenta is None
        ):

            cv2.putText(
                resultado,
                'Padrao nao encontrado',
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

            return resultado, -1, -1, -1

        h = self.calcular_h(
            centro_ciano,
            centro_magenta
        )

        angulo = self.calcular_theta(
            centro_ciano,
            centro_magenta
        )

        distancia = self.encontrar_D(
            self.f,
            DISTANCIA_REAL_CIRCULOS,
            h
        )

        # Desenha os centros.
        cv2.circle(
            resultado,
            centro_ciano,
            8,
            (255, 255, 0),
            -1
        )

        cv2.circle(
            resultado,
            centro_magenta,
            8,
            (255, 0, 255),
            -1
        )

        # Desenha a linha entre os círculos.
        cv2.line(
            resultado,
            centro_ciano,
            centro_magenta,
            (0, 255, 0),
            3
        )

        resultado = self.escrever_texto(
            resultado,
            distancia,
            angulo
        )

        return resultado, distancia, angulo, h


def rodar_imagem():

    estimador = EstimarPose()

    imagem_calibracao = cv2.imread(
        IMAGEM_CALIBRACAO
    )

    if imagem_calibracao is None:

        raise FileNotFoundError(
            f'Não foi possível abrir: '
            f'{IMAGEM_CALIBRACAO}'
        )

    # Primeiro calcula a distância focal.
    foco = estimador.calibrar(
        imagem_calibracao,
        DISTANCIA_CALIBRACAO,
        DISTANCIA_REAL_CIRCULOS
    )

    if foco <= 0:
        return

    imagem_teste = cv2.imread(
        IMAGEM_TESTE
    )

    if imagem_teste is None:

        raise FileNotFoundError(
            f'Não foi possível abrir: {IMAGEM_TESTE}'
        )

    resultado, distancia, angulo, h = (
        estimador.run(imagem_teste)
    )

    print(f'Distância estimada: {distancia:.2f} m')
    print(f'Ângulo estimado: {angulo:.2f} graus')
    print(f'Distância em pixels: {h:.2f} px')

    cv2.imshow(
        'Resultado',
        resultado
    )

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def rodar_webcam():

    estimador = EstimarPose()

    imagem_calibracao = cv2.imread(
        IMAGEM_CALIBRACAO
    )

    if imagem_calibracao is None:

        raise FileNotFoundError(
            f'Não foi possível abrir: '
            f'{IMAGEM_CALIBRACAO}'
        )

    foco = estimador.calibrar(
        imagem_calibracao,
        DISTANCIA_CALIBRACAO,
        DISTANCIA_REAL_CIRCULOS
    )

    if foco <= 0:
        return

    webcam = cv2.VideoCapture(0)

    if not webcam.isOpened():

        raise RuntimeError(
            'Não foi possível abrir a webcam'
        )

    try:

        while True:

            conseguiu_ler, frame = webcam.read()

            if not conseguiu_ler:
                break

            resultado, distancia, angulo, h = (
                estimador.run(frame)
            )

            cv2.imshow(
                'Estimativa de pose',
                resultado
            )

            tecla = cv2.waitKey(1) & 0xFF

            if tecla == 27 or tecla == ord('q'):
                break

    finally:

        webcam.release()
        cv2.destroyAllWindows()


def main():

    # Para testar com imagens:
    rodar_imagem()

    # Para executar com a webcam:
    # rodar_webcam()


if __name__ == '__main__':
    main()